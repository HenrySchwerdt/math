#!/bin/bash
cd /home/user/math/research/ecdlp/experiments/round16-inventor-g
python3 g3_search.py $1 $2 $3 > out_e3_$1_$2.jsonl 2> err_e3_$1_$2.txt
