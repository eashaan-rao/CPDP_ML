# Copyright 2020 The JAX Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script that builds a jaxlib wheel, intended to be run via bazel run as part
# of the jaxlib build process.

# Most users should not run this script directly; use build.py instead.

import argparse
import functools
import os
import pathlib
import platform
import re
import subprocess
import tempfile

from bazel_tools.tools.python.runfiles import runfiles
from jax.tools import build_utils

parser = argparse.ArgumentParser()
parser.add_argument(
    "--sources_path",
    default=None,
    help="Path in which the wheel's sources should be prepared. Optional. If "
    "omitted, a temporary directory will be used.",
)
parser.add_argument(
    "--output_path",
    default=None,
    required=True,
    help="Path to which the output wheel should be written. Required.",
)
parser.add_argument(
    "--cpu", default=None, required=True, help="Target CPU architecture. Required."
)
parser.add_argument(
    "--editable",
    action="store_true",
    help="Create an 'editable' jaxlib build instead of a wheel.",
)
parser.add_argument(
    "--include_gpu_plugin_extension",
    # args.include_gpu_plugin_extension is True when
    # --include_gpu_plugin_extension is in the command
    action="store_true",
    help="Whether to include gpu plugin extension.",
)
args = parser.parse_args()

r = runfiles.Create()


def _is_mac():
  return platform.system() == "Darwin"


pyext = "pyd" if build_utils.is_windows() else "so"


def exists(src_file):
  return r.Rlocation(src_file) is not None


def patch_copy_mlir_import(src_file, dst_dir):
  src_file = r.Rlocation(src_file)
  src_filename = os.path.basename(src_file)
  with open(src_file) as f:
    src = f.read()

  with open(dst_dir / src_filename, "w") as f:
    replaced = re.sub(
        r"^from mlir(\..*)? import (.*)",
        r"from jaxlib.mlir\1 import \2",
        src,
        flags=re.MULTILINE,
    )
    f.write(replaced)


_XLA_EXTENSION_STUBS = [
    "__init__.pyi",
    "jax_jit.pyi",
    "ops.pyi",
    "outfeed_receiver.pyi",
    "pmap_lib.pyi",
    "profiler.pyi",
    "pytree.pyi",
    "transfer_guard_lib.pyi",
]
_OPTIONAL_XLA_EXTENSION_STUBS = []


def patch_copy_xla_extension_stubs(dst_dir):
  xla_extension_dir = os.path.join(dst_dir, "xla_extension")
  os.makedirs(xla_extension_dir)
  for stub_name in _XLA_EXTENSION_STUBS:
    stub_path = r.Rlocation("xla/xla/python/xla_extension/" + stub_name)
    stub_path = str(stub_path)  # Make pytype accept os.path.exists(stub_path).
    if stub_name in _OPTIONAL_XLA_EXTENSION_STUBS and not os.path.exists(stub_path):
      continue
    with open(stub_path) as f:
      src = f.read()
    src = src.replace(
        "from xla.python import xla_extension", "from .. import xla_extension"
    )
    with open(os.path.join(xla_extension_dir, stub_name), "w") as f:
      f.write(src)


def verify_mac_libraries_dont_reference_chkstack():
  """Verifies that xla_extension.so doesn't depend on ____chkstk_darwin.

  We don't entirely know why this happens, but in some build environments
  we seem to target the wrong Mac OS version.
  https://github.com/google/jax/issues/3867

  This check makes sure we don't release wheels that have this dependency.
  """
  if not _is_mac():
    return
  nm = subprocess.run(
      ["nm", "-g", r.Rlocation("xla/xla/python/xla_extension.so")],
      capture_output=True,
      text=True,
      check=False,
  )
  if nm.returncode != 0:
    raise RuntimeError(f"nm process failed: {nm.stdout} {nm.stderr}")
  if "____chkstk_darwin" in nm.stdout:
    raise RuntimeError(
        "Mac wheel incorrectly depends on symbol ____chkstk_darwin, which "
        "means that it isn't compatible with older MacOS versions."
    )


def write_setup_cfg(sources_path, cpu):
  tag = build_utils.platform_tag(cpu)
  with open(sources_path / "setup.cfg", "w") as f:
    f.write(
        f"""[metadata]
license_files = LICENSE.txt

[bdist_wheel]
plat-name={tag}
"""
    )


