# EvalMe
An open-source benchmarking tool.

## Requisites
**EvalMe** requires the following software to be already installed in the system:
* [Hyperfine](https://github.com/sharkdp/hyperfine)
* [Python 3+](https://www.python.org/downloads/) and the libraries in `requirements.txt`

## Installation
The installation of EvalMe only requires:
* Cloning this repo `git clone https://github.com/reverseame/evalme`
* Installing Python requirements `pip3 install -r requirements.txt`
![installation](https://i.imgur.com/hXGThNv.gif)

## Usage
EvalMe has several avaialable options and it is fully compatible with [Hyperfine](https://github.com/sharkdp/hyperfine). Use `-h` flag to print the **help** message:
* `./evalme.py -h`:
![help](https://i.imgur.com/Ga9rE9x.gif)

Available options:
| flag | effect |value type|example|default value|
|:---|:---|:---|:---|:---|
|-s, --slice|Defines the slice (in seconds) EvalMe will poll the spawned process and check its memory usage.|int|-s 0.001|0.1|
|-r, --runs|Perform exactly RUNS runs for each command.|int|-r 150|10|
|-w, --warmup|Perform NUM warmup runs before the actual benchmark. This can be used to fill (disk) caches for I/O-heavy programs.|int|-w 5||
|-p, --prepare|Execute the command before each timing run. This is useful for clearing disk caches, for example. The --prepare option can be specified once for all commands or multiple times, once for each command. In the latter case, each preparation command will be run prior to the corresponding benchmark command.||||
|-c, --cleanup|Execute the command after the completion of all benchmarking runs for each individual command to be benchmarked. This is useful if the commands to be benchmarked produce artifacts that need to be cleaned up.||||
|-j, --json|Prints JSON-formatted output. CPU is measured in seconds; memory is measured in bytes.||||
|-v, --verbose|Prints the original hyperfine's output.||||
|-h|Prints help message|

* Usage example: `./evalme.py 'i=0; while [ $i -le 1000 ]; do i=$((i+1));aux=$((i*i)); done' -r 100 -s 0.001`
![example](https://i.imgur.com/gU1I1ab.gif)

* JSON output: `./evalme.py 'i=0; while [ $i -le 1000 ]; do i=$((i+1));aux=$((i*i)); done' -r 100 -s 0.001 --json`
![json](https://i.imgur.com/nPobuH0.gif)

## License
**EvalMe** is distributed under the terms of the GNU GPL v3 License. You can read its terms [here](https://github.com/reverseame/evalme/blob/main/LICENSE).

## Authors

Razvan Raducu
Ricardo J. Rodríguez
Pedro Álvarez