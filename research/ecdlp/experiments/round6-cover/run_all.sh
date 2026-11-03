#!/bin/sh
# Official runs, executed through scripts/research.py exec (one invocation per size / curve).
RUN=RUN-9e957bce-b882-4389-860f-d3b1fed7ec75
D=research/ecdlp/experiments/round6-cover
for b in 8 10 12; do
  python3 scripts/research.py exec ecdlp $RUN -- python3 $D/icj.py --bits $b --curves 3 --out $D/results_bits$b.json
done
