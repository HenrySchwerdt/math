"""H2 attack: exhaustive check of 'at most M(M+1) M-bad traces' for all prime powers q <= QMAX.
Method (no factoring of q^m-1 needed): for each integer N in the CLOSED Hasse interval
[q+1-2sqrt q, q+1+2sqrt q] (t = q+1-N, |t|<=2 sqrt q  <=>  (t)^2 <= 4q, exact integer test),
factor N, take primes r | N with r^2 > 16 q (r > 4 sqrt q), r not | q, compute ord_r(q).
mo(t) = min such order (inf if none).  t is M-bad iff mo(t) <= M.
Deterministic; no randomness. Usage: python3 h2_sparsity.py [QMAX] [SEED]  (SEED => sampled mode)"""
import sys
from math import isqrt

QMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
NMAX = QMAX + 1 + 2 * isqrt(QMAX) + 3
spf = list(range(NMAX + 1))
for i in range(2, isqrt(NMAX) + 1):
    if spf[i] == i:
        for j in range(i * i, NMAX + 1, i):
            if spf[j] == j:
                spf[j] = i

def pfactors(n):
    s = set()
    while n > 1:
        p = spf[n]; s.add(p)
        while n % p == 0: n //= p
    return s

def prime_power(q):
    if q < 2: return None
    p = spf[q]; 
    while q % p == 0: q //= p
    return p if q == 1 else None

def order(q, r):
    o = r - 1
    for f in pfactors(o):
        while o % f == 0 and pow(q, o // f, r) == 1: o //= f
    return o

best = {}   # M -> (count, q, ts)
MS = list(range(1, 13))
worst_ratio = 0
total_q = 0
viol = []
import random
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else None
if SEED is None:
    qs = range(2, QMAX + 1)
else:  # sampled mode: 400 random prime powers in [2e4, QMAX]
    rnd = random.Random(SEED); qs = []
    while len(qs) < 400:
        c = rnd.randrange(20000, QMAX + 1)
        if prime_power(c) is not None: qs.append(c)
for q in qs:
    if prime_power(q) is None: continue
    total_q += 1
    ts = {}
    for N in range(1, q + 1 + 2 * isqrt(q) + 2):
        t = q + 1 - N
        if t * t > 4 * q: continue          # exact |t| <= 2 sqrt q
        mo = None
        for r in pfactors(N):
            if r * r > 16 * q and q % r != 0:   # r > 4 sqrt q exactly
                o = order(q, r)
                mo = o if mo is None else min(mo, o)
        if mo is not None: ts[t] = mo
    for M in MS:
        c = sum(1 for v in ts.values() if v <= M)
        if c > M * (M + 1): viol.append((q, M, c))
        if M not in best or c > best[M][0]:
            best[M] = (c, q, sorted(t for t, v in ts.items() if v <= M))
print('prime powers tested:', total_q, 'q range 2..', QMAX)
print('violations of M(M+1):', viol)
for M in MS:
    c, q, ts = best[M]
    print(f'M={M:2d} bound M(M+1)={M*(M+1):3d} max #bad t={c} at q={q} t={ts[:8]}')
