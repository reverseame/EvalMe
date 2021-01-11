#!/usr/bin/python3
'''
pip3 install -r requirements.txt

@Authors:
	Razvan Raducu
	Ricardo J Rodriguez
	Pedro Álvarez

@Limiattions:
	Both hyperfine and Python's subprocess execute plain Bourne shell (/bin/sh) instead of Bash (/bin/bash). That is, commands like ./evalme.py 'for((i=0;i<1000;i++));do aux=$((i*i)); done' will not work because that's Bash sintax. In order to eval it, an equivalente bourne shell command must be provided ./evalme.py 'i=0; while [ $i -le 1000 ]; do i=$((i+1));aux=$((i*i)); done'

@Additional info:
	We used pipreqs to generate requirements.txt https://github.com/bndr/pipreqs
'''
import argparse
import subprocess
import copy
import psutil
import time
import humanfriendly
import sys
import pandas
import json
import os
import tempfile
from datetime import datetime

NAME = "EvalMe"

def usage():
	usage = "Use EvalMe with the exact syntax as hyperfine. Example:\n"
	usage += "\tevalme.py \"ls -R\"\n"
	usage += "\tevalme.py --min-runs 5 \"grep -R TODO *\"\n"
	usage += "\tevalme.py -r 150 \"ls -laihR\"\n"
	usage += "\tevalme.py 'i=0; while [ $i -le 1000 ]; do i=$((i+1));aux=$((i*i)); done' -r 10000 -s 0.001\n\n"

	return usage

def parse_arguments():
	parser = argparse.ArgumentParser(description=NAME + ", an open-source benchmarking tool.", usage=usage())
	parser.add_argument("command", help="The command or binary to benchmark")
	parser.add_argument("-s", "--slice", action="store", dest="SLICE_IN_SECONDS", type=float, help="(Default = 0.1) Defines the slice (in seconds) " +NAME+ " will poll the spawned process and check its memory usage.", default=0.1)
	parser.add_argument("-w", "--warmup", help="Perform NUM warmup runs before the actual benchmark. This can be used to fill (disk) caches for I/O-heavy programs.")
	#parser.add_argument("-m", "--min-runs", help="Perform at least NUM runs for each command (default: 10).", dest="min-runs")
	#parser.add_argument("-M", "--max-runs", help="Perform at most NUM runs for each command. By default, there is no limit.", dest="max-runs")
	parser.add_argument("-r", "--runs", action="store", type=int, help="(Default = 10) Perform exactly RUNS runs for each command.", default=10)
	parser.add_argument("-p", "--prepare", help="Execute the command before each timing run. This is useful for clearing disk caches, for example. \nThe --prepare option can be specified once for all commands or multiple times, once for each command. In the latter case, each preparation command will be run prior to the corresponding benchmark command.")
	parser.add_argument("-c", "--cleanup", help="Execute the command after the completion of all benchmarking runs for each individual command to be benchmarked. This is useful if the commands to be benchmarked produce artifacts that need to be cleaned up.")
	parser.add_argument("--verbose", "-v", action="count", default=0, help="Prints the original hyperfine's output")
	arguments = parser.parse_args()

	return arguments

def get_current_datetime():
	return str(datetime.now()).replace(' ', '_')

def delete_file(filename):
	os.remove(filename)

def print_results_from_json_file(filename):

	print("[+] Results:")
	with open(filename) as file:
		results = json.load(file)["results"]

	for result in results: 
		#print(result)
		print("\t[>] Command: '{}'".format(result['command']))
		#print("\t[>]\tmean:   {} s".format(result['mean']))
		print("\t[>]\tmean:   {:.6f} ms".format(result['mean']*1000)) # manually convert to ms
		print("\t[>]\tstddev: {:.6f} ms".format(result['stddev']*1000))
		print("\t[>]\tmedian: {:.6f} ms".format(result['median']*1000))
		print("\t[>]\tmin:    {:.6f} ms".format(result['min']*1000))
		print("\t[>]\tmax:    {:.6f} ms".format(result['max']*1000))
		print("\t[>]\tuser:    {:.6f} ms".format(result['user']*1000))
		print("\t[>]\tsystem:    {:.6f} ms".format(result['system']*1000))
		print()

def print_descriptive_statistics_from_dataframe(dataframe):
	# loc function allows to get specific values given their label
	# second identifier (in this case 0) is needed as it can be seen
	# in the examples at the official docs:
	# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.loc.html
	#print("\t[>]\tcount " + humanfriendly.format_size(dataframe.loc['count', 0]))
	print("\t[>]\tmean " + humanfriendly.format_size(dataframe.loc['mean', 0]))
	print("\t[>]\tstddev " + humanfriendly.format_size(dataframe.loc['std', 0]))
	print("\t[>]\tmin " + humanfriendly.format_size(dataframe.loc['min', 0]))
	print("\t[>]\tmax " + humanfriendly.format_size(dataframe.loc['max', 0]))
	print()

def launch_hyperfine(arguments):

	# Temporary file creation
	os_handler, filename = tempfile.mkstemp(suffix=".json", dir=".") # If dir is not specified, the file is created within /tmp/
	print("TEMPORARY FILE CREATED -> " + filename)

	# Parsing the corresponding arguments and binary to execute by hiperfine
	arguments_copy = copy.deepcopy(arguments)
	command = arguments_copy.command

	# Delete all commands that are not compatible with hyperfine
	del vars(arguments_copy)['command']
	del vars(arguments_copy)['SLICE_IN_SECONDS']
	del vars(arguments_copy)['verbose']

	arguments_array = []
	for argument,value in vars(arguments_copy).items():
		if value is not None:
			arguments_array.append("--" + str(argument))
			arguments_array.append(str(value))

	arguments_array.append(command)

	# Export to JSON file
	arguments_array.append("--export-json")
	arguments_array.append(filename)

	arguments_array.insert(0, "hyperfine")

	print("[+] Launching hyperfine\n\t"  + str(arguments_array))


	popen = subprocess.run(arguments_array, capture_output=True) # Output is returned as byte sequence
	return_code = popen.returncode

	if arguments.verbose:
		print("[+] Hyperfine original output:\n" + popen.stdout.decode())

	if return_code:
		print_error(popen.stderr.decode())
		return return_code

	print_results_from_json_file(filename)

	# Delete results file
	delete_file(filename)

	return return_code


def check_ram_usage(arguments):

	RUNS = arguments.runs
	SLICE_IN_SECONDS = arguments.SLICE_IN_SECONDS

	resultTable = []
	for i in range(0,RUNS):
		proc = subprocess.Popen(arguments.command, shell=True, stdout=subprocess.DEVNULL)
		#time.sleep(SLICE_IN_SECONDS)
		while proc.poll() is None:
			p = psutil.Process(proc.pid)
			used_memory = p.memory_full_info()
			resultTable.append(used_memory.rss)
			#resultTable.append( humanfriendly.format_size(used_memory.vms))
			resultTable.append(used_memory.vms)
			time.sleep(SLICE_IN_SECONDS)

	#pandas.options.display.float_format = "{0:.2f}".format # Printing statistics with 2 decimals
	print("[+] Results:")
	# Real memory
	print("\tReal memory:")
	print_descriptive_statistics_from_dataframe(pandas.DataFrame(resultTable[::2]).describe(include='all'))

	# Virtual memory
	print("\tVirtual memory:")
	print_descriptive_statistics_from_dataframe(pandas.DataFrame(resultTable[1::2]).describe(include='all'))
	#print("ResultTable -> ")
	#print(resultTable)
	#for memory in resultTable:
	#	print(humanfriendly.format_size(memory))


def print_error(message):
	print(message, file=sys.stderr)

'''
def print_descriptive_statistics(data_array):
	data = pandas.DataFrame(data_array)
	print("\t\t[>] Count:" + data.count())
'''

if __name__ == '__main__':
	arguments = parse_arguments()
	print("[!][*] Benchmarks of executing \"" + str(arguments.command) + "\" " +str(arguments.runs) + " times [*][!]")
	print("[+] CPU BENCHMARK [+]")
	hyperfine_exit_code = launch_hyperfine(arguments)
	if hyperfine_exit_code:
		print_error("[!] Aborting "+NAME+"!")
		sys.exit(-1)
	print("[+] MEMORY BENCHMARK [+]")
	check_ram_usage(arguments)
	
	# Helpful links:
	# https://stackoverflow.com/questions/12263779/how-to-get-memory-usage-of-an-external-program-python
	# https://psutil.readthedocs.io/en/latest/#psutil.Process.memory_info


