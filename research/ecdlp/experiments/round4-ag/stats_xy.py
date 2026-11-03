# Moments / max / symmetry of Y_c for g in {x, y} split by p mod 4. Seeded.
import random, sys, json
import numpy as np
from common import *
SEED = 20261104
rng = random.Random(SEED); random.seed(SEED)
primes = [p for p in range(1000, 5000) if is_prime(p)]
acc = {}
for p in rng.sample(primes, 120):
    L = legendre_table(p)
    res = random_prime_order_curve(p, rng, L)
    if not res: continue
    a, b, r = res
    E = Curve(a, b, p); pts = orbit(E, r)
    for g in ['x', 'y']:
        seq = np.array([0 if Q is None else int(L[(Q[0] if g=='x' else Q[1]) % p]) for Q in pts], dtype=float)
        Y = np.fft.fft(seq)[1:] / np.sqrt(p)          # c=1..r-1 (sign of exponent irrelevant)
        key = (g, p % 4)
        d = acc.setdefault(key, dict(m2=[], m4=[], m6=[], mx=[], reim=[], n=0))
        A = np.abs(Y)**2
        d['m2'].append(A.mean()); d['m4'].append((A**2).mean()); d['m6'].append((A**3).mean())
        d['mx'].append(np.abs(Y).max()); d['n'] += 1
        # symmetry: y odd => Y real if p=1(4), imaginary if p=3(4)
        d['reim'].append(float(np.abs(Y.imag).max() if p % 4 == 1 else np.abs(Y.real).max()) if g == 'y' else float(np.abs(Y.imag).max()))
out = {}
for (g, m), d in sorted(acc.items()):
    out[f"g={g},p%4={m}"] = dict(curves=d['n'], m2=round(float(np.mean(d['m2'])), 4), m4=round(float(np.mean(d['m4'])), 4),
        m6=round(float(np.mean(d['m6'])), 4), maxY=round(float(np.max(d['mx'])), 4),
        max_forbidden_part=float(np.max(d['reim'])))
print(json.dumps(out, indent=1))
