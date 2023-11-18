import csv
import os

# Load the list of files from the input CSV
input_csv_file = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR 2024/Extracted_ML_files_Dataset/jax_ml_files.csv'  # Replace with the path to your input CSV file
input_files = set()
with open(input_csv_file, 'r') as input_csv:
    csv_reader = csv.reader(input_csv)
    next(csv_reader)  # Skip the header row if present
    for row in csv_reader:
        input_files.add(row[0])  # Assuming the file name is in the second column

# Load the list of all files in your project (you can use your previous code)
# Replace the code below with the logic to collect all files
# in the project excluding the ones in the input CSV

project_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR 2024/Dataset/jax-main'  # Specify your project directory
all_files = set()

# Example: Collect all files in your project
for root, dirs, files in os.walk(project_directory):
    for file in files:
        if file.endswith(".py"):  # Adjust the extension as needed
            all_files.add(file)

# Calculate the difference between all_files and input_files
files_to_exclude = input_files.intersection(all_files)
remaining_files = all_files - files_to_exclude

# Write the remaining files to a new CSV file
output_csv_file = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR 2024/Extracted_ML_files_Dataset/jax_nonml_files.csv'  # Specify the output CSV file
with open(output_csv_file, 'w', newline='') as output_csv:
    csv_writer = csv.writer(output_csv)
    csv_writer.writerow(['Non-ML File'])  # Header row
    for root, dirs, files in os.walk(project_directory):
        for file in files:
            if file in remaining_files:
                relative_path = os.path.relpath(root, project_directory)
                relative_path = relative_path + '/' + file
                csv_writer.writerow([relative_path])

