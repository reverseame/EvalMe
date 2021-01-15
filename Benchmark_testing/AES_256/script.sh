#!/bin/bash

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -c|--cipher)
    touch "$3"
    shift # past argument
    shift # past value
    ;;
    -d|--decipher)
    touch "$3"
    shift # past argument
    shift # past value
    ;;
    *)    # unknown option
    shift # past argument
    ;;
esac
done