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


def usage():
	usage = "Use EvalMe with the exact syntax as hyperfine. Example:\n"
	usage += "\tevalme.py \"ls -R\"\n"
	usage += "\tevalme.py --min-runs 5 \"grep -R TODO *\"\n"
	usage += "\tevalme.py -r 150 \"ls -laihR\"\n"
	usage += "\tevalme.py 'i=0; while [ $i -le 1000 ]; do i=$((i+1));aux=$((i*i)); done' -r 10000 -s 0.001\n\n"

	return usage

def parse_arguments():
	parser = argparse.ArgumentParser(description="EvalMe, an open-source benchmarking tool.", usage=usage())
	parser.add_argument("command", help="The command or binary to benchmark")
	parser.add_argument("-s", "--slice", action="store", dest="SLICE_IN_SECONDS", type=float, help="(Default = 0.1) Defines the slice (in seconds) EvalMe will poll the spawned process and check its memory usage.")
	parser.add_argument("-w", "--warmup", help="Perform NUM warmup runs before the actual benchmark. This can be used to fill (disk) caches for I/O-heavy programs.")
	#parser.add_argument("-m", "--min-runs", help="Perform at least NUM runs for each command (default: 10).", dest="min-runs")
	#parser.add_argument("-M", "--max-runs", help="Perform at most NUM runs for each command. By default, there is no limit.", dest="max-runs")
	parser.add_argument("-r", "--runs", action="store", type=int, help="(Default = 10) Perform exactly RUNS runs for each command.")
	parser.add_argument("-p", "--prepare", help="Execute the command before each timing run. This is useful for clearing disk caches, for example. \nThe --prepare option can be specified once for all commands or multiple times, once for each command. In the latter case, each preparation command will be run prior to the corresponding benchmark command.")
	parser.add_argument("-c", "--cleanup", help="Execute the command after the completion of all benchmarking runs for each individual command to be benchmarked. This is useful if the commands to be benchmarked produce artifacts that need to be cleaned up.")
	arguments = parser.parse_args()

	return arguments

def launch_hyperfine(arguments):

	# Parsing the corresponding arguments and binary to execute by hiperfine
	arguments_copy = copy.deepcopy(arguments)
	command = arguments_copy.command

	# Delete all commands that are not compatible with hyperfine
	del vars(arguments_copy)['command']
	del vars(arguments_copy)['SLICE_IN_SECONDS']

	arguments_array = []
	for argument,value in vars(arguments_copy).items():
		if value is not None:
			arguments_array.append("--" + str(argument))
			arguments_array.append(str(value))

	arguments_array.append(command)
	arguments_array.insert(0, "hyperfine")

	popen = subprocess.run(arguments_array)


def check_ram_usage(arguments):

	if arguments.runs is not None:
		RUNS = arguments.runs
	else :
		RUNS = 10

	if arguments.SLICE_IN_SECONDS is not None:
		SLICE_IN_SECONDS = arguments.SLICE_IN_SECONDS
	else:
		SLICE_IN_SECONDS = 0.1
	

	#print("RUNS -> " + str(runs))
	print("RUNS VALUE IS ->" + str(RUNS))
	print("SLICE VALUE IS ->" + str(SLICE_IN_SECONDS))
	resultTable = []
	for i in range(0,RUNS):
		proc = subprocess.Popen(arguments.command, shell=True, stdout=subprocess.DEVNULL)
		while proc.poll() is None:
			p = psutil.Process(proc.pid)
			used_memory = p.memory_full_info()
			resultTable.append(used_memory.rss)
			#resultTable.append( humanfriendly.format_size(used_memory.vms))
			resultTable.append(used_memory.vms)
			time.sleep(SLICE_IN_SECONDS)

	real_memory = 0
	virtual_memory = 0
	counter = 0
	for memory in resultTable[::2]:
		real_memory += memory
		counter += 1
	real_memory = real_memory / counter

	counter = 0
	for memory in resultTable[1::2]:
		virtual_memory += memory
		counter += 1
	virtual_memory = virtual_memory / counter

	print("[+] Average of real memory used while executing \"" + str(arguments.command) + "\" " +str(RUNS) + " times: " + humanfriendly.format_size(real_memory))
	print("[+] Average of virtual memory used while executing \"" + str(arguments.command) +"\" "+ str(RUNS) + " times: " + humanfriendly.format_size(virtual_memory))
	#print("ResultTable -> ")
	#print(resultTable)
	#for memory in resultTable:
	#	print(humanfriendly.format_size(memory))


if __name__ == '__main__':
	arguments = parse_arguments()
	launch_hyperfine(arguments)
	check_ram_usage(arguments)
	
	# Helpful links:
	# https://stackoverflow.com/questions/12263779/how-to-get-memory-usage-of-an-external-program-python
	# https://psutil.readthedocs.io/en/latest/#psutil.Process.memory_info