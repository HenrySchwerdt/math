#!/bin/bash
cd "$(dirname "$0")"; export PYTHONPATH=/tmp/claude-0/-home-user-math/1a63ece5-8e90-57cd-878a-b7d0d1d0ee6f/scratchpad/pylib
for m in 2 3 4; do for d in 4 6 8 10 12 14 16 20 24; do echo "$m $d"; done; done | xargs -P 4 -L 1 bash -c 'timeout 90 python3 gb.py $0 $1 > out_gb_$0_$1.jsonl 2>/dev/null || echo "{\"m\":$0,\"d\":$1,\"timeout_s\":90}" > out_gb_$0_$1.jsonl'
