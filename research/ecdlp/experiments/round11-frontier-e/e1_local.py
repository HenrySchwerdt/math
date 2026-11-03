"""E1 local integer structure of (x_k, x_{k+j}). See PROTOCOL.md. usage: e1_local.py SEED [NNULL]"""
import sys, time
import numpy as np
from common import *

SH = [1, 2, 3, 5]

def stats(X, r, p, j):
    a = X[1:r - j]; b = X[1 + j:r]; N = len(a)
    out = {}
    # G
    ia = a * 16 // p; ib = b * 16 // p
    T = np.bincount(ia * 16 + ib, minlength=256).reshape(16, 16).astype(float)
    E = np.outer(T.sum(1), T.sum(0)) / N
    out['G'] = float(((T - E) ** 2 / E).sum())
    # B
    sh = int(p).bit_length()
    A = np.stack([(a >> i) & 1 for i in range(sh)], 1).astype(np.float32)
    B = np.stack([(b >> i) & 1 for i in range(sh)], 1).astype(np.float32)
    ma, mb = A.mean(0), B.mean(0)
    C = (A.T @ B) / N - np.outer(ma, mb)
    den = np.sqrt(np.outer(ma * (1 - ma), mb * (1 - mb))) + 1e-12
    out['B'] = float(np.abs(C / den).max() * np.sqrt(N))
    # D, S
    d = (b - a) % p
    h = np.bincount(d * 4096 // p, minlength=4096).astype(float)
    out['D'] = float(((h - N / 4096) ** 2 / (N / 4096)).sum())
    out['S'] = float((np.minimum(d, p - d) < p // 1024).sum())
    return out

def allstats(vals, r, p):
    X = fold(vals, r)
    return {j: stats(X, r, p, j) for j in SH}

def mc(vals, r, p, nnull, rng, label):
    obs = allstats(vals, r, p)
    nulls = []
    for _ in range(nnull):
        nulls.append(allstats(rng.permutation(vals), r, p))
    res = {}
    for j in SH:
        for s in 'GBDS':
            arr = np.array([n[j][s] for n in nulls]); mu, sd = arr.mean(), arr.std()
            zo = abs(obs[j][s] - mu) / sd; zn = np.abs(arr - mu) / sd
            pv = (1 + (zn >= zo).sum()) / (nnull + 1)
            res[(s, j)] = (obs[j][s], zo, pv)
    print(f'--- {label}  (min attainable p={1/(nnull+1):.4f})')
    for j in SH:
        print(f' j={j} ' + '  '.join(f'{s}: z={res[(s,j)][1]:6.2f} p={res[(s,j)][2]:.4f}' for s in 'GBDS'))
    det = [f'{s}{j}' for (s, j), v in res.items() if v[2] <= 1.0 / (nnull + 1) + 1e-12]
    print(f' DETECTED cells ({label}): {det}')
    sys.stdout.flush()
    return det

if __name__ == '__main__':
    seed = int(sys.argv[1]); nnull = int(sys.argv[2]) if len(sys.argv) > 2 else 150; nctl = int(sys.argv[3]) if len(sys.argv) > 3 else nnull
    t0 = time.time()
    rng = random.Random(seed); E, r = prime_order_curve(rng)
    print(f'seed={seed} p={E.p} a={E.a} b={E.b} r={r} prime-order, r!=p')
    vals = half_orbit(E, r); M = len(vals)
    print(f'orbit built {time.time()-t0:.1f}s; distinct={len(set(vals.tolist()))}=={M}')
    nr = np.random.default_rng(1000 + seed)
    real = mc(vals, r, E.p, nnull, nr, 'REAL')
    pl = vals.copy()
    ks = nr.choice(np.arange(0, M - 1), size=int(0.02 * M), replace=False)
    pl[ks + 1] = (pl[ks] + nr.integers(0, E.p // 1024, size=len(ks))) % E.p
    # planted values may no longer be distinct; harmless for E1
    pos = mc(pl, r, E.p, nctl, nr, 'POSITIVE CONTROL (planted)')
    neg = mc(nr.integers(0, E.p, size=M), r, E.p, nctl, nr, 'NEGATIVE CONTROL (iid)')
    print(f'total {time.time()-t0:.1f}s')
