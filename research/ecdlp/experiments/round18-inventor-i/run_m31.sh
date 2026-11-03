#!/bin/bash
export PYTHONPATH=/tmp/claude-0/-home-user-math/1a63ece5-8e90-57cd-878a-b7d0d1d0ee6f/scratchpad/pylib
cd "$(dirname "$0")"
for b in 20 24 28 32 36 40; do for s in 0 1 2; do echo "$b $s"; done; done | xargs -P 3 -L 1 bash -c 'python3 run_mitm31.py $0 $1 20 5 > out_m31_$0_$1.jsonl'
# random-base control (MITM 2+2 only): same sizes, cost and success are base-independent
for b in 28 36; do for s in 0 1 2; do echo "$b $s"; done; done | xargs -P 3 -L 1 bash -c 'python3 run_finders.py $0 $1 20 5 1.0 random notower > out_ctlrand_$0_$1.jsonl'
