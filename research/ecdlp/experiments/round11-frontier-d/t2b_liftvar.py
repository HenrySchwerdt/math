"""T2b / Idea 3 (round 11, defined after T1/T2 first outputs; see PROTOCOL Amendment 2): lift-variation of the Hensel-section defect.
g_L(R) = z([N] l_L(R))/p mod p for lifts L=(A,B) of the curve mod p^2 (same Hensel set-theoretic x-lift).
Tests: (i) is g_L - g_0 affine in the lift parameters (a',b')? (ii) is Delta_L(R)=g_L(R)-g_0(R) (and the cocycle defect delta d1) a low-degree polynomial in (x,y) on E(F_p)?
(iii) correlation of Delta with k; (iv) rank of {k, 1, g_L} across t lifts as functions on the orbit (does the unknown-count grow with the number of lifts?)
Usage: python3 t2b_liftvar.py P0 SEED"""
import sys, random, json
sys.path.insert(0, '../round10-frontier-a')
from t3_section_digit import rcb_add, mul
from t2_cocycle import setup, sqrt_mod, poly_fit
import numpy as np

def run(p0, seed):
    rnd, p, a, b, E, N = setup(p0, seed); M = p * p
    while True:
        x = rnd.randrange(p); rhs = (x ** 3 + a * x + b) % p
        if rhs and pow(rhs, (p - 1) // 2, p) == 1: P = (x, sqrt_mod(rhs, p)); break
    pts = [None, P]; R = P
    for k in range(2, N): R = E.add(R, P); pts.append(R)
    def lift(pt, A, B):
        x, y0 = pt; f = (x ** 3 + A * x + B) % M
        y = (y0 + ((f - y0 * y0) // p) * pow(2 * y0, -1, p) * p) % M
        assert (y * y - f) % M == 0; return (x, y, 1)
    def g_seq(da, db):
        A = (a + p * da) % M; B = (b + p * db) % M; b3 = 3 * B % M
        out = [0]
        for k in range(1, N):
            S = mul(N, lift(pts[k], A, B), A, b3, M); X, Y, Z = S
            assert X % p == 0 and Z % p == 0
            out.append((-X * pow(Y, -1, M) % M) // p % p)
        return out
    lifts = [(0, 0), (1, 0), (2, 0), (5, 0), (0, 1), (0, 3), (1, 1), (3, 7)]
    G = {l: g_seq(*l) for l in lifts}
    n = N - 1
    xs = [pts[k][0] for k in range(1, N)]; ys = [pts[k][1] for k in range(1, N)]
    out = dict(p=p, N=N, seed=seed)
    d = lambda l: [(u - v) % p for u, v in zip(G[l][1:], G[(0, 0)][1:])]
    # (i) affine in (a', b'): Delta(2,0) = 2 Delta(1,0); Delta(5,0)=5 Delta(1,0); Delta(0,3)=3 Delta(0,1); Delta(1,1)=Delta(1,0)+Delta(0,1); Delta(3,7)=3D(1,0)+7D(0,1)
    D10, D01 = d((1, 0)), d((0, 1))
    out['affine_checks'] = {
        '2a': d((2, 0)) == [2 * v % p for v in D10], '5a': d((5, 0)) == [5 * v % p for v in D10],
        '3b': d((0, 3)) == [3 * v % p for v in D01], 'a+b': d((1, 1)) == [(u + v) % p for u, v in zip(D10, D01)],
        '3a+7b': d((3, 7)) == [(3 * u + 7 * v) % p for u, v in zip(D10, D01)]}
    rr = random.Random(9)
    out['Delta_nonzero_frac'] = {'a': sum(1 for v in D10 if v) / n, 'b': sum(1 for v in D01 if v) / n}
    out['polyfit_Delta'] = {D: {'Da': poly_fit(xs, ys, D10, p, D, rr), 'Db': poly_fit(xs, ys, D01, p, D, rr),
                                'g0': poly_fit(xs, ys, G[(0, 0)][1:], p, D, rr),
                                'rand': poly_fit(xs, ys, [rr.randrange(p) for _ in range(n)], p, D, rr)} for D in (4, 8, 12, 20)}
    # also in terms of y-multiples: Delta/y, Delta*y (u2 = lam*y*g has the y factor)
    out['polyfit_Delta_div_y'] = {D: poly_fit(xs, ys, [v * pow(y, -1, p) % p for v, y in zip(D10, ys)], p, D, rr) for D in (4, 8, 12, 20)}
    out['polyfit_Delta_times_y'] = {D: poly_fit(xs, ys, [v * y % p for v, y in zip(D10, ys)], p, D, rr) for D in (4, 8, 12, 20)}
    # (iii) correlation of Delta with k mod m (ANOVA F, analytic chi2) and a Delta*k linear-trend check: is Delta(kP) = c1*k + c2 on a window?
    from t2_cocycle import chi2_sf
    ks_ = np.arange(1, N); v = np.array(D10, dtype=float); an = {}
    for mm in (2, 3, 4, 5, 7, 8, 16):
        g = [v[(ks_ % mm) == j] for j in range(mm)]; grand = v.mean()
        F = (sum(len(x) * (x.mean() - grand) ** 2 for x in g) / (mm - 1)) / (sum(((x - x.mean()) ** 2).sum() for x in g) / (n - mm))
        an[mm] = round(chi2_sf((mm - 1) * F, mm - 1), 4)
    out['anova_p_DeltaA'] = an
    # (iv) rank over F_p of the functions {1, k, g_L (all 8 lifts)} on the orbit
    rows = [[1] * n, [k % p for k in range(1, N)]] + [G[l][1:] for l in lifts]
    out['rank_1_k_g_lifts'] = rank_mod(rows, p); out['n_functions'] = len(rows)
    rows2 = [[1] * n, [k % p for k in range(1, N)]] + [d(l) for l in lifts[1:]]
    out['rank_1_k_deltas'] = rank_mod(rows2, p); out['n_functions_deltas'] = len(rows2)
    # BM of Delta
    from t3_section_digit import bm
    out['BM_Delta'] = (bm(D10[:1500], p), min(n, 1500) // 2)
    print(json.dumps(out), flush=True)

def rank_mod(rows, p):
    mat = [r[:] for r in rows]; r = 0; nc = len(mat[0])
    for c in range(nc):
        pr = next((i for i in range(r, len(mat)) if mat[i][c] % p), None)
        if pr is None: continue
        mat[r], mat[pr] = mat[pr], mat[r]; inv = pow(mat[r][c], -1, p); mat[r] = [v * inv % p for v in mat[r]]
        for i in range(r + 1, len(mat)):
            if mat[i][c] % p:
                f = mat[i][c]; mat[i] = [(x - f * y) % p for x, y in zip(mat[i], mat[r])]
        r += 1
        if r == len(mat): break
    return r

if __name__ == '__main__': run(int(sys.argv[1]), int(sys.argv[2]))
