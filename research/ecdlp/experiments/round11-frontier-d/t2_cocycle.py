"""T2 (round 11): explicit cocycle of the homomorphic Hensel section and its p^3 digit; structure tests along k.
Usage: python3 t2_cocycle.py P0 SEED [FULL_U3(0/1)]   (writes JSON summary lines to stdout)"""
import sys, random, json, time
import numpy as np, math
sys.path.insert(0, '../round10-frontier-a'); sys.path.insert(0, '../lib')
from t3_section_digit import rcb_add, mul, bm, holonomic
from toyec import Curve, is_prime

def lift_point_e(x, y0, A, B, M, p):
    y = y0
    for _ in range(4):
        f = (pow(x, 3, M) + A * x + B) % M
        y = (y - (y * y - f) * pow(2 * y, -1, M)) % M
    assert (y * y - (pow(x, 3, M) + A * x + B)) % M == 0 and y % p == y0
    return (x, y, 1)

def sqrt_mod(a, p):  # brute/Tonelli-light for small p
    if p % 4 == 3: return pow(a, (p + 1) // 4, p)
    return next(y for y in range(p) if y * y % p == a)

def chi2_sf(x, d):
    a = d / 2.0; x = x / 2.0
    if x <= 0: return 1.0
    term = 1.0 / a; tot = term; n = 0
    while term > 1e-14 * tot and n < 5000:
        n += 1; term *= x / (a + n); tot += term
    lp = a * math.log(x) - x - math.lgamma(a) + math.log(tot)
    return max(0.0, 1.0 - math.exp(lp))

def poly_fit(xs, ys, tv, p, D, rng):
    """is target tv (on points) a polynomial sum c_ij x^i y^j (i<=D, j<=1)? exact solve on 2*unk random rows, validate on all."""
    unk = 2 * (D + 1); n = len(xs)
    def row(i): return [pow(xs[i], a, p) * (ys[i] if b else 1) % p for a in range(D + 1) for b in range(2)]
    idx = rng.sample(range(n), min(n, 3 * unk + 10))
    mat = [row(i) + [tv[i] % p] for i in idx]
    r = 0
    for c in range(unk):
        pr = next((i for i in range(r, len(mat)) if mat[i][c]), None)
        if pr is None: continue
        mat[r], mat[pr] = mat[pr], mat[r]; inv = pow(mat[r][c], -1, p); mat[r] = [v * inv % p for v in mat[r]]
        for i in range(len(mat)):
            if i != r and mat[i][c]:
                f = mat[i][c]; mat[i] = [(a - f * b) % p for a, b in zip(mat[i], mat[r])]
        r += 1
    if any(mat[i][unk] for i in range(r, len(mat))): return False   # inconsistent on training rows
    sol = [0] * unk
    for i in range(r):
        c = next(j for j in range(unk) if mat[i][j]); sol[c] = mat[i][unk]
    return all(sum(a * b for a, b in zip(row(i), sol)) % p == tv[i] % p for i in range(n))

def setup(p0, seed):
    rnd = random.Random(seed); p = p0
    while True:
        p += 1
        if not is_prime(p) or p % 4 != 3: continue
        for _ in range(80):
            a = rnd.randrange(1, p); b = rnd.randrange(1, p)
            try: E = Curve(a, b, p)
            except ValueError: continue
            N = E.order()
            if is_prime(N) and N != p and N > 100: return rnd, p, a, b, E, N

def main(p0, seed, full_u3):
    rnd, p, a, b, E, N = setup(p0, seed)
    M = p ** 3
    A = (a + p * rnd.randrange(p) + p * p * rnd.randrange(p)) % M; B = (b + p * rnd.randrange(p) + p * p * rnd.randrange(p)) % M
    b3 = 3 * B % M
    while True:
        x = rnd.randrange(p); rhs = (x ** 3 + a * x + b) % p
        if rhs and pow(rhs, (p - 1) // 2, p) == 1: P = (x, sqrt_mod(rhs, p)); break
    # orbit
    pts = [None, P]; R = P
    for k in range(2, N + 1):
        R = E.add(R, P); pts.append(R)
    assert pts[N] is None and pts[N - 1][0] == P[0]
    O = (0, 1, 0)
    L = [O] + [lift_point_e(pt[0], pt[1], A, B, M, p) for pt in pts[1:N]] + [O]     # L[k] lift of kP, k=0..N
    def neg(S): return (S[0], (-S[1]) % M, S[2])
    def zval(S):
        X, Y, Z = S; assert X % p == 0 and Z % p == 0 and Y % p != 0, "not in E_1"
        return (-X * pow(Y, -1, M)) % M
    LP = L[1]; d1 = [0] * (N + 1); d2 = [0] * (N + 1); c3 = [0] * (N + 1)
    for k in range(0, N):
        c = rcb_add(rcb_add(L[k], LP, A, b3, M), neg(L[(k + 1) % (N + 1)] if k + 1 < N else O), A, b3, M)
        z = zval(c); assert z % p == 0
        c3[k] = z // p; d1[k] = c3[k] % p; d2[k] = (c3[k] // p) % p
    # direct g at precision 3: g3 = z([N] l)/p mod p^2
    def g3_direct(Sx): return zval(mul(N, Sx, A, b3, M)) // p % (p * p)
    gP = g3_direct(LP)
    S1 = [0] * (N + 1); S3 = [0] * (N + 1)      # S_k = sum_{i<k} c3(i) mod p^2  (S1 = mod p)
    for k in range(1, N + 1): S3[k] = (S3[k - 1] + c3[k - 1]) % (p * p)
    g3 = [(k * gP - N * S3[k]) % (p * p) for k in range(N + 1)]
    out = dict(p=p, a=a, b=b, N=N, seed=seed, checks={})
    out['checks']['S_N_equals_gP'] = (S3[N] - gP * pow(N, -1, p * p) * N % (p * p) * 0) % (p * p) == S3[N] and ((N * S3[N] - N * gP) % (p * p) == 0)
    samp = rnd.sample(range(1, N), min(N - 1, 300))
    out['checks']['g_direct_matches_formula_p2'] = all(g3_direct(L[k]) % (p * p) == g3[k] for k in samp[:60])
    # section digits (sampled direct, then formula)
    m1 = pow(p, -1, N); m2 = pow(p * p, -1, N)
    def xs_digits(S, mm, pw):
        s = mul(pw * mm, S, A, b3, M); X, Y, Z = s; assert Z % p
        xx = X * pow(Z, -1, M) % M; return xx, s
    u2d = {}; u3d = {}
    ks = list(range(1, N)) if full_u3 else samp[:120]
    for k in ks:
        xx, _ = xs_digits(L[k], m1, p)
        xx2, _ = xs_digits(L[k], m2, p * p)   # p^2-multiplier section at precision p^3 (digit 2 of its x)
        assert xx % p == pts[k][0] and xx2 % p == pts[k][0]
        u2d[k] = (xx // p) % p; u3d[k] = (xx2 // p ** 2) % p
        # NOTE u2 from the p-multiplier section (mod p^2 is enough); u3 from p^2-multiplier section digit 2.
    # fit lambda: u2 = lam * y * g (g mod p) ; y = y of the lift reduced mod p
    kk0 = next(k for k in samp if g3[k] % p and pts[k][1])
    lam = u2d[kk0] * pow(pts[kk0][1] * (g3[kk0] % p), -1, p) % p
    out['checks']['u2_equals_lam_y_g'] = all(u2d[k] == lam * pts[k][1] * (g3[k] % p) % p for k in ks)
    out['lambda'] = lam; out['lambda_times_N_mod_p'] = lam * N % p
    # sequences k=1..N-1
    n = N - 1
    seq = {'d1': d1[1:N], 'd2': d2[1:N], 'S': [s % p for s in S3[1:N]], 'g': [v % p for v in g3[1:N]],
           'u2': [lam * pts[k][1] * (g3[k] % p) % p for k in range(1, N)]}
    if full_u3: seq['u3'] = [u3d[k] for k in range(1, N)]
    rng = np.random.default_rng(5); rr = random.Random(5)
    ctrl = {'random': [rr.randrange(p) for _ in range(n)], 'shuf_d1': rr.sample(seq['d1'], n),
            'pos_lin': [(3 * k + 5) % p for k in range(1, N)], 'pos_kgk': [k * pow(7, k, p) % p for k in range(1, N)]}
    allseq = {**seq, **ctrl}
    BMN = min(n, 2500)
    res = {}
    for name, s in allseq.items():
        L_ = bm(s[:BMN], p)
        h = holonomic(s, p, 3, 3) if n > 120 else None
        h4 = holonomic(s, p, 4, 4)
        v = np.array(s, dtype=float)
        # ANOVA vs k mod m with permutation null
        an = {}
        ks_ = np.arange(1, N)
        for mm in (2, 3, 4, 5, 7, 8, 16):
            def F(vv):
                g = [vv[(ks_ % mm) == j] for j in range(mm)]
                grand = vv.mean(); ssb = sum(len(x) * (x.mean() - grand) ** 2 for x in g); ssw = sum(((x - x.mean()) ** 2).sum() for x in g)
                return (ssb / (mm - 1)) / (ssw / (len(vv) - mm))
            f0 = F(v); nul = [F(rng.permutation(v)) for _ in range(120)]
            an[mm] = (round(f0, 3), round(chi2_sf((mm - 1) * f0, mm - 1), 6), round(float((1 + sum(x >= f0 for x in nul)) / 121), 3))
        z = np.exp(2j * np.pi * v / p); mx = lambda zz: np.abs(np.fft.fft(zz))[1:].max() / np.sqrt(n)
        s0 = mx(z); nl = [mx(rng.permutation(z)) for _ in range(40)]
        spec = round(float((s0 - np.mean(nl)) / np.std(nl)), 2)
        res[name] = dict(BM_L=L_, BM_expect=BMN // 2, holo3=h, holo4=h4, anova_F_and_perm_p=an, spectral_z=spec)
    out['seq'] = res
    # low-degree polynomial representability in (x,y)
    xs = [pts[k][0] for k in range(1, N)]; ys = [pts[k][1] for k in range(1, N)]
    out['polyfit'] = {}
    for D in (4, 8, 12):
        tg = {'pos_ctrl': [(x ** 3 + y * x) % p for x, y in zip(xs, ys)], 'rand': ctrl['random'], 'd1': seq['d1'], 'd2': seq['d2'], 'g': seq['g'], 'S': seq['S']}
        out['polyfit'][D] = {k: poly_fit(xs, ys, v, p, D, rr) for k, v in tg.items()}
    print(json.dumps(out), flush=True)

if __name__ == '__main__':
    t0 = time.time(); main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 0)
    print('elapsed', round(time.time() - t0, 1), file=sys.stderr)
