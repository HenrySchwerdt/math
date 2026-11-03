"""E1: closure ratio of coordinate-defined sets. usage: g1_coord.py BITS SEED REPS [S_FACTOR]
For each family and each rep (random window offset / pattern), V = ~s points (negation-closed), s = S_FACTOR*sqrt(p).
Statistics (all ratios observed / prediction for a uniformly random s-subset of E):
 tri  : ordered pairs (u,v), u!=v, u+v!=O, u+v in V          (m=2 closed relations; pred s(s-1)(s-2)/(N-2))
 quad : unordered pairs of distinct unordered pairs with equal sum, i.e. closed 4-relations u+v=w+t (m=3 supply); pred C(M,2)/(N-1), M=C(s,2)
 cov  : |V+V| / N versus random expectation (1-exp(-M/N)) ~ target coverage for m=2 decomposition"""
import sys, json, random, math
import numpy as np
from g_lib import *

def popcount(a):
    a = a.copy(); c = np.zeros_like(a)
    while a.any(): c += a & 1; a >>= 1
    return c

def family_sets(name, p, a, b, X, Y, s, rng):
    Ym = np.minimum(Y, p - Y); n = len(X)
    if name == 'rand': return rng.sample(range(n), s)
    if name == 'xwin': sc = X
    elif name == 'ywin': sc = Ym
    elif name == 'box':  # joint window: x in a random interval of width p/4, then the s smallest ybar inside it
        x0 = rng.randrange(p); w = p // 4; inside = np.nonzero(((X - x0) % p) < w)[0]
        return list(inside[np.argsort(Ym[inside], kind='stable')[:s]])
    elif name == 'lowbits':
        t = max(1, int(round(math.log2(n / s) / 2))); c1, c2 = rng.randrange(1 << t), rng.randrange(1 << t)
        idx = np.nonzero(((X & ((1 << t) - 1)) == c1) & ((Ym & ((1 << t) - 1)) == c2))[0]
        return list(idx)
    elif name == 'popcount':
        sc = popcount(X) * (1 << 20) + popcount(Ym) * (1 << 10) + (X % 1024)  # low Hamming weight of (x,ybar) jointly, tie-break x
        o = np.argsort(sc, kind='stable'); return list(o[:s])
    elif name == 'xyl':  # integer linear form of (x,y), symmetrised
        al, be = rng.randrange(1, p), rng.randrange(1, p)
        u1 = (al * X + be * Y) % p; u2 = (al * X - be * Y) % p; sc = np.minimum(u1, u2)
    elif name == 'xap':  # x in an arithmetic progression of F_p with random ratio (short integer vector image)
        c = rng.randrange(1, p); sc = X * pow(c, -1, p) % p
    elif name == 'xy':  # product x*y
        m = X * Y % p; sc = np.minimum(m, p - m)
    elif name == 'ordmin':  # local minima of ybar along x order, then x-window of s of them
        h = np.nonzero(Y <= p - Y)[0]; ox = h[np.argsort(X[h], kind='stable')]; ys = Ym[ox]; lm = np.zeros(len(ox), bool)
        lm[1:-1] = (ys[1:-1] < ys[:-2]) & (ys[1:-1] < ys[2:]); xsel = X[ox[lm]]; st = rng.randrange(0, max(1, len(xsel) - s // 2)); xsel = xsel[st:st + s // 2]
        return list(np.nonzero(np.isin(X, xsel))[0])
    elif name == 'ordgap':  # largest gaps to the next x in sorted order (order statistics of integer spacings)
        ux = np.unique(X); gap = np.diff(np.concatenate([ux, [ux[0] + p]])); big = ux[np.argsort(-gap, kind='stable')[:s // 2 + 1]]
        return list(np.nonzero(np.isin(X, big))[0])
    else: raise ValueError(name)
    o = np.argsort(sc, kind='stable'); st = rng.randrange(0, max(1, n - s)); return list(o[st:st + s])

FAMS = ['rand', 'xwin', 'ywin', 'box', 'lowbits', 'popcount', 'xyl', 'xap', 'xy', 'ordmin', 'ordgap']

def stats(p, a, N, Xv, Yv):
    s = len(Xv); key = np.sort(keys_of(p, Xv, Yv)); tri = 0; sums = []
    rows = max(1, (1 << 22) // s)
    for i0 in range(0, s, rows):
        i1 = min(s, i0 + rows); I = np.repeat(np.arange(i0, i1), s); J = np.tile(np.arange(s), i1 - i0); m = I != J; I, J = I[m], J[m]
        x3, y3, ok = add_vec(p, a, Xv[I], Yv[I], Xv[J], Yv[J]); k3 = keys_of(p, x3[ok], y3[ok])
        pos = np.searchsorted(key, k3); pos[pos == s] = s - 1; tri += int((key[pos] == k3).sum())
        un = (I < J)[ok]; sums.append(k3[un])
    allk = np.sort(np.concatenate(sums)); M = len(allk)
    d = np.diff(np.concatenate([[-1], allk, [-2]]) != 0)  # run boundaries
    idx = np.nonzero(np.concatenate([[True], allk[1:] != allk[:-1], [True]]))[0]; r = np.diff(idx)
    quad = int((r * (r - 1) // 2).sum()); cov = len(r) / N
    pm = s * (s - 1) / 2
    return dict(s=s, tri=tri, tri_pred=predicted_closure(s, N), quad=quad, quad_pred=pm * (pm - 1) / 2 / (N - 1), cov=cov, cov_pred=1 - math.exp(-pm / N))

if __name__ == '__main__':
    bits, seed, reps = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); sf = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5
    C = gen_curve(bits, seed); p, a, b, N = C['p'], C['a'], C['b'], C['N']
    X, Y, N2 = all_points(p, a, b); assert N2 == N
    s = int(sf * math.sqrt(p)); rng = random.Random(7 * bits + seed)
    for fam in FAMS:
        for rep in range(reps):
            idx = np.array(sorted(set(family_sets(fam, p, a, b, X, Y, s, rng))), dtype=np.int64)
            if len(idx) < 8: continue
            st = stats(p, a, N, X[idx], Y[idx]); st.update(fam=fam, bits=bits, seed=seed, rep=rep, p=p, N=N)
            print(json.dumps(st), flush=True)
