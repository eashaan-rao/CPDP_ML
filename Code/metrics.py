import os
import csv
import subprocess
import tempfile
import re
import radon
from tqdm import tqdm
from radon.visitors import ComplexityVisitor
from radon.visitors import HalsteadVisitor
from radon.complexity import cc_rank, cc_visit
from radon.raw import analyze
from radon.metrics import h_visit, mi_visit, mi_parameters
import warnings
warnings.filterwarnings("ignore")

  
def calculate_metrics(content, file, relative_path, project_folder, output_csv):
	relative_path = relative_path + '/' + file
	#print(relative_path)

	#######################################################################################
	# calculating halstead, cyclomatic complexity, maintainability index and basic metrics
	halstead_metric = h_visit(content)
	maintainability_index = mi_visit(content, multi=True)
	parameters = mi_parameters(content)
	basic_metrics = analyze(content)
	
	h1 = halstead_metric[0].h1
	h2 = halstead_metric[0].h2
	N1 = halstead_metric[0].N1
	N2 = halstead_metric[0].N2
	program_vocabulary = halstead_metric[0].vocabulary
	program_length = halstead_metric[0].length
	calculated_length = halstead_metric[0].calculated_length
	difficulty = halstead_metric[0].difficulty
	effort = halstead_metric[0].effort
	time = halstead_metric[0].time
	halstead_volume =  parameters[0]
	cyclomatic_complexity = parameters[1]
	loc = basic_metrics.loc
	lloc = basic_metrics.lloc
	sloc = basic_metrics.sloc
        
	# Save project folder path, processed file and its related calculated metrics to the CSV
	with open(output_csv, mode='a', newline='') as csv_file:
		csv_writer = csv.writer(csv_file)
		csv_writer.writerow([project_folder, relative_path, loc, lloc, sloc, h1, h2, N1, N2, program_vocabulary, program_length, calculated_length, difficulty, effort, time, halstead_volume, cyclomatic_complexity, maintainability_index])
	

	
###############################################################################################

# iterating over each python file and for each file calling calculate_metrics() 
def files_traversal(directory, output_csv, project_folder):
	#processed_files = set()
	project_root = os.path.abspath(directory)  # Get the absolute path of the project root
	
	# opening a csv file where all metrics data for each file will be stored
	with open(output_csv, mode='w', newline='') as csv_file:
		csv_writer = csv.writer(csv_file)
		csv_writer.writerow(['Project', 'Files', 'LOC', 'LLOC', 'SLOC', 'h1', 'h2', 'N1', 'N2', 'N', 'Length', 'Calculated_length', 'Difficulty', 'Effort', 'Time', 'Halstead_Volume', 'Cyclomatic_Complexity', 'Maintainabilty_Index'])
	
	# walking through each file, subfolders and folders	
	for root, dirs, files in tqdm(os.walk(directory)):
		if project_folder == 'transformers_4.23.0' and 'templates' in dirs:
        	# If the "templates" directory is in the list of subdirectories, remove it to skip processing
        		dirs.remove('templates')
		for file in files:
			if file.endswith(".py"):  # Adjust the extension as needed
				with open(os.path.join(root, file), 'r', errors='ignore') as f:
					content = f.read() # reading the content of file
					
					#if file not in processed_files:
						#processed_files.add(file)
						#print(file)
					# Calculate the relative path of the project_folder
					relative_path = os.path.relpath(root, project_root)
					# Calculating metrics for each file
					calculate_metrics(content, file, relative_path, project_folder, output_csv)
		        
    
################################################################################################

# Define the path to your Python project directory


transformers_directory = '../Dataset/ML Projects/transformers_versions/transformers-4.23.0'
output_csv = '../transformers_4_23_0.csv'  # Change this to your desired output file path
files_traversal(transformers_directory, output_csv, 'transformers_4.23.0')


