"""Addendum runner for C1b (see PROTOCOL_ADDENDUM.md). Usage: bench2.py BITS  -> out_negw_BITS.jsonl"""
import json, random, sys, time
from lib12 import find_prime_order_curve, Ops
from algos2 import rho_neg_w
from bench import Lmask, trials_for
bits = int(sys.argv[1])
E, P, n = find_prime_order_curve(bits, 'c12')
out = open(f'out_negw_{bits}.jsonl', 'w')
for t in range(trials_for(bits)):
    k = random.Random(f'k-{bits}-{t}').randrange(1, n); Q = E.mul(k, P)
    ops = Ops(E.p, E.a); t0 = time.time()
    kk, c, info = rho_neg_w(ops, P, Q, n, random.Random(f'w-{bits}-{t}'), Lmask(n, 16))
    rec = dict(mode='negw', bits=bits, p=E.p, n=n, trial=t, ops=c, setup=ops.setup, ok=(kk == k), dps=info[0], stats=info[1], sec=round(time.time()-t0, 3))
    out.write(json.dumps(rec)+'\n'); out.flush(); print(rec, flush=True)
