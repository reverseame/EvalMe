#!/usr/bin/python3
'''
@Authors:
	Razvan Raducu
	Ricardo J Rodriguez
	Pedro Álvarez

Script used to automate the process of benchmarking several binaries using EvalMe.py	
'''
import argparse
import os
import hashlib
import subprocess
import sys
import json

plaintext_folder = "Plaintext"
bash_script_name = "script.sh"
eval_me = "./evalme.py"
key_lengths = [128, 192, 256]
operation_modes = ['cbc', 'ofb', 'ctr', 'cfb']

def parse_arguments():
	parser = argparse.ArgumentParser(description="Benchmarking cipher/decipher binaries with EvalMe")
	parser.add_argument("input_directory", help="Input directory. The directory must contain a folder called \"Plaintext\", where original files are. Additionally, a folder for each cipher algorithm should be created.")
	parser.add_argument("output", help="Output json file. (json extension will be added automatically)")
	parser.add_argument("-r", "--runs", action="store", type=int, help="(Default = 10) Perform exactly RUNS runs for each command.", default=10)
	arguments = parser.parse_args()

	return arguments

def get_md5_of_file(filename):
	# We read the file 4K at a time, since loading the whole file at once in memory may file for very large inputs
	md5_hash = hashlib.md5()
	with open(filename, 'rb') as file:
	    # Read and update hash in chunks of 4K
	    for byte_block in iter(lambda: file.read(4096), b""):
	        md5_hash.update(byte_block)
	    return md5_hash.hexdigest()

def get_absolute_path(filename):
	return os.path.abspath(filename)

def encryption(bash_script, input_file, output_file, mode, key_length):
	bash = "{} -e {} {} -m {} -k {}".format(bash_script, input_file, output_file, mode, key_length)

	arguments_array = [eval_me, bash, '--json', "-r {}".format(arguments.runs)]

	popen = subprocess.run(arguments_array, capture_output=True) 
	# Check errors
	if popen.returncode:
		print("[!] ** THERE WAS AN ERROR:\n{}".format(popen.stderr.decode()))
		print("[!] ABORTING [!]")
		sys.exit(-1)

	json_results = json.loads(popen.stdout.decode())

	json_data['results'][algorithm][file][mode][key_length]['encrypt'] = {
		'cpu':json_results['results']['cpu']['mean'],
		'mem':json_results['results']['memory']['real']['mean'],
		'vmem':json_results['results']['memory']['virtual']['mean']
	}



def decryption(bash_script, input_file, output_file, mode, key_length):
	bash = "{} -d {} {} -m {} -k {}".format(bash_script, input_file, output_file, mode, key_length)

	arguments_array = [eval_me, bash, '--json', "-r {}".format(arguments.runs)]

	popen = subprocess.run(arguments_array, capture_output=True) 
	# Check errors
	if popen.returncode:
		print("[!] ** THERE WAS AN ERROR:\n{}".format(popen.stderr.decode()))
		print("[!] ABORTING [!]")
		sys.exit(-1)

	json_results = json.loads(popen.stdout.decode())

	json_data['results'][algorithm][file][mode][key_length]['decrypt'] = {
		'cpu':json_results['results']['cpu']['mean'],
		'mem':json_results['results']['memory']['real']['mean'],
		'vmem':json_results['results']['memory']['virtual']['mean']
	}


if __name__ == '__main__':
	arguments = parse_arguments()

	plaintext_files = []
	plaintext_files_md5 = {}
	
	# Retrieving plaintext files
	for (path, dirs, files) in os.walk(os.path.join(arguments.input_directory, plaintext_folder)):
		for file in files:
			plaintext_files.append(file)

	# Computing MD5 of plaintext files
	for file in plaintext_files:
		file_path = os.path.join(path, file)
		plaintext_files_md5[file] = (file_path, get_md5_of_file(file_path))

	json_data = {}
	json_data['results'] = {}

	for (path, dirs, files) in os.walk(arguments.input_directory):

		# We perform ciphering, deciphering and results gather for every subdirectory except the directory itself and the one containing original plaintexts
		if path != os.path.join(arguments.input_directory, plaintext_folder) and path != arguments.input_directory:
			# Ciphering / deciphering and results gathering should happen here. Overhead must be also taken into account
			# Ciphering (pseudocode): 
			bash_script_abspath = get_absolute_path(os.path.join(path, bash_script_name))
			algorithm = path.split("/")[-1]
			json_data['results'][algorithm] = {}

			for file, description in plaintext_files_md5.items():
				'''
				file: plaintext file name
				description[0]: plaintext full path
				description[1]: md5
				'''	
				json_data['results'][algorithm][file] = {}

				for mode in operation_modes:

					json_data['results'][algorithm][file][mode] = {}

					for key_length in key_lengths:

						json_data['results'][algorithm][file][mode][key_length] = {}

						################################################# ENCRYPTION #######################################################
						input_file_abspath = get_absolute_path(description[0])
						output_file_abspath = get_absolute_path(os.path.join(path, file)) + ".enc"
						
						encryption(bash_script_abspath,
							input_file_abspath,
							output_file_abspath,
							mode,
							key_length)
						##################################################################################################################


						################################################ DECRYPTION #####################################################
						input_file_abspath = output_file_abspath
						output_file_abspath = get_absolute_path(os.path.join(path, file))

						decryption(bash_script_abspath,
							input_file_abspath,
							output_file_abspath,
							mode,
							key_length)
						##################################################################################################################


						################################################ MD5 CHECKING #####################################################
					
						deciphered_md5 = get_md5_of_file(output_file_abspath)
						if deciphered_md5 != description[1]:
							print("[!] ERROR. MD5 of deciphered file (1) is not equal to the original plaintext (2) [!]\n[!] 1: {} [!]\n[!] 2: {} [!]".format(deciphered_md5, description[1]))
							print("[!] ABORTING [!]")
							sys.exit(-1)
						
						##################################################################################################################

	with open(arguments.output+".json", "w") as file:
		json.dump(json_data, file)
	
				
