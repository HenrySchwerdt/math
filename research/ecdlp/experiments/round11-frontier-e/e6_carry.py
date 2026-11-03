"""E6 three-term carry predicate c_k=[x_{k+1}+x_{k-1}>=p]. See PROTOCOL_AMENDMENT1.md. usage: e6_carry.py SEED"""
import sys, time
import numpy as np
from common import *

def stat(g):
    g = g.astype(float); g = g - g.mean(); var = g.var()
    F = np.abs(np.fft.rfft(g)) ** 2
    h = np.arange(1, (len(g) - 1) // 2 + 1)
    return (F[h] / (len(g) * var)).max(), int(h[np.argmax(F[h])])

def build(halfg, r):  # halfg[k-2] for k=2..M -> full array length r (index k), mirror, zeros elsewhere filled below
    g = np.zeros(r)
    M = (r - 1) // 2
    ks = np.arange(2, M + 1)
    g[ks] = halfg; g[r - ks] = halfg
    # fill k=0,1,r-1 with the mean to keep length r (they are excluded from signal)
    m = halfg.mean(); g[0] = g[1] = g[r - 1] = m
    return g

def analyse(halfg, r, rng, nshuf, label):
    M = len(halfg); Neff = len(halfg)
    z = (halfg.mean() - 0.5) * 2 * np.sqrt(Neff)
    T, h = stat(build(halfg, r))
    nulls = np.array([stat(build(rng.permutation(halfg), r))[0] for _ in range(nshuf)])
    pv = (1 + (nulls >= T).sum()) / (nshuf + 1)
    print(f'{label}: mean={halfg.mean():.5f} z_mean={z:.2f}  T={T:.2f} at h={h}  null mean={nulls.mean():.2f} max={nulls.max():.2f}  p_T={pv:.4f}')
    sys.stdout.flush()

if __name__ == '__main__':
    seed = int(sys.argv[1]); nshuf = 200
    rng = random.Random(seed); E, r = prime_order_curve(rng)
    vals = half_orbit(E, r); M = len(vals)
    X = fold(vals, r)
    ks = np.arange(2, M + 1)
    c = ((X[ks + 1] + X[ks - 1]) >= E.p).astype(int)
    print(f'seed={seed} p={E.p} r={r}  N={len(c)}')
    nr = np.random.default_rng(3000 + seed)
    analyse(c, r, nr, nshuf, 'REAL carry')
    # extra carry variants (documented here, not pre-registered individually: labelled EXTRA)
    c2 = ((X[ks + 1] + X[ks - 1]) >= E.p // 2 * 3).astype(int)   # EXTRA: sum >= 1.5p? (rare) -- skip if degenerate
    # EXTRA: borrow of x_k - x_{k+1}-x_{k-1}? use [x_k < (x_{k+1}+x_{k-1}) mod p]
    c3 = (X[ks] < ((X[ks + 1] + X[ks - 1]) % E.p)).astype(int)
    analyse(c3, r, nr, nshuf, 'EXTRA [x_k < (x_{k+1}+x_{k-1}) mod p]')
    pc = c.copy(); idx = nr.random(len(c)) < 0.10
    pc[idx] = (np.cos(2 * np.pi * 777 * ks[idx] / r) > 0).astype(int)
    analyse(pc, r, nr, nshuf, 'POSITIVE CONTROL h0=777, 10% overwritten')
    analyse(nr.integers(0, 2, size=len(c)), r, nr, nshuf, 'NEGATIVE CONTROL iid bits')
