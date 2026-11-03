#!/bin/bash
cd "$(dirname "$0")"
rm -f out_t2.jsonl
for cfg in "1000 11 1" "1000 12 1" "4100 11 1" "4100 12 1" "12000 11 1" "12000 12 1" "30000 11 0" "30000 12 0"; do
  set -- $cfg
  ( time python3 t2_cocycle.py $1 $2 $3 ) >> out_t2.jsonl 2>> log_t2.txt
done
echo done > t2_done.flag
