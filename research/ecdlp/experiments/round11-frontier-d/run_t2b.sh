#!/bin/bash
cd "$(dirname "$0")"
rm -f out_t2b.jsonl
for cfg in "1000 11" "1000 12" "4100 11" "300 12" "300 13"; do set -- $cfg; python3 t2b_liftvar.py $1 $2 >> out_t2b.jsonl 2>> log_t2b.txt; done
echo done > t2b_done.flag
