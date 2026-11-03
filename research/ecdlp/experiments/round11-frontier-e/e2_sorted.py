"""E2 sorted-neighbour index-difference leak. See PROTOCOL.md. usage: e2_sorted.py SEED [NNULL]"""
import sys, time
import numpy as np
from common import *
WS = [1, 2, 4]

def stat_from_order(order, r, w):
    # order[s] = index k (1..M) of s-th smallest value
    k1 = order[:-w]; k2 = order[w:]
    d1 = np.abs(k1 - k2); d2 = np.minimum(k1 + k2, r - k1 - k2)
    m = np.bincount(np.concatenate([d1, d2]), minlength=r)
    return float((m.astype(np.float64) ** 2).sum()), float(m.max())

def allstats(order, r):
    return {w: stat_from_order(order, r, w) for w in WS}

def mc(vals, r, nnull, rng, label):
    M = len(vals)
    order = np.argsort(vals, kind='stable') + 1
    obs = allstats(order, r)
    nulls = [allstats(rng.permutation(M) + 1, r) for _ in range(nnull)]
    print(f'--- {label} (min attainable p={1/(nnull+1):.4f})')
    det = []
    for w in WS:
        row = []
        for si, s in enumerate('CX'):
            arr = np.array([n[w][si] for n in nulls]); mu, sd = arr.mean(), arr.std() + 1e-12
            zo = abs(obs[w][si] - mu) / sd; zn = np.abs(arr - mu) / sd
            pv = (1 + (zn >= zo).sum()) / (nnull + 1)
            row.append(f'{s}: obs={obs[w][si]:.0f} null={mu:.0f}+-{sd:.1f} z={zo:6.2f} p={pv:.4f}')
            if pv <= 1.0 / (nnull + 1) + 1e-12: det.append(f'{s}{w}')
        print(f' w={w} ' + ' | '.join(row))
    print(f' DETECTED cells ({label}): {det}'); sys.stdout.flush()

if __name__ == '__main__':
    seed = int(sys.argv[1]); nnull = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    t0 = time.time()
    rng = random.Random(seed); E, r = prime_order_curve(rng)
    print(f'seed={seed} p={E.p} a={E.a} b={E.b} r={r}')
    vals = half_orbit(E, r); M = len(vals)
    print(f'orbit built {time.time()-t0:.1f}s distinct={len(set(vals.tolist()))}=={M}')
    nr = np.random.default_rng(2000 + seed)
    mc(vals, r, nnull, nr, 'REAL')
    pl = vals.copy(); D0 = 12345
    ks = nr.choice(np.arange(0, M - D0), size=int(0.002 * M), replace=False)
    pl[ks + D0] = (pl[ks] + nr.integers(1, 17, size=len(ks))) % E.p
    mc(pl, r, nnull, nr, 'POSITIVE CONTROL (planted D0=12345)')
    mc(nr.permutation(E.p)[:M], r, nnull, nr, 'NEGATIVE CONTROL (iid distinct)')
    print(f'total {time.time()-t0:.1f}s')
