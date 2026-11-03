#!/bin/bash
# usage: run_e3.sh BITS  (runs 3 curves in parallel, nH=48)
cd "$(dirname "$0")"
python3 - "$1" <<'PY' | xargs -P 3 -L 1 ./e3
import json,sys
for c in json.load(open('curves_confirm.json')):
    if c['bits']==int(sys.argv[1]): print(c['p'],c['a'],c['b'],c['r'],c['Px'],c['Py'],c['bits'],f"out_e3c_{c['bits']}_{c['seed']}.json",48)
PY
