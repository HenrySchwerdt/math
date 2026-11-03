#!/bin/bash
# usage: run_e1.sh BITS SEED REPS TAG
cd /home/user/math/research/ecdlp/experiments/round16-inventor-g
python3 g1_coord.py $1 $2 $3 > out_e1_$4_$1_$2.jsonl 2> err_e1_$4_$1_$2.txt
