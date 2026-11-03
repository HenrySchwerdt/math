#!/bin/bash
# success probability per random target (MITM exact), bits {20,24,28}, kappa {1,2,3,4}, 3 curves
export PYTHONPATH=/tmp/claude-0/-home-user-math/1a63ece5-8e90-57cd-878a-b7d0d1d0ee6f/scratchpad/pylib
cd "$(dirname "$0")"
for b in 20 24 28; do for k in 1.0 2.0 3.0 4.0; do for s in 0 1 2; do echo "$b $k $s"; done; done; done | xargs -P 4 -L 1 bash -c 'n=1500; [ $0 -ge 28 ] && n=700; python3 run_finders.py $0 $2 $n 0 $1 coset notower > out_lambda_$0_$1_$2.jsonl'
