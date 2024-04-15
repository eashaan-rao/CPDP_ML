import os


count = 0
for root_dir, cur_dir, files in os.walk(r'../Dataset/ML Projects/folder_name'):
    count += len(files)
print('Total file count:', count)


