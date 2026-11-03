"""Frozen benchmark runner for round12-inventor-c. Usage: python3 bench.py MODE  (see PROTOCOL.md)
Writes out_MODE.jsonl (one JSON object per line). Verifies correctness of every output against known k
(k*P == Q is by construction) and, for bits<=32 on the first 4 trials per size, against lab dlog_bsgs."""
import json, math, random, sys, time, hashlib, os
from lib12 import find_prime_order_curve, Ops
from algos import rho_ref, rho_neg, PreTable, batch_rho
from toyec import dlog_bsgs

def Lmask(n, div, scale=None):
    base = n**0.5 if scale is None else scale
    return 2**max(1, round(base/div).bit_length()-1)

def trials_for(bits): return 16 if bits <= 36 else 12

def single(mode, f):
    sizes = (24, 28, 32, 36, 40, 44)
    out = open(f'out_{mode}.jsonl', 'w')
    for bits in sizes:
        E, P, n = find_prime_order_curve(bits, 'c12')
        for t in range(trials_for(bits)):
            k = random.Random(f'k-{bits}-{t}').randrange(1, n); Q = E.mul(k, P)
            if bits <= 32 and t < 4: assert dlog_bsgs(E, P, Q, n) == k
            ops = Ops(E.p, E.a); t0 = time.time()
            kk, c, info = f(ops, P, Q, n, random.Random(f'w-{bits}-{t}'), Lmask(n, 16))
            rec = dict(mode=mode, bits=bits, p=E.p, n=n, trial=t, ops=c, setup=ops.setup, ok=(kk == k),
                       dps=(info if isinstance(info, int) else info[0]), sec=round(time.time()-t0, 3))
            if not isinstance(info, int): rec['stats'] = info[1]
            out.write(json.dumps(rec)+'\n'); out.flush()
            print(rec, flush=True)

def pre():
    out = open('out_pre.jsonl', 'w')
    for bits in (20, 24, 28, 32, 36):
        E, P, n = find_prime_order_curve(bits, 'c12')
        c3 = n**(1/3)
        ops = Ops(E.p, E.a)
        tb = PreTable(ops, P, n, random.Random(f'pre-{bits}'), int(2*c3)+1, max(2, int(c3)))
        for t in range(32):
            k = random.Random(f'k-{bits}-{t}').randrange(1, n); Q = E.mul(k, P)
            if bits <= 32 and t < 4: assert dlog_bsgs(E, P, Q, n) == k
            kk, c, r = tb.query(Q, random.Random(f'q-{bits}-{t}'))
            rec = dict(mode='pre', bits=bits, n=n, trial=t, online_ops=c, restarts=r, ok=(kk == k),
                       pre_ops=tb.pre_ops, S=len(tb.table), chains=tb.chains, L=tb.mask+1)
            out.write(json.dumps(rec)+'\n'); out.flush(); print(rec, flush=True)

def batch(mode, cases):
    out = open(f'out_{mode}.jsonl', 'w')
    for bits, M, T in cases:
        E, P, n = find_prime_order_curve(bits, 'c12')
        for t in range(T):
            rng = random.Random(f'b-{bits}-{M}-{t}')
            ks = [rng.randrange(1, n) for _ in range(M)]
            Qs = [E.mul(x, P) for x in ks]
            if bits <= 32 and t < 4 and M <= 16: assert all(dlog_bsgs(E, P, q, n) == x for q, x in zip(Qs[:2], ks[:2]))
            ops = Ops(E.p, E.a); t0 = time.time()
            res, c, d = batch_rho(ops, P, Qs, n, random.Random(f'bw-{bits}-{M}-{t}'), Lmask(n, 8, (n/(M+1))**0.5))
            rec = dict(mode=mode, bits=bits, n=n, M=M, trial=t, ops=c, per_instance=c/M, ok=(res == ks), dps=d,
                       sec=round(time.time()-t0, 3))
            out.write(json.dumps(rec)+'\n'); out.flush(); print(rec, flush=True)

if __name__ == '__main__':
    m = sys.argv[1]
    if m == 'ref': single('ref', rho_ref)
    elif m == 'neg': single('neg', rho_neg)
    elif m == 'pre': pre()
    elif m == 'batchN': batch('batchN', [(24,16,12),(28,16,12),(32,16,12),(36,16,12),(40,16,6)])
    elif m == 'batchM': batch('batchM', [(32,M,12) for M in (1,2,4,8,16,32,64)])
    else: raise SystemExit('unknown mode')
