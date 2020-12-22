#!/usr/bin/python3
'''
@Authors:
	Razvan Raducu
	Ricardo J Rodriguez
	Pedro Álvarez

We used pipreqs to generate requirements.txt
https://github.com/bndr/pipreqs
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
	usage += "\tevalme.py -r 150 \"ls -laihR\"\n\n"

	return usage

def parse_arguments():
	parser = argparse.ArgumentParser(description="EvalMe, an open-source benchmarking tool.", usage=usage())
	parser.add_argument("command", help="The command or binary to benchmark")
	parser.add_argument("-w", "--warmup", help="Perform NUM warmup runs before the actual benchmark. This can be used to fill (disk) caches for I/O-heavy programs.")
	parser.add_argument("-m", "--min-runs", help="Perform at least NUM runs for each command (default: 10).", dest="min-runs")
	parser.add_argument("-M", "--max-runs", help="Perform at most NUM runs for each command. By default, there is no limit.", dest="max-runs")
	parser.add_argument("-r", "--runs", help="Perform exactly NUM runs for each command. If this option is not specified, hyperfine automatically determines the number of runs.")
	parser.add_argument("-p", "--prepare <CMD>...", help="Execute CMD before each timing run. This is useful for clearing disk caches, for example. \nThe --prepare option can be specified once for all commands or multiple times, once for each command. In the latter case, each preparation command will be run prior to the corresponding benchmark command.")
	parser.add_argument("-c", "--cleanup <CMD>", help="Execute CMD after the completion of all benchmarking runs for each individual command to be benchmarked. This is useful if the commands to be benchmarked produce artifacts that need to be cleaned up.")
	arguments = parser.parse_args()

	return arguments

def launch_hyperfine(arguments):

	# Parsing the corresponding arguments and binary to execute by hiperfine
	arguments_copy = copy.deepcopy(arguments)
	command = arguments_copy.command

	# Delete ([("command", binary)...])
	del vars(arguments_copy)['command']

	arguments_array = []
	for argument,value in vars(arguments_copy).items():
		if value is not None:
			arguments_array.append("--" + str(argument))
			arguments_array.append(str(value))

	arguments_array.append(command)
	arguments_array.insert(0, "hyperfine")

	popen = subprocess.run(arguments_array)


def check_ram_usage(arguments):
	runs = 10
	if arguments.runs is not None:
		runs = int(arguments.runs)

	#print("RUNS -> " + str(runs))
	SLICE_IN_SECONDS = 0.1
	resultTable = []
	for i in range(0,runs):
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

	print("[+] Average of real memory used while executing \"" + str(arguments.command) + "\" " +str(runs) + " times: " + humanfriendly.format_size(real_memory))
	print("[+] Average of virtual memory used while executing \"" + str(arguments.command) +"\" "+ str(runs) + " times: " + humanfriendly.format_size(virtual_memory))
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