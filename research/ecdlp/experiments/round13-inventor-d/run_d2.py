"""usage: run_d2.py MODE GIDX BITS SEEDS(comma) [KIND] ; MODE in full|perrel|rho. Appends JSON lines to out_<mode>_<gidx>_<bits>.jsonl"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d2lib import *
mode, gidx, bits = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
seeds = [int(x) for x in sys.argv[4].split(',')]
kinds = sys.argv[5].split(',') if len(sys.argv) > 5 else ['coset']
fn = os.path.join(HERE, f'out_{mode}_{gidx}_{bits}.jsonl')
for sd in seeds:
    inst = gen_instance(bits, sd, gidx)
    if mode == 'rho':
        from common import rho_dp
        k, n = rho_dp(dict(a=inst['a'], b=inst['b'], p=inst['p'], r=inst['r'], P=inst['P'], Q=inst['Q']), rng_seed=sd)
        res = dict(bits=bits, seed=sd, gidx=gidx, p=inst['p'], r=inst['r'], U1=n, ok=(k == inst['k']), rho_walk_model=(math.pi*inst['r']/2)**0.5)
        res2 = [res]
    elif mode == 'full':
        res2 = [run_pipeline(inst, kd, sd) for kd in kinds]
    else:
        res2 = [per_relation(inst, kd, sd, 40) for kd in kinds]
    for res in res2:
        print(json.dumps(res)); open(fn, 'a').write(json.dumps(res) + '\n')
