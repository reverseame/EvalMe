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