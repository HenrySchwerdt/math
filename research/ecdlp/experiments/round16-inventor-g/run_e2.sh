#!/bin/bash
# usage: run_e2.sh BITS D BFAC NK SEED
cd /home/user/math/research/ecdlp/experiments/round16-inventor-g
python3 g2_lattice.py $1 $2 $3 $4 $5 > out_e2_$1_$2_$3_$5.jsonl 2> err_e2_$1_$2_$3_$5.txt
