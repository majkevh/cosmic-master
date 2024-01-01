#!/bin/bash

# Default values
alg="CCPH"
snapshot=99
dataset="TNG50-1-Dark"
crop=100

# Optional arguments with default values
bs=${bs:-32}   # batch size
nb=${nb:-10}   # number of batches
mr=${mr:-0.5}  # max radius

# Executing Python script with arguments
python3 parser.py -alg "$alg" -snap "$snapshot" -dt "$dataset" -bs "$bs" -nb "$nb" -mr "$mr" -crop "$crop"

# Exiting with the status of the last command
exit $?
