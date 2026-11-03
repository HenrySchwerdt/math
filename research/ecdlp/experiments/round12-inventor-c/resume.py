"""Completes (bits, trial) runs of bench.py single() that were cut off by the 295 s timeout. Same code, same
seeds; writes to out_{mode}_resume_{bits}_{tlist}.jsonl. Usage: resume.py MODE BITS T1,T2,..."""
import json, random, sys, time
from lib12 import find_prime_order_curve, Ops
from algos import rho_ref, rho_neg
from bench import Lmask
mode, bits, ts = sys.argv[1], int(sys.argv[2]), [int(x) for x in sys.argv[3].split(',')]
f = {'ref': rho_ref, 'neg': rho_neg}[mode]
E, P, n = find_prime_order_curve(bits, 'c12')
out = open(f'out_{mode}_resume_{bits}_{sys.argv[3].replace(",","-")}.jsonl', 'w')
for t in ts:
    k = random.Random(f'k-{bits}-{t}').randrange(1, n); Q = E.mul(k, P)
    ops = Ops(E.p, E.a); t0 = time.time()
    kk, c, info = f(ops, P, Q, n, random.Random(f'w-{bits}-{t}'), Lmask(n, 16))
    rec = dict(mode=mode, bits=bits, p=E.p, n=n, trial=t, ops=c, setup=ops.setup, ok=(kk == k),
               dps=(info if isinstance(info, int) else info[0]), sec=round(time.time()-t0, 3))
    if not isinstance(info, int): rec['stats'] = info[1]
    out.write(json.dumps(rec)+'\n'); out.flush(); print(rec, flush=True)
