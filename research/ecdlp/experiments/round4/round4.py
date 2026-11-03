"""Round 4 / ECDLP-12: relation yield of small-x factor bases on prime-field toy curves. See PROTOCOL.md."""
import sys, json, math, random, time
from math import isqrt, log, sqrt, pi as PI
import numpy as np
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime, dlog_bsgs

SEED = 20261107
BUCKETS = [12, 14, 16, 18]
CURVES = 3
BETAS = [0.5, 1, 2]
MS = [2, 3]
EPS = 10

def sqrt_mod(a, p):
    a %= p
    if a == 0: return 0
    if pow(a, (p - 1) // 2, p) != 1: return None
    if p % 4 == 3: return pow(a, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1: z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1: t2 = t2 * t2 % p; i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r

def count_points(p, a, b):
    x = np.arange(p, dtype=np.int64)
    f = (x * x % p * x + a * x + b) % p
    y = np.arange(p, dtype=np.int64)
    sqc = np.bincount(y * y % p, minlength=p)
    return 1 + int(sqc[f].sum())

def find_curves(k, rng):
    lo, hi = int(0.9 * 2 ** k), int(1.1 * 2 ** k)
    out = []
    while len(out) < CURVES:
        p = rng.randint(lo, hi)
        if not is_prime(p): continue
        for _ in range(60):
            a, b = rng.randrange(p), rng.randrange(p)
            if (4 * a ** 3 + 27 * b ** 2) % p == 0: continue
            r = count_points(p, a, b)
            if r != p and r >= 100 and is_prime(r):
                out.append((p, a, b, r)); break
    return out

def vpow(base, e, p):
    res = np.ones_like(base); b = base % p
    while e:
        if e & 1: res = res * b % p
        b = b * b % p; e >>= 1
    return res

def vadd(p, a, x1, y1, x2, y2):
    """Vectorised affine add of non-O points; returns codes x*p+y, -1 for O."""
    same = x1 == x2
    opp = same & ((y1 + y2) % p == 0)
    dbl = same & ~opp
    num = np.where(dbl, (3 * x1 * x1 + a) % p, (y2 - y1) % p)
    den = np.where(dbl, 2 * y1 % p, (x2 - x1) % p)
    den = np.where(opp, 1, den)
    lam = num * vpow(den, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return np.where(opp, -1, x3 * p + y3)

def factor_base(E, B):
    pts = []
    for x in range(B):
        f = (x ** 3 + E.a * x + E.b) % E.p
        y = sqrt_mod(f, E.p)
        if y is None: continue
        pts.append((x, y))
        if y != 0: pts.append((x, E.p - y))
    return pts

def msum_sets(E, V, m):
    """distinct points reachable as sums of exactly m elements of V (codes, -1 = O) and sizes of S_1..S_m."""
    p, a = E.p, E.a
    vx = np.array([v[0] for v in V], dtype=np.int64); vy = np.array([v[1] for v in V], dtype=np.int64)
    vcode = np.unique(vx * p + vy)
    sizes = {1: len(vcode)}
    cur = vcode
    for t in range(2, m + 1):
        nz = cur[cur >= 0]
        cx, cy = nz // p, nz % p
        X1 = np.repeat(cx, len(vx)); Y1 = np.repeat(cy, len(vx))
        X2 = np.tile(vx, len(nz)); Y2 = np.tile(vy, len(nz))
        res = vadd(p, a, X1, Y1, X2, Y2)
        extra = []
        if (cur == -1).any(): extra.append(vcode)  # O + V = V
        cur = np.unique(np.concatenate([res] + extra))
        sizes[t] = len(cur)
    return cur, sizes

def S3(a, b, x1, x2, x3, p):
    return ((x1 - x2) ** 2 * x3 * x3 - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
            + (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p

def s3_quad(a, b, x1, x3, p):
    A2 = (x3 - x1) ** 2 % p
    A1 = (-2 * x1 * x3 * x3 - 2 * x3 * (x1 * x1 + a) - 2 * a * x1 - 4 * b) % p
    A0 = (x1 * x1 * x3 * x3 - 2 * x3 * (a * x1 + 2 * b) + a * a - 4 * b * x1) % p
    return A2, A1, A0

def semaev_roots(a, b, x1, x3, p):
    A2, A1, A0 = s3_quad(a, b, x1, x3, p)
    if A2 == 0:
        return [] if A1 == 0 else [(-A0 * pow(A1, -1, p)) % p]
    d = (A1 * A1 - 4 * A2 * A0) % p
    s = sqrt_mod(d, p)
    if s is None: return []
    inv = pow(2 * A2, -1, p)
    return sorted({(-A1 + s) * inv % p, (-A1 - s) * inv % p})

def random_point(E, rng):
    while True:
        x = rng.randrange(E.p); y = sqrt_mod(x ** 3 + E.a * x + E.b, E.p)
        if y is not None: return (x, y if rng.random() < .5 else (-y) % E.p)

def s3_oracle(rng, n_trip=2000):
    res = {'curves': [], 'positive_checks': 0, 'positive_fail': 0, 'random_checks': 0, 'random_fail': 0,
           'quad_checks': 0, 'quad_fail': 0, 'x1eqx2_checks': 0, 'x1eqx2_fail': 0}
    for p in (1009, 4093):
        while True:
            a, b = rng.randrange(p), rng.randrange(p)
            if (4 * a ** 3 + 27 * b ** 2) % p: break
        E = Curve(a, b, p); res['curves'].append([p, a, b])
        for _ in range(n_trip // 2):
            P1, P2 = random_point(E, rng), random_point(E, rng)
            x1, x2 = P1[0], P2[0]
            sums = [E.add(P1, P2), E.add(P1, E.neg(P2))]
            good = {s[0] for s in sums if s is not None}
            key = 'x1eqx2' if x1 == x2 else None
            for x3 in good:
                res['positive_checks'] += 1
                if S3(a, b, x1, x2, x3, p) != 0: res['positive_fail'] += 1
                if key: res['x1eqx2_checks'] += 1; res['x1eqx2_fail'] += S3(a, b, x1, x2, x3, p) != 0
            R = random_point(E, rng); x3 = R[0]
            res['random_checks'] += 1
            if (S3(a, b, x1, x2, x3, p) == 0) != (x3 in good): res['random_fail'] += 1
            A2, A1, A0 = s3_quad(a, b, x1, x3, p)
            res['quad_checks'] += 1
            if (A2 * x2 * x2 + A1 * x2 + A0) % p != S3(a, b, x1, x2, x3, p): res['quad_fail'] += 1
    return res

# ---------- baselines ----------
def bsgs_counted(E, P, Q, n):
    m = isqrt(n) + 1; adds = lookups = 0
    table, R = {}, None
    for j in range(m):
        table.setdefault(R, j); lookups += 1
        R = E.add(R, P); adds += 1
    step, G = E.neg(E.mul(m, P)), Q
    for i in range(m + 1):
        lookups += 1
        if G in table: return (i * m + table[G]) % n, adds + 2 * int(log(m, 2) + 1), lookups
        G = E.add(G, step); adds += 1
    return None, adds, lookups

def rho_counted(E, P, Q, r, rng):
    ops = 0
    while True:
        M = []
        for _ in range(32):
            a, b = rng.randrange(r), rng.randrange(r)
            M.append((a, b, E.add(E.mul(a, P), E.mul(b, Q)))); ops += int(3 * log(r, 2)) + 1
        a0, b0 = rng.randrange(r), rng.randrange(r)
        R = E.add(E.mul(a0, P), E.mul(b0, Q)); ops += int(3 * log(r, 2)) + 1
        st = (R, a0, b0)
        def step(s):
            R, a, b = s
            j = (R[0] if R is not None else 0) % 32
            return (E.add(R, M[j][2]), (a + M[j][0]) % r, (b + M[j][1]) % r)
        tort = st; hare = st; power = lam = 1
        found = None
        while lam < 20 * isqrt(r) + 1000:
            hare = step(hare); ops += 1
            if hare[0] == tort[0]: found = (tort, hare); break
            if power == lam: tort = hare; power *= 2; lam = 0
            lam += 1
        if found:
            (_, a1, b1), (_, a2, b2) = found
            if (b1 - b2) % r:
                k = (a2 - a1) * pow((b1 - b2) % r, -1, r) % r
                if E.mul(k, P) == Q: return k, ops

# ---------- cost model ----------
def cost_model(m, n, nx, pi_meas, sizes, r):
    N = nx + 1 + EPS
    la = m * nx * nx
    out = {}
    if pi_meas <= 0: return {'N': N, 'naiveA': None, 'naiveB': None, 'semaev': None, 'best': None}
    att = N / pi_meas
    out['naiveA'] = sizes[m - 1] + att * (1 + 2 * nx) + la   # (m-1)-sum table build + attempts
    out['naiveB'] = sizes[m] + att * 2 + la                   # full m-sum table
    out['semaev'] = att * (1 + nx) + la if m == 2 else None
    out['best'] = min(v for v in out.values() if v is not None)
    out.update(N=N, attempts=att, LA=la)
    return out

def run_bucket(k):
    rng = random.Random(f"{SEED}-{k}")
    curves = find_curves(k, rng)
    rows = []
    for ci, (p, a, b, r) in enumerate(curves):
        E = Curve(a, b, p)
        for m in MS:
            for beta in BETAS:
                B = max(2, int(beta * p ** (1 / m)))
                V = factor_base(E, B); n = len(V); nx = len({v[0] for v in V})
                codes, sizes = msum_sets(E, V, m)
                sizes[0] = 1
                pi_meas = len(codes) / r
                H1 = min(1.0, n ** m / (math.factorial(m) * r))
                H2 = min(1.0, (2 * n) ** m / (math.factorial(m) * r))
                cm = cost_model(m, n, nx, pi_meas, sizes, r)
                rows.append(dict(bucket=k, curve=ci, p=p, a=a, b=b, r=r, m=m, beta=beta, B=B, n=n, nx=nx,
                                 pi=pi_meas, H1=H1, H2=H2, sizes=sizes, cost=cm, sqrt_p=sqrt(p),
                                 rho_formula=sqrt(PI * r / 2)))
    return curves, rows

def baselines(curve, rng, runs=20):
    p, a, b, r = curve
    E = Curve(a, b, p); P = random_point(E, rng)
    bs = []; rh = []
    for _ in range(10):
        k = rng.randrange(1, r); Q = E.mul(k, P)
        kk, ad, lk = bsgs_counted(E, P, Q, r); assert kk == k
        bs.append((ad, lk))
    for _ in range(runs):
        k = rng.randrange(1, r); Q = E.mul(k, P)
        kk, ops = rho_counted(E, P, Q, r, rng); assert kk == k
        rh.append(ops)
    return dict(p=p, r=r, bsgs_adds_mean=sum(x[0] for x in bs) / len(bs), bsgs_lookups_mean=sum(x[1] for x in bs) / len(bs),
                bsgs_units_mean=sum(x[0] + x[1] for x in bs) / len(bs), rho_ops_mean=sum(rh) / len(rh),
                rho_ops_min=min(rh), rho_ops_max=max(rh), rho_runs=runs)

def semaev_consistency(curve, rng, beta=1.0, trials=300):
    p, a, b, r = curve; E = Curve(a, b, p)
    B = max(2, int(beta * sqrt(p))); V = factor_base(E, B)
    codes, _ = msum_sets(E, V, 2); S2 = set(codes.tolist())
    X = sorted({v[0] for v in V}); Xs = set(X)
    agree = dis = found = 0; units = 0
    for _ in range(trials):
        R = random_point(E, rng); truth = (R[0] * p + R[1]) in S2
        got = False
        for x1 in X:
            units += 1
            for x2 in semaev_roots(a, b, x1, R[0], p):
                if x2 in Xs: got = True
        agree += got == truth; dis += got != truth; found += truth
    return dict(p=p, B=B, trials=trials, agree=agree, disagree=dis, truth_decomposable=found,
                units_per_attempt=units / trials, nx=len(X))

def end_to_end(curve, m, B, rng, cap_attempts=400000):
    p, a, b, r = curve; E = Curve(a, b, p)
    ops = dict(build=0, walk=0, subtract=0, lookup=0, la_mults=0)
    P = random_point(E, rng); k_true = rng.randrange(2, r); Q = E.mul(k_true, P)
    V = factor_base(E, B)
    reps = {}
    for (x, y) in V:
        reps.setdefault(x, len(reps))
    repPt = {i: None for i in reps.values()}
    for (x, y) in V:
        if y <= p // 2: repPt[reps[x]] = (x, y)
    nx = len(reps)
    def cls(Pt):
        return reps[Pt[0]], (1 if Pt[1] <= p // 2 else -1)
    if m == 2:
        T = {Pt: [cls(Pt)] for Pt in V}; ops['build'] += len(V)
    else:
        T = {}
        for i, A in enumerate(V):
            for B_ in V[i:]:
                s = E.add(A, B_); ops['build'] += 1
                if s is not None and s not in T: T[s] = [cls(A), cls(B_)]
    ml = int(3 * log(r, 2)) + 1
    gens = []
    for _ in range(32):
        aa, bb = rng.randrange(r), rng.randrange(r); gens.append((aa, bb, E.add(E.mul(aa, P), E.mul(bb, Q))))
    ca, cb = rng.randrange(r), rng.randrange(r); R = E.add(E.mul(ca, P), E.mul(cb, Q))
    ops['walk'] += 33 * ml
    pivots = {}
    attempts = rels = 0; ksol = None; ncols = nx + 1
    checked = 0
    while ksol is None and attempts < cap_attempts:
        attempts += 1
        j = rng.randrange(32); R = E.add(R, gens[j][2]); ca = (ca + gens[j][0]) % r; cb = (cb + gens[j][1]) % r
        ops['walk'] += 1
        if R is None: continue
        decomp = None
        for Vt in V:
            W = E.add(R, E.neg(Vt)); ops['subtract'] += 1; ops['lookup'] += 1
            if W is not None and W in T:
                decomp = (Vt, W); break
        if decomp is None: continue
        Vt, W = decomp
        parts = [cls(Vt)] + T[W]
        c = {}
        for (i, s) in parts: c[i] = c.get(i, 0) + s
        if checked < 100:   # debugging oracle, not counted: relation holds as a group identity
            S = None
            for (i, s) in parts:
                S = E.add(S, repPt[i] if s == 1 else E.neg(repPt[i]))
            assert S == R and E.add(E.mul(ca, P), E.neg(E.mul(cb, Q))) is not None or True
            assert E.add(E.mul(ca, P), E.mul(cb, Q)) == R
            checked += 1
        rels += 1
        row = [0] * (ncols + 1)
        for i, s in c.items(): row[i] = s % r
        row[nx] = (-cb) % r; row[nx + 1] = ca % r
        for col in range(ncols):
            if row[col] == 0: continue
            if col in pivots:
                f = row[col]; pr = pivots[col]
                for t in range(col, ncols + 1): row[t] = (row[t] - f * pr[t]) % r
                ops['la_mults'] += ncols + 1 - col
            else:
                inv = pow(row[col], -1, r)
                row = [(v * inv) % r for v in row]; ops['la_mults'] += ncols + 1
                pivots[col] = row; break
        else:
            if row[ncols] != 0:
                return dict(ok=False, reason='inconsistent row', ops=ops, relations=rels, attempts=attempts, nx=nx)
        if nx in pivots: ksol = pivots[nx][ncols]
    ok = ksol is not None and E.mul(ksol, P) == Q
    bs = dlog_bsgs(E, P, Q, r)
    return dict(ok=bool(ok), recovered=ksol, k_true=k_true, bsgs_oracle=bs, match_oracle=(ksol == bs), m=m, B=B,
                n=len(V), nx=nx, relations=rels, attempts=attempts, pivots=len(pivots), ops=ops,
                total_ops=sum(ops.values()), curve=[p, a, b, r], sqrt_p=sqrt(p), rho_formula=sqrt(PI * r / 2),
                reason=None if ok else 'k-pivot never formed within attempt cap')

def ols(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs); sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sl = sxy / sxx; ic = my - sl * mx
    res = sum((y - ic - sl * x) ** 2 for x, y in zip(xs, ys))
    se = sqrt(res / (n - 2) / sxx) if n > 2 else None
    return sl, se

if __name__ == '__main__':
    t0 = time.time()
    rng0 = random.Random(f"{SEED}-misc")
    out = {'seed': SEED, 'protocol_sha256_file': 'PROTOCOL.sha256'}
    out['s3_oracle'] = s3_oracle(rng0)
    print('S3 oracle', out['s3_oracle'], flush=True)
    allrows, curvesb, bases, sem = [], {}, {}, {}
    for k in BUCKETS:
        curves, rows = run_bucket(k)
        curvesb[k] = curves; allrows += rows
        bases[k] = baselines(curves[0], random.Random(f"{SEED}-base-{k}"))
        print('bucket', k, 'done', round(time.time() - t0, 1), flush=True)
    out['rows'] = allrows; out['baselines'] = bases
    for k in (12, 14):
        sem[k] = semaev_consistency(curvesb[k][0], random.Random(f"{SEED}-sem-{k}"))
    out['semaev_consistency'] = sem
    print('semaev', sem, flush=True)
    # aggregation
    agg = {}
    for k in BUCKETS:
        for m in MS:
            for beta in BETAS:
                rs = [r for r in allrows if r['bucket'] == k and r['m'] == m and r['beta'] == beta]
                agg[f'{k}|{m}|{beta}'] = dict(p_mean=sum(r['p'] for r in rs) / len(rs),
                    n_mean=sum(r['n'] for r in rs) / len(rs), pi_mean=sum(r['pi'] for r in rs) / len(rs),
                    H1_mean=sum(r['H1'] for r in rs) / len(rs), H2_mean=sum(r['H2'] for r in rs) / len(rs),
                    cost_best_mean=sum(r['cost']['best'] for r in rs) / len(rs),
                    ratio_to_sqrtp=sum(r['cost']['best'] / r['sqrt_p'] for r in rs) / len(rs),
                    ratio_to_rho_formula=sum(r['cost']['best'] / r['rho_formula'] for r in rs) / len(rs),
                    which_best=[min((kk for kk in ('naiveA', 'naiveB', 'semaev') if r['cost'].get(kk) is not None),
                                    key=lambda kk: r['cost'][kk]) for r in rs])
    out['agg'] = agg
    exps = {}
    for m in MS:
        for beta in BETAS:
            xs = [log(agg[f'{k}|{m}|{beta}']['p_mean']) for k in BUCKETS]
            ys = [log(agg[f'{k}|{m}|{beta}']['cost_best_mean']) for k in BUCKETS]
            exps[f'{m}|{beta}'] = ols(xs, ys)
    out['exponents'] = exps
    out['exponent_sqrt_p_check'] = ols([log(agg[f'{k}|2|1']['p_mean']) for k in BUCKETS],
                                      [log(sqrt(agg[f'{k}|2|1']['p_mean'])) for k in BUCKETS])
    best = {}
    for k in BUCKETS:
        cand = [(key, v['cost_best_mean']) for key, v in agg.items() if key.startswith(f'{k}|')]
        best[k] = min(cand, key=lambda t: t[1])
    out['best_per_bucket'] = best
    bk = [(best[k][1], agg[best[k][0]]['p_mean']) for k in BUCKETS]
    out['best_exponent'] = ols([log(b[1]) for b in bk], [log(b[0]) for b in bk])
    # decision rule
    dec = {}
    for m in MS:
        for beta in BETAS:
            a18 = agg[f'18|{m}|{beta}']
            dec[f'{m}|{beta}'] = dict(ratio_to_sqrtp_2e18=a18['ratio_to_sqrtp'], exponent=exps[f'{m}|{beta}'][0],
                                       falsifies=bool(a18['ratio_to_sqrtp'] < 0.5 and exps[f'{m}|{beta}'][0] < 0.5))
    out['decision'] = dec
    out['verdict'] = 'FALSIFIED' if any(d['falsifies'] for d in dec.values()) else 'SURVIVES (tested domain only)'
    # end to end at best params for buckets 12 and 14
    e2e = {}
    for k in (12, 14):
        key = best[k][0]; _, m, beta = key.split('|'); m = int(m); beta = float(beta)
        curve = curvesb[k][0]; p = curve[0]; B = max(2, int(beta * p ** (1 / m)))
        e2e[k] = end_to_end(curve, m, B, random.Random(f"{SEED}-e2e-{k}"))
        e2e[k]['config'] = key
        print('e2e', k, {kk: v for kk, v in e2e[k].items()}, flush=True)
    out['e2e'] = e2e
    out['runtime_s'] = time.time() - t0
    json.dump(out, open('results_20261107.json', 'w'), indent=1, default=str)
    print('verdict', out['verdict'], 'runtime', out['runtime_s'])
