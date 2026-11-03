#!/bin/bash
cd "$(dirname "$0")"
for kind in j0 j1728; do
  ( for b in 22 26 30 34 38; do python3 run_t1.py $kind $b 30 || echo FAIL $kind $b; done ) &
done
wait
