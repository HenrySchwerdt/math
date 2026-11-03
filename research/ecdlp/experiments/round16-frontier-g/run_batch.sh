#!/bin/bash
# usage: run_batch.sh GENS SEED... ; seeds >= 10 run seeded
cd "$(dirname "$0")"
G=$1; shift
for s in "$@"; do
  if [ "$s" -ge 10 ]; then python3 evolve.py $s $G seeded >> log_evolve_$s.txt 2>&1 & else python3 evolve.py $s $G >> log_evolve_$s.txt 2>&1 & fi
done
wait
tail -n1 log_evolve_*.txt
