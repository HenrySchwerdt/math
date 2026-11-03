#!/bin/bash
# usage: run_e1.sh BITS ; all curves of that size, S exponents 1/3,1/2,2/3 and full (<=24 bits)
cd "$(dirname "$0")"
python3 - "$1" <<'PY' | while read args; do ./e1 $args; done
import json,sys
b=int(sys.argv[1])
for c in json.load(open('curves.json')):
    if c['bits']!=b: continue
    for ex in (0.3333333,0.5,0.6666667)+((0,) if b<=24 else ()):
        print(c['p'],c['a'],c['b'],c['r'],c['Px'],c['Py'],c['bits'],f"out_e1_{c['bits']}_{c['seed']}_{ex:.2f}.json",ex)
PY
