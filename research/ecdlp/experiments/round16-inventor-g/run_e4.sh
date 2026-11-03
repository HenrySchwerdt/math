#!/bin/bash
cd /home/user/math/research/ecdlp/experiments/round16-inventor-g
python3 g4_fibre.py $1 $2 > out_e4_$1_$2.jsonl 2> err_e4_$1_$2.txt
