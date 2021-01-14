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

plaintext_folder = "Plaintext"
bash_script = "script.sh"

def parse_arguments():
	parser = argparse.ArgumentParser(description="Benchmarking cipher/decipher binaries with EvalMe")
	parser.add_argument("input_directory", help="Input directory. The directory must contain a folder called \"Plaintext\", where original files are. Additionally, a folder for each cipher algorithm should be created.")
	#parser.add_argument("output", help="Input directory")
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


if __name__ == '__main__':
	arguments = parse_arguments()

	plaintext_files = []
	plaintext_files_md5 = {}

	# Retrieving plaintext files
	for (path, dirs, files) in os.walk(os.path.join(arguments.input_directory, plaintext_folder)):
		for file in files:
			plaintext_files.append(file)

	print(plaintext_files)

	# Computing MD5 of plaintext files
	for file in plaintext_files:
		file_path = os.path.join(path, file)
		plaintext_files_md5[file_path] = (file, get_md5_of_file(file_path))

	print(plaintext_files_md5)	

	for (path, dirs, files) in os.walk(arguments.input_directory):

		print(path)
		print(dirs)

		
		#if path != os.path.join(arguments.input_directory, plaintext_folder):
			# Ciphering / deciphering and results gathering should happen here. Overhead must be also taken into account
			# Ciphering (pseudocode): 
			# for (file, hash) in plaintext_files_md5:
				# bash = "\"bash_script -c {} {}\"".format(file, )
				# popen = subprocess.run(arguments_array, capture_output=True) script.sh -

	
	