"""E4 (POST-HOC, written after seeing ywin ratio 1.44 and xyl 1.14-1.24 in E1; labelled post-hoc, not pre-registered).
Hypothesis: sets defined by a window of a degree-d function f(x,y) are unions of whole fibres; fibre of f meets E in 3d points summing to O (Abel), so
zero-sum (3d)-tuples exist inside V for free, but they are disjoint (block structure) and can have rank at most |V|/3d.
usage: g4_fibre.py BITS SEED   -> for fam in {rand, ywin, lin(y-alpha x window, NOT negation closed)} and s in {1.5 sqrt p, 2.5 p^{1/3}}:
 tri0 = #{(u,v) ordered, u!=v, -(u+v) in V} (zero-sum triples; = closed triples when V=-V), pred = s(s-1)(s-2)/(N-2) ;
 tri_line = those whose three points lie on the defining fibre (all same value of f);  residual = tri0 - tri_line ;
 rank of the relation matrix over GF(2^31-1) with l(-P) = -l(P) identification, number of unknowns, number of connected components."""
import sys, json, math, random
import numpy as np
from g_lib import *
Q = 2147483647

def rank_mod(rows, ncols):
    M = np.zeros((len(rows), ncols), dtype=np.int64)
    for i, r in enumerate(rows):
        for c, v in r: M[i, c] = (M[i, c] + v) % Q
    rk = 0; m = M.shape[0]
    for c in range(ncols):
        piv = None
        for i in range(rk, m):
            if M[i, c]: piv = i; break
        if piv is None: continue
        M[[rk, piv]] = M[[piv, rk]]; inv = pow(int(M[rk, c]), Q - 2, Q); M[rk] = M[rk] * inv % Q
        nz = np.nonzero(M[:, c])[0]
        for i in nz:
            if i != rk: M[i] = (M[i] - M[i, c] * M[rk]) % Q
        rk += 1
        if rk == m: break
    return rk

def analyse(p, a, N, X, Y, fval):
    """X,Y arrays of V (distinct). fval: array f(P) for P in V and a function for the sum point is NOT needed; line-type = fval equal for u,v and for -w"""
    s = len(X); key = keys_of(p, X, Y); o = np.argsort(key); sk = key[o]
    tri = 0; line = 0; rel = set()
    rows_per = max(1, (1 << 21) // s)
    for i0 in range(0, s, rows_per):
        i1 = min(s, i0 + rows_per); I = np.repeat(np.arange(i0, i1), s); J = np.tile(np.arange(s), i1 - i0); m = (I != J) & (I < J); I, J = I[m], J[m]
        x3, y3, ok = add_vec(p, a, X[I], Y[I], X[J], Y[J]); I, J = I[ok], J[ok]; k3 = keys_of(p, x3[ok], (p - y3[ok]) % p)  # t = -(u+v)
        pos = np.searchsorted(sk, k3); pos[pos == s] = s - 1; hit = sk[pos] == k3
        T = o[pos[hit]]; I2, J2 = I[hit], J[hit]
        tri += 2 * int(hit.sum())  # ordered pairs
        same = (fval[I2] == fval[J2]) & (fval[J2] == fval[T]); line += 2 * int(same.sum())
        for u, v, t in zip(I2.tolist(), J2.tolist(), T.tolist()): rel.add(tuple(sorted((u, v, t))))
    # unknowns: one per +-pair rep (point index or its negation index if present)
    kmap = {int(k): i for i, k in enumerate(key)}
    rep = {}; nunk = 0
    for i in range(s):
        nk = int(X[i]) * p + (p - int(Y[i])) % p
        if nk in kmap and kmap[nk] in rep: rep[i] = (rep[kmap[nk]][0], -1)
        else: rep[i] = (nunk, 1); nunk += 1
    rows = []
    for (u, v, t) in rel:
        row = {}
        for q in (u, v, t):
            c, sg = rep[q]; row[c] = row.get(c, 0) + sg
        row = [(c, v_ % Q) for c, v_ in row.items() if v_ % Q]
        if row: rows.append(row)
    # components via union-find over unknowns using relations
    par = list(range(nunk))
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for r in rows:
        for c, _ in r[1:]: par[f(c)] = f(r[0][0])
    comps = len({f(i) for i in range(nunk)})
    rk = rank_mod(rows, nunk) if rows and nunk <= 700 else None
    return dict(s=s, tri0=tri, line=line, nrel=len(rows), nunk=nunk, comps=comps, rank=rk)

if __name__ == '__main__':
    bits, seed = int(sys.argv[1]), int(sys.argv[2]); C = gen_curve(bits, seed); p, a, b, N = C['p'], C['a'], C['b'], C['N']
    X, Y, _ = all_points(p, a, b); rng = random.Random(5 * bits + seed); n = len(X); Ym = np.minimum(Y, p - Y)
    for sname, s in (('sqrt', int(1.5 * math.sqrt(p))), ('cbrt', int(2.5 * p ** (1 / 3)))):
        for fam in ('rand', 'ywin', 'lin'):
            for rep in range(3):
                alpha = rng.randrange(1, p)
                if fam == 'rand': idx = np.array(rng.sample(range(n), s)); fv = np.arange(s)  # no fibres
                elif fam == 'ywin': sc = Ym; o = np.argsort(sc, kind='stable'); st = rng.randrange(0, n - s); idx = o[st:st + s]; fv = Ym[idx]
                else: sc = (Y - alpha * X) % p; o = np.argsort(sc, kind='stable'); st = rng.randrange(0, n - s); idx = o[st:st + s]; fv = sc[idx]
                if fam == 'ywin': fv = Ym[idx]  # horizontal line: y equal up to sign is handled because relation uses -w: same ybar
                r = analyse(p, a, N, X[idx], Y[idx], fv); pred = predicted_closure(s, N)
                r.update(bits=bits, seed=seed, p=p, N=N, fam=fam, sizing=sname, rep=rep, pred=pred, ratio=r['tri0'] / pred, resid_ratio=(r['tri0'] - r['line']) / pred)
                print(json.dumps(r), flush=True)
