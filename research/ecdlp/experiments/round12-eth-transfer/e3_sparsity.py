"""E3: sparsity of k -> x(kP) as a polynomial in the ell bits of k (the 'bit-decomposition' polynomial form).
For each prime-order toy curve (bitlength(r)=ell): F(k)=x(kP) (x(O):=0) for k in [0,2^ell).
 (i) ANF over F_2 of each of the m = bitlength(p) output bits: #monomials / 2^ell, max degree.
 (ii) multilinear polynomial over F_p (Moebius transform mod p): fraction of nonzero coefficients, max degree.
Controls: random function table (dense expected), parity of the bits of k (sparse: ell monomials).
Usage: python3 e3_sparsity.py   (seed 31)"""
import sys, os, json, random, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(EXP, 'lib')); sys.path.insert(0, os.path.join(EXP, 'round10-frontier-b'))
from toyec import Curve
import sat_ecdlp as S10

def mobius_xor(a, ell):       # in-place ANF transform over F_2 on uint8 array of length 2^ell
    for i in range(ell):
        v = a.reshape(-1, 2, 1 << i); v[:, 1, :] ^= v[:, 0, :]
    return a

def mobius_mod(a, ell, p):    # multilinear coefficients mod p
    for i in range(ell):
        v = a.reshape(-1, 2, 1 << i); v[:, 1, :] = (v[:, 1, :] - v[:, 0, :]) % p
    return a

def popcount_arr(n):
    pc = np.zeros(1 << n, dtype=np.int16)
    for i in range(n): pc[1 << i: 1 << (i + 1)] = pc[: 1 << i] + 1
    return pc

def xs_table(E, P, ell):
    N = 1 << ell; X = np.zeros(N, dtype=np.int64); R = None
    for k in range(N):
        X[k] = 0 if R is None else R[0]
        R = E.add(R, P)
    return X

def stats_f2(X, m, ell, pc):
    dens, degs = [], []
    for b in range(m):
        a = ((X >> b) & 1).astype(np.uint8); mobius_xor(a, ell)
        nz = a.astype(bool); dens.append(float(nz.mean())); degs.append(int(pc[nz].max()) if nz.any() else -1)
    return dens, degs

def run():
    rng = random.Random(31); rows = []
    for ell in range(6, 17):
        pc = popcount_arr(ell)
        for rep in range(2):
            while True:
                E, P, N, S = S10.find_instance(rng, ell)
                if N.bit_length() == ell: break
            m = E.p.bit_length(); X = xs_table(E, P, ell)
            dens, degs = stats_f2(X, m, ell, pc)
            a = X.copy() % E.p; mobius_mod(a, ell, E.p); nz = a != 0
            rows.append(dict(kind='ecdlp', ell=ell, p=E.p, r=N, m=m, f2_density_min=min(dens), f2_density_median=sorted(dens)[len(dens)//2],
                             f2_density_max=max(dens), f2_maxdeg_min=min(degs), f2_monomials_min=int(min(dens) * 2 ** ell),
                             fp_density=float(nz.mean()), fp_maxdeg=int(pc[nz].max()), fp_nonzero=int(nz.sum()),
                             polylog_budget=int(math.log2(2 ** ell) ** 3)))
        # controls
        Xr = np.array([rng.randrange(E.p) for _ in range(1 << ell)], dtype=np.int64)
        d, g = stats_f2(Xr, m, ell, pc)
        rows.append(dict(kind='control_random', ell=ell, m=m, f2_density_min=min(d), f2_density_median=sorted(d)[len(d)//2], f2_maxdeg_min=min(g)))
        par = np.zeros(1 << ell, dtype=np.int64)
        for i in range(ell): par ^= ((np.arange(1 << ell) >> i) & 1)
        d, g = stats_f2(par, 1, ell, pc)
        rows.append(dict(kind='control_parity', ell=ell, m=1, f2_density_min=d[0], f2_maxdeg_min=g[0], f2_monomials=int(d[0] * 2 ** ell)))
    json.dump(rows, open(os.path.join(HERE, 'out_e3.json'), 'w'), indent=1)
    for r in rows: print(json.dumps(r))
    e = [r for r in rows if r['kind'] == 'ecdlp']
    print('DECISION: min over all ecdlp rows of f2_density_min = %.3f ; of fp_density = %.3f ; dense(>=0.25 everywhere)=%s' % (
        min(r['f2_density_min'] for r in e), min(r['fp_density'] for r in e),
        all(r['f2_density_min'] >= 0.25 and r['fp_density'] >= 0.25 for r in e)))

if __name__ == '__main__':
    run()
