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
	##########################################################################################
	# calculating lcom
	#lcom = 0
	#with tempfile.TemporaryFile() as tempf:
	#    proc = subprocess.Popen(['lcom', relative_path], stdout=tempf)
	#    proc.wait()
	#    tempf.seek(0)
	#    output = tempf.read()

	#output = str(output)

	# Define a regular expression pattern to match the lcom value
	#pattern = r'\| Average \| (\d+\.\d+) \|'

	# Use re.search to find the value in the string
	#match = re.search(pattern, output)

	# Check if a match was found
	#if match:
	    # Extract the value from the matched group
	    #lcom = match.group(1)
	    # print("lcom:", lcom)
	#else:
	    #print("Value is not able to be extracted from terminal.")
	    #lcom = 0

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
	
	#########################################################################################
	#print('the number of distinct operators (h1): ', h1)
	#print('the number of distinct operands (h2): ', h2)
	#print('the total number of operators (N1): ', N1)
	#print('the total number of operands (N2): ', N2)
	#print('Program vocabulary (h): ', program_vocabulary)
	#print('length (N1+N2): ', program_length)
	#print('calculated length: ', calculated_length)
	#print('difficulty: ', difficulty)
	#print('effort: ', effort)
	#print('time: ', time)
	#print('halstead_volume: ', halstead_volume)
	#print('cyclomatic complexity: ', cyclomatic_complexity)
	#print('loc: ', loc)
	#print('lloc: ', lloc)
	#print('sloc: ', sloc)
	#print('maintainability index: ', maintainability_index)
	#########################################################################################
	
	
	# Find the starting index of name of the project_folder
	#main_index = relative_path.find(project_folder)
	#if main_index != -1:
		#relative_path = relative_path[main_index+1:]  # Exclude the path before the name of project_folder
	#relative_path = relative_path.replace('.', project_folder)
	#if not relative_path.startswith(project_folder):
		#relative_path = project_folder + '/' + relative_path        
        
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
#jax_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Jax_Versions/jax-jax-v0.1.73'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Jax_Versions/jax_0.1.73.csv'  # Change this to your desired output file path
#files_traversal(jax_directory, output_csv, 'jax_0.1.73')

#jax_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Jax_Versions/jax-jax-v0.2.21'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Jax_Versions/jax_0.2.21.csv'  # Change this to your desired output file path
#files_traversal(jax_directory, output_csv, 'jax_0.2.21')

#jax_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Jax_Versions/jax-jax-v0.2.28'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Jax_Versions/jax_0.2.28.csv'  # Change this to your desired output file path
#files_traversal(jax_directory, output_csv, 'jax_0.2.28')

#jax_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Jax_Versions/jax-jax-v0.3.15'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Jax_Versions/jax_0.3.15.csv'  # Change this to your desired output file path
#files_traversal(jax_directory, output_csv, 'jax_0.3.15')


#lightning_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Lightning_Versions/lightning-0.5.1'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Lightning_Versions/lightning_0.5.1.csv'  # Change this to your desired output file path
#files_traversal(lightning_directory, output_csv, 'lightning_0.5.1')

#lightning_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Lightning_Versions/lightning-1.0.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Lightning_Versions/lightning_1.0.0.csv'  # Change this to your desired output file path
#files_traversal(lightning_directory, output_csv, 'lightning_1.0.0')

#lightning_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Lightning_Versions/lightning-1.5.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Lightning_Versions/lightning_1.5.0.csv'  # Change this to your desired output file path
#files_traversal(lightning_directory, output_csv, 'lightning_1.5.0')

#lightning_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Lightning_Versions/lightning-1.8.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/Lightning_Versions/lightning_1.8.0.csv'  # Change this to your desired output file path
#files_traversal(lightning_directory, output_csv, 'lightning_1.8.0')

#yolov5_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/yolov5-master'
#output_csv = 'yolov5_files_metrics.csv'  # Change this to your desired output file path
#files_traversal(yolov5_directory, output_csv, 'yolov5')

#transformers_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/transformers_versions/transformers-2.0.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/transformers_versions/transformers_2.0.0.csv'  # Change this to your desired output file path
#files_traversal(transformers_directory, output_csv, 'transformers_2.0.0')

#transformers_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/transformers_versions/transformers-3.5.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/transformers_versions/transformers_3.5.0.csv'  # Change this to your desired output file path
#files_traversal(transformers_directory, output_csv, 'transformers_3.5.0')

#transformers_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/transformers_versions/transformers-4.13.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/transformers_versions/transformers_4.13.0.csv'  # Change this to your desired output file path
#files_traversal(transformers_directory, output_csv, 'transformers_4.13.0')

transformers_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/transformers_versions/transformers-4.23.0'
output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/transformers_versions/transformers_4.23.0.csv'  # Change this to your desired output file path
files_traversal(transformers_directory, output_csv, 'transformers_4.23.0')

#yolov5_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/yolov5-versions/yolov5-4.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/yolov5-versions/yolov5_4.0.csv'  # Change this to your desired output file path
#files_traversal(yolov5_directory, output_csv, 'yolov5_4.0')

#yolov5_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/yolov5-versions/yolov5-6.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/yolov5-versions/yolov5_6.0.csv'  # Change this to your desired output file path
#files_traversal(yolov5_directory, output_csv, 'yolov5_6.0')

#ray_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/ray_versions/ray-ray-0.3.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/ray_versions/ray_0.3.0.csv'  # Change this to your desired output file path
#files_traversal(ray_directory, output_csv, 'ray_0.3.0')

#ray_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/ray_versions/ray-ray-0.6.1'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/ray_versions/ray_0.6.1.csv'  # Change this to your desired output file path
#files_traversal(ray_directory, output_csv, 'ray_0.6.1')

#ray_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/ray_versions/ray-ray-0.8.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/ray_versions/ray_0.8.0.csv'  # Change this to your desired output file path
#files_traversal(ray_directory, output_csv, 'ray_0.8.0')

#ray_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/ray_versions/ray-ray-1.1.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/ray_versions/ray_1.1.0.csv'  # Change this to your desired output file path
#files_traversal(ray_directory, output_csv, 'ray_1.1.0')

#ray_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/ray_versions/ray-ray-1.9.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/ray_versions/ray_1.9.0.csv'  # Change this to your desired output file path
#files_traversal(ray_directory, output_csv, 'ray_1.9.0')

#ray_directory = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/ray_versions/ray-ray-2.0.0'
#output_csv = '/home/user/CS21D002_A_Eashaan_Rao/Research/CPDP/MSR_2024/Dataset/ray_versions/ray_2.0.0.csv'  # Change this to your desired output file path
#files_traversal(ray_directory, output_csv, 'ray_2.0.0')
