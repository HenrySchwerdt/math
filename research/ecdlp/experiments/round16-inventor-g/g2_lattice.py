"""E2: images of short integer vectors Z^d -> E, V = {sum a_i G_i : |a_i| <= B}, G_i known points.
usage: g2_lattice.py BITS D BFAC NK SEED  -- B = max(1, round(BFAC * N^{1/(2d)})) so |V| ~ (2B+1)^d ~ (2 BFAC)^d sqrt(N).
G_1 = P (generator), G_i = lambda_i P with lambda_i random (the log relations are what an attacker does NOT know in ECDLP; here used to classify closure).
For NK random choices of (lambda_i) report: closure split into trivial (coefficient vectors add in Z^d) and nontrivial (wrap-around mod N: carries information),
V+V coverage, and the fraction of k with at least one nontrivial relation."""
import sys, json, math, random
import numpy as np
from g_lib import *

def scalar_mul_pts(p, a, P, ks):
    """x,y of k*P for each integer k in ks (list), by sequential adds on arrays: ks must be 0..B range handled by caller."""
    pass

def multiples(p, a, P, B):
    """arrays of j*P for j=-B..B, j=0 omitted (point O) -> returns dict j-> (x,y) as arrays with coefficient list."""
    xs, ys, js = [], [], []
    cx, cy = P
    cur = P
    pts = {1: P}
    from_ = P
    for j in range(2, B + 1):
        x3, y3, ok = add_vec(p, a, np.array([from_[0]]), np.array([from_[1]]), np.array([P[0]]), np.array([P[1]]))
        assert ok[0]; from_ = (int(x3[0]), int(y3[0])); pts[j] = from_
    for j, (x, y) in pts.items():
        xs += [x, x]; ys += [y, (p - y) % p]; js += [j, -j]
    return np.array(xs, dtype=np.int64), np.array(ys, dtype=np.int64), np.array(js, dtype=np.int64)

def build_V(p, a, gens, B):
    """V as arrays (X,Y,C[s,d]) with first-vector-kept dedup, O excluded. Also returns number of dropped (collisions, O)."""
    d = len(gens); mx, my, mj = zip(*[multiples(p, a, g, B) for g in gens])
    # start with zero-vector 'O': represent sets as points + coefficient matrix, with a flag for O
    X = np.zeros(0, dtype=np.int64); Y = X.copy(); C = np.zeros((0, d), dtype=np.int64)
    # level i: V_i = V_{i-1} + (multiples of G_i) union multiples themselves union V_{i-1}
    for i in range(d):
        nX, nY, nC = [X], [Y], [C]
        m = len(mx[i])
        ci = np.zeros((m, d), dtype=np.int64); ci[:, i] = mj[i]
        nX.append(mx[i]); nY.append(my[i]); nC.append(ci)
        if len(X):
            I = np.repeat(np.arange(len(X)), m); J = np.tile(np.arange(m), len(X))
            x3, y3, ok = add_vec(p, a, X[I], Y[I], mx[i][J], my[i][J])
            nX.append(x3[ok]); nY.append(y3[ok]); nC.append(C[I][ok] + ci[J][ok])
        X = np.concatenate(nX); Y = np.concatenate(nY); C = np.concatenate(nC)
        k = keys_of(p, X, Y); _, first = np.unique(k, return_index=True); first.sort(); X, Y, C = X[first], Y[first], C[first]
    return X, Y, C

def classify(p, a, N, X, Y, C):
    s = len(X); key = keys_of(p, X, Y); o = np.argsort(key); sk = key[o]
    tri = triv = 0; sums = []
    rows = max(1, (1 << 22) // s)
    for i0 in range(0, s, rows):
        i1 = min(s, i0 + rows); I = np.repeat(np.arange(i0, i1), s); J = np.tile(np.arange(s), i1 - i0); m = I != J; I, J = I[m], J[m]
        x3, y3, ok = add_vec(p, a, X[I], Y[I], X[J], Y[J]); I, J = I[ok], J[ok]; k3 = keys_of(p, x3[ok], y3[ok])
        pos = np.searchsorted(sk, k3); pos[pos == s] = s - 1; hit = sk[pos] == k3
        w = o[pos[hit]]; same = (C[I[hit]] + C[J[hit]] == C[w]).all(axis=1)
        tri += int(hit.sum()); triv += int(same.sum())
        sums.append(k3[(I < J)])
    allk = np.unique(np.concatenate(sums))
    return tri, triv, len(allk) / N

if __name__ == '__main__':
    bits, d, bfac, nk, seed = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    C0 = gen_curve(bits, seed); p, a, N = C0['p'], C0['a'], C0['N']
    X, Y, _ = all_points(p, a, C0['b']); rng = random.Random(99 * bits + seed)
    P = (int(X[0]), int(Y[0]))  # prime order: any point generates
    B = max(1, round(bfac * N ** (1.0 / (2 * d))))
    # multiples lam_i * P via double-and-add on python ints (affine)
    def mul(k, Pt):
        R = None; Q = Pt
        while k:
            if k & 1: R = Q if R is None else padd(R, Q)
            Q = padd(Q, Q); k >>= 1
        return R
    def padd(A, Bp):
        if A is None: return Bp
        if Bp is None: return A
        if A[0] == Bp[0] and (A[1] + Bp[1]) % p == 0: return None
        if A == Bp: l = (3 * A[0] * A[0] + a) * pow(2 * A[1], -1, p) % p
        else: l = (Bp[1] - A[1]) * pow(Bp[0] - A[0], -1, p) % p
        x = (l * l - A[0] - Bp[0]) % p; return (x, (l * (A[0] - x) - A[1]) % p)
    for t in range(nk):
        gens = [P] + [mul(rng.randrange(2, N - 1), P) for _ in range(d - 1)]
        Xv, Yv, Cv = build_V(p, a, gens, B); s = len(Xv)
        tri, triv, cov = classify(p, a, N, Xv, Yv, Cv)
        pred = predicted_closure(s, N); pm = s * (s - 1) / 2
        print(json.dumps(dict(bits=bits, d=d, B=B, seed=seed, t=t, p=p, N=N, s=s, tri=tri, trivial=triv, nontrivial=tri - triv, rand_pred=pred, cov=cov, cov_rand=1 - math.exp(-pm / N), box_sums=(4 * B + 1) ** d)), flush=True)
