#!/bin/bash
# one 240 s slice for 4 parallel runs
cd "$(dirname "$0")"
export SLICE_SECONDS=${SLICE_SECONDS:-235}
python3 evolve2.py r0 0 120 > log_r0.txt 2>&1 &
python3 evolve2.py r1 1 120 > log_r1.txt 2>&1 &
python3 evolve2.py s2 2 120 seeded > log_s2.txt 2>&1 &
python3 evolve2.py s3 3 120 seeded > log_s3.txt 2>&1 &
wait
tail -n 2 log_r0.txt log_r1.txt log_s2.txt log_s3.txt
