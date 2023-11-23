import os
import csv

def count_ml_files(directory, keywords, output_csv, project_folder):
    ml_file_count = 0
    total_py_file_count = 0
    total_files = 0 
    processed_files = set()
    project_root = os.path.abspath(directory)  # Get the absolute path of the project root
    with open(output_csv, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['ML Files'])

    for root, dirs, files in os.walk(directory):
        for file in files:
            total_files += 1
            if file.endswith(".py"):  # Adjust the extension as needed
            	total_py_file_count +=1
            	with open(os.path.join(root, file), 'r', errors='ignore') as f:
                    content = f.read()
                    #if any(keyword in content for keyword in keywords):
                    if file not in processed_files and any(keyword in content for keyword in keywords):
                        ml_file_count += 1
                        processed_files.add(file)
                        
                        # Calculate the relative path from 'jax-main' and save it to the CSV
                        relative_path = os.path.relpath(root, project_root)
                               
                        # Save project folder path and processed file to the CSV
                        with open(output_csv, mode='a', newline='') as csv_file:
                            csv_writer = csv.writer(csv_file)
                            relative_path = relative_path + '/' + file
                            csv_writer.writerow([relative_path])
    
    print("Total Files: ", total_files)
    print("Total Python Files: ", total_py_file_count)
    return ml_file_count

#project_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR 2024/Dataset/ray-master'





jax_directory = '../Dataset/ML Projects/Jax_Versions/jax-jax-v0.3.15'
jax_libraries = ['ml_dtypes', 'numpy', 'opt_einsum', 'scipy', 'jax', 'scikit-learn', 'matplotlib'] # Add your ML-related keywords to this list for jax
output_csv = 'jax_ml_files.csv'  # Change this to your desired output file path
ml_count = count_ml_files(jax_directory, jax_libraries, output_csv, 'jax-main')
print(f"Number of ML-related files in Jax: {ml_count}")
print(f"Processed files saved to {output_csv}")

ray_directory = '../Dataset/ML Projects/ray_versions/ray-ray-2.0.0'
ray_libraries = ['numpy', 'scipy', 'gymnasium', 'scikit-learn', 'scikit-image', 'pandas', 'tensorboardX'] # Add your ML-related keywords to this list for ray
output_csv = 'ray_ml_files.csv'  # Change this to your desired output file path
ml_count = count_ml_files(ray_directory, ray_libraries, output_csv, 'ray-master')
print(f"Number of ML-related files in Ray: {ml_count}")
print(f"Processed files saved to {output_csv}")

lightning_directory = '../Dataset/ML Projects/Lightning_Versions/lightning-1.8.0'
lightning_libraries = ['torch', 'numpy', 'torchmetrics', 'gym', 'matplotlib', 'tensorboardX', 'scikit-learn', 'tensorboard', 'pytorch-lightning', 'torchdata', 'torchvision', 'torchmetrics', 'lightning-colossalai', 'neptune', 'comet-ml', 'mlflow', 'onnx' ] # Add your ML-related keywords to this list for lightning
output_csv = 'lightning_ml_files.csv'  # Change this to your desired output file path
ml_count = count_ml_files(lightning_directory, lightning_libraries, output_csv, 'lightning-master')
print(f"Number of ML-related files in lightning: {ml_count}")
print(f"Processed files saved to {output_csv}")

yolov5_directory = '../Dataset/ML Projects/yolov5-versions/yolov5-7.0'
yolov5_libraries = ['numpy', 'scipy', 'matplotlib', 'opencv-python', 'opencv', 'torch', 'torchvision', 'ultralytics', 'tensorboard', 'clearml', 'comet', 'coremltools', 'onnx', 'onnx-simplifier', 'scikit-learn', 'tensorflow', 'tensorflowjs', 'openvino-dev' ] # Add your ML-related keywords to this list for yolov5
output_csv = 'yolov5_ml_files.csv'  # Change this to your desired output file path
ml_count = count_ml_files(yolov5_directory, yolov5_libraries, output_csv, 'yolov5-master')
print(f"Number of ML-related files in yolov5: {ml_count}")
print(f"Processed files saved to {output_csv}")

transformers_directory = '../Dataset/ML Projects/transformers_versions/transformers-4.23.0'
transformers_libraries = ['deepspeed', 'diffusers', 'evaluate', 'flax', 'huggingface-hub', 'jax', 'jaxlib', 'jieba', 'keras', 'keras-nlp', 'nltk', 'numpy', 'onnxconverter-common', 'onnxruntime-tools', 'onnxruntime', 'opencv-python', 'optuna', 'safetensors', 'sagemaker', 'scikit-learn', 'sentencepiece', 'sigopt', 'tensorboard', 'tensorflow', 'torch', 'torchaudio', 'torchvision' ] # Add your ML-related keywords to this list for transformers
output_csv = 'transformers_ml_files.csv'  # Change this to your desired output file path
ml_count = count_ml_files(transformers_directory, transformers_libraries, output_csv, 'transformers-main')
print(f"Number of ML-related files in transfomers: {ml_count}")
print(f"Processed files saved to {output_csv}")


