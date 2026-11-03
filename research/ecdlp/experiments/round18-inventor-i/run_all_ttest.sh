#!/bin/bash
# T_test measurement per PROTOCOL.md (sizes 20..44 step 4, 3 seeds, 20 random + 5 planted targets each)
export PYTHONPATH=/tmp/claude-0/-home-user-math/1a63ece5-8e90-57cd-878a-b7d0d1d0ee6f/scratchpad/pylib
cd "$(dirname "$0")"
for b in 20 24 28 32 36 40 44; do for s in 0 1 2; do echo "$b $s"; done; done | xargs -P 3 -L 1 bash -c 'python3 run_finders.py $0 $1 20 5 1.0 > out_ttest_$0_$1.jsonl'