def prepare_wheel(sources_path: pathlib.Path, *, cpu, include_gpu_plugin_extension):
  """Assembles a source tree for the wheel in `sources_path`."""
  copy_runfiles = functools.partial(build_utils.copy_file, runfiles=r)

  verify_mac_libraries_dont_reference_chkstack()
  copy_runfiles(
      dst_dir=sources_path,
      src_files=[
          "__main__/jaxlib/tools/LICENSE.txt",
          "__main__/jaxlib/README.md",
          "__main__/jaxlib/setup.py",
      ],
  )
  write_setup_cfg(sources_path, cpu)

  jaxlib_dir = sources_path / "jaxlib"
  copy_runfiles(
      "__main__/jaxlib/init.py", dst_dir=jaxlib_dir, dst_filename="__init__.py"
  )
  if include_gpu_plugin_extension:
    copy_runfiles(
        dst_dir=jaxlib_dir, src_files=[f"__main__/jaxlib/cuda_plugin_extension.{pyext}"]
    )
  copy_runfiles(
      dst_dir=jaxlib_dir,
      src_files=[
          f"__main__/jaxlib/cpu_feature_guard.{pyext}",
          f"__main__/jaxlib/utils.{pyext}",
          "__main__/jaxlib/lapack.py",
          "__main__/jaxlib/hlo_helpers.py",
          "__main__/jaxlib/ducc_fft.py",
          "__main__/jaxlib/gpu_prng.py",
          "__main__/jaxlib/gpu_linalg.py",
          "__main__/jaxlib/gpu_rnn.py",
          "__main__/jaxlib/gpu_triton.py",
          "__main__/jaxlib/gpu_common_utils.py",
          "__main__/jaxlib/gpu_solver.py",
          "__main__/jaxlib/gpu_sparse.py",
          "__main__/jaxlib/tpu_mosaic.py",
          "__main__/jaxlib/version.py",
          "__main__/jaxlib/xla_client.py",
          f"__main__/jaxlib/xla_extension.{pyext}",
      ],
  )
  # This file is required by PEP-561. It marks jaxlib as package containing
  # type stubs.
  with open(jaxlib_dir / "py.typed", "w"):
    pass
  patch_copy_xla_extension_stubs(jaxlib_dir)

  copy_runfiles(
      dst_dir=jaxlib_dir / "cpu",
      src_files=[
          f"__main__/jaxlib/cpu/_lapack.{pyext}",
          f"__main__/jaxlib/cpu/_ducc_fft.{pyext}",
      ],
  )

  if exists(f"__main__/jaxlib/cuda/_solver.{pyext}"):
    copy_runfiles(
        dst_dir=jaxlib_dir / "cuda" / "nvvm" / "libdevice",
        src_files=["local_config_cuda/cuda/cuda/nvvm/libdevice/libdevice.10.bc"],
    )
    copy_runfiles(
        dst_dir=jaxlib_dir / "cuda",
        src_files=[
            f"__main__/jaxlib/cuda/_solver.{pyext}",
            f"__main__/jaxlib/cuda/_blas.{pyext}",
            f"__main__/jaxlib/cuda/_linalg.{pyext}",
            f"__main__/jaxlib/cuda/_prng.{pyext}",
            f"__main__/jaxlib/cuda/_rnn.{pyext}",
            f"__main__/jaxlib/cuda/_sparse.{pyext}",
            f"__main__/jaxlib/cuda/_triton.{pyext}",
            f"__main__/jaxlib/cuda/_versions.{pyext}",
        ],
    )
  if exists(f"__main__/jaxlib/rocm/_solver.{pyext}"):
    copy_runfiles(
        dst_dir=jaxlib_dir / "rocm",
        src_files=[
            f"__main__/jaxlib/rocm/_solver.{pyext}",
            f"__main__/jaxlib/rocm/_blas.{pyext}",
            f"__main__/jaxlib/rocm/_linalg.{pyext}",
            f"__main__/jaxlib/rocm/_prng.{pyext}",
            f"__main__/jaxlib/rocm/_sparse.{pyext}",
            f"__main__/jaxlib/rocm/_triton.{pyext}",
        ],
    )

  mosaic_python_dir = jaxlib_dir / "mosaic" / "python"
  copy_runfiles(
      dst_dir=mosaic_python_dir,
      src_files=[
          "__main__/jaxlib/mosaic/python/apply_vector_layout.py",
          "__main__/jaxlib/mosaic/python/infer_memref_layout.py",
          "__main__/jaxlib/mosaic/python/tpu.py",
      ],
  )
  # TODO (sharadmv,skyewm): can we avoid patching this file?
  patch_copy_mlir_import(
      "__main__/jaxlib/mosaic/python/_tpu_gen.py", dst_dir=mosaic_python_dir
  )

  copy_runfiles(
      dst_dir=jaxlib_dir / "mlir",
      src_files=[
          "__main__/jaxlib/mlir/ir.py",
          "__main__/jaxlib/mlir/passmanager.py",
      ],
  )
  copy_runfiles(
      dst_dir=jaxlib_dir / "mlir" / "dialects",
      src_files=[
          "__main__/jaxlib/mlir/dialects/_arith_enum_gen.py",
          "__main__/jaxlib/mlir/dialects/_arith_ops_gen.py",
          "__main__/jaxlib/mlir/dialects/_builtin_ops_gen.py",
          "__main__/jaxlib/mlir/dialects/_chlo_ops_gen.py",
          "__main__/jaxlib/mlir/dialects/_func_ops_gen.py",
          "__main__/jaxlib/mlir/dialects/_math_ops_gen.py",
          "__main__/jaxlib/mlir/dialects/_memref_ops_gen.py",
          "__main__/jaxlib/mlir/dialects/_mhlo_ops_gen.py",
          "__main__/jaxlib/mlir/dialects/_ml_program_ops_gen.py",
          "__main__/jaxlib/mlir/dialects/_ods_common.py",
          "__main__/jaxlib/mlir/dialects/_scf_ops_gen.py",
          "__main__/jaxlib/mlir/dialects/_sparse_tensor_enum_gen.py",
          "__main__/jaxlib/mlir/dialects/_sparse_tensor_ops_gen.py",
          "__main__/jaxlib/mlir/dialects/_stablehlo_ops_gen.py",
          "__main__/jaxlib/mlir/dialects/_vector_enum_gen.py",
          "__main__/jaxlib/mlir/dialects/_vector_ops_gen.py",
          "__main__/jaxlib/mlir/dialects/arith.py",
          "__main__/jaxlib/mlir/dialects/builtin.py",
          "__main__/jaxlib/mlir/dialects/chlo.py",
          "__main__/jaxlib/mlir/dialects/func.py",
          "__main__/jaxlib/mlir/dialects/math.py",
          "__main__/jaxlib/mlir/dialects/memref.py",
          "__main__/jaxlib/mlir/dialects/mhlo.py",
          "__main__/jaxlib/mlir/dialects/ml_program.py",
          "__main__/jaxlib/mlir/dialects/scf.py",
          "__main__/jaxlib/mlir/dialects/sparse_tensor.py",
          "__main__/jaxlib/mlir/dialects/stablehlo.py",
          "__main__/jaxlib/mlir/dialects/vector.py",
      ],
  )

  if build_utils.is_windows():
    capi_so = "__main__/jaxlib/mlir/_mlir_libs/jaxlib_mlir_capi.dll"
  else:
    so_ext = "dylib" if _is_mac() else "so"
    capi_so = f"__main__/jaxlib/mlir/_mlir_libs/libjaxlib_mlir_capi.{so_ext}"

  mlir_libs_dir = jaxlib_dir / "mlir" / "_mlir_libs"
  copy_runfiles(
      dst_dir=mlir_libs_dir,
      src_files=[
          capi_so,
          "__main__/jaxlib/mlir/_mlir_libs/__init__.py",
          f"__main__/jaxlib/mlir/_mlir_libs/_mlir.{pyext}",
          f"__main__/jaxlib/mlir/_mlir_libs/_chlo.{pyext}",
          f"__main__/jaxlib/mlir/_mlir_libs/_mlirHlo.{pyext}",
          f"__main__/jaxlib/mlir/_mlir_libs/_mlirDialectsSparseTensor.{pyext}",
          f"__main__/jaxlib/mlir/_mlir_libs/_mlirSparseTensorPasses.{pyext}",
          f"__main__/jaxlib/mlir/_mlir_libs/_tpu_ext.{pyext}",
          f"__main__/jaxlib/mlir/_mlir_libs/_stablehlo.{pyext}",
          f"__main__/jaxlib/mlir/_mlir_libs/_site_initialize_0.{pyext}",
      ],
  )


tmpdir = None
sources_path = args.sources_path
if sources_path is None:
  tmpdir = tempfile.TemporaryDirectory(prefix="jaxlib")
  sources_path = tmpdir.name

try:
  os.makedirs(args.output_path, exist_ok=True)
  prepare_wheel(
      pathlib.Path(sources_path),
      cpu=args.cpu,
      include_gpu_plugin_extension=args.include_gpu_plugin_extension,
  )
  package_name = "jaxlib"
  if args.editable:
    build_utils.build_editable(sources_path, args.output_path, package_name)
  else:
    build_utils.build_wheel(sources_path, args.output_path, package_name)
finally:
  if tmpdir:
    tmpdir.cleanup()
