#!/bin/bash
# usage: run_e2.sh n qlo qhi passes seeds... ; one curve per seed
n=$1; lo=$2; hi=$3; ps=$4; shift 4
for s in "$@"; do python3 research/ecdlp/experiments/round19-frontier-i/e2_alg2.py $n $lo $hi $ps $s; done
