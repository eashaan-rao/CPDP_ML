import os

# folder path
#dir_path = r'/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR 2024/Dataset/jax-main'
#count = 0
# Iterate directory
#for path in os.listdir(dir_path):
    # check if current path is a file
#    if os.path.isfile(os.path.join(dir_path, path)):
#        count += 1
#print('Total File count:', count)



count = 0
for root_dir, cur_dir, files in os.walk(r'/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR 2024/Dataset/ray-master'):
    count += len(files)
print('Total file count:', count)


