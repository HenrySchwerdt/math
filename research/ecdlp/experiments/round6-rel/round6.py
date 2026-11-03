"""Round 6 / ECDLP-16 experiment driver (m=3 relation finding). See PROTOCOL.md (pre-registered).
Usage: round6.py verify | run K | m2 K | sweep | e2e | summarize
Counted field operations; Python reference only. Toy sizes."""
import sys, os, json, random, math, time, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from toyec import Curve, dlog_bsgs, is_prime

SEED = 20261108
def rng(tag): return random.Random(f"{SEED}-{tag}")
INF = 'INF'

# ---------------------------------------------------------------- Semaev polynomials
def s3(x1, x2, a, b, p):
    s = x1 + x2; m = x1 * x2
    return ((x1 - x2) ** 2 % p, (-2 * (s * (m + a) + 2 * b)) % p, ((m - a) ** 2 - 4 * b * s) % p)  # (c2,c1,c0) in X

def res2(A, B, p):
    A2, A1, A0 = A; B2, B1, B0 = B
    return ((A2 * B0 - A0 * B2) ** 2 - (A2 * B1 - A1 * B2) * (A1 * B0 - A0 * B1)) % p

def S3(x1, x2, x3, a, b, p):
    c2, c1, c0 = s3(x1, x2, a, b, p)
    return (c2 * x3 * x3 + c1 * x3 + c0) % p

def S4(x1, x2, x3, x4, a, b, p):
    return res2(s3(x1, x2, a, b, p), s3(x3, x4, a, b, p), p)

def rand_curve(r, p):
    while True:
        a, b = r.randrange(p), r.randrange(p)
        if (4 * a ** 3 + 27 * b ** 2) % p:
            return Curve(a, b, p)

def affine_pt(E, r, pts):
    while True:
        P = r.choice(pts)
        if P is not None:
            return P

# ---------------------------------------------------------------- Step 1: oracle
def verify():
    out = {'seed': SEED, 'checks': {}}
    tot3 = tot4 = 0
    for p in (4001, 15791, 65537, 1000003):
        r = rng(f"verify-{p}")
        E = rand_curve(r, p); pts = E.points(); a, b = E.a, E.b
        bad3 = bad4 = n3 = n4 = 0
        while n3 < 600:
            P1, P2 = affine_pt(E, r, pts), affine_pt(E, r, pts)
            Q = E.add(P1, P2)
            if Q is None: continue
            n3 += 1
            if S3(P1[0], P2[0], Q[0], a, b, p): bad3 += 1
        while n4 < 600:
            P1, P2, P3 = (affine_pt(E, r, pts) for _ in range(3))
            Q = E.add(E.add(P1, P2), P3)
            if Q is None: continue
            P4 = E.neg(Q); n4 += 1
            if S4(P1[0], P2[0], P3[0], P4[0], a, b, p): bad4 += 1
        out['checks'][f'p{p}'] = dict(a=a, b=b, order=len(pts), S3_tuples=n3, S3_bad=bad3, S4_tuples=n4, S4_bad=bad4)
        tot3 += n3; tot4 += n4
        assert bad3 == 0 and bad4 == 0, out
    out['total_S3_tuples'] = tot3; out['total_S4_tuples'] = tot4
    # (iii) completeness + (iv) negative control at p=4001
    p = 4001; r = rng("verify-complete"); E = rand_curve(r, p); pts = E.points(); a, b = E.a, E.b
    eq = ne = 0; reasons = {}; negctl = negbad = 0
    for _ in range(300):
        P = [affine_pt(E, r, pts) for _ in range(3)]
        exp = set(); degenerate = False
        for s in itertools.product((1, -1), repeat=3):
            Q = None
            for si, Pi in zip(s, P): Q = E.add(Q, Pi if si == 1 else E.neg(Pi))
            if Q is None: degenerate = True
            else: exp.add(Q[0])
        A = s3(P[0][0], P[1][0], a, b, p)
        roots = {x for x in range(p) if res2(A, s3(P[2][0], x, a, b, p), p) == 0}
        if roots == exp: eq += 1
        else:
            ne += 1; key = ('degenerate_sum_O' if degenerate else 'repeated_or_other')
            reasons[key] = reasons.get(key, 0) + 1
        for _ in range(7):
            x4 = r.randrange(p)
            if x4 in exp: continue
            negctl += 1
            if S4(P[0][0], P[1][0], P[2][0], x4, a, b, p) == 0: negbad += 1
    out['completeness_p4001'] = dict(tuples=300, root_set_equals_expected=eq, not_equal=ne, reasons=reasons)
    out['negative_control'] = dict(random_x4=negctl, spurious_zero=negbad,
                                   note='random x4 outside expected set with S_4=0: genuinely rare only if roots==expected (see not_equal)')
    assert negbad == 0 or negbad <= ne, out
    return out

# ---------------------------------------------------------------- primes, factor bases
def factorize(n):
    f = {}; d = 2
    while d * d <= n:
        while n % d == 0: f[d] = f.get(d, 0) + 1; n //= d
        d += 1
    if n > 1: f[n] = f.get(n, 0) + 1
    return f

def divisors(n):
    ds = [1]
    for q, e in factorize(n).items(): ds = [d * q ** i for d in ds for i in range(e + 1)]
    return sorted(ds)

def find_prime(k):
    best = None
    for p in range(2 ** k, int(1.03 * 2 ** k)):
        if not is_prime(p): continue
        f = factorize(p - 1)
        if max(f) > 97: continue
        ds = divisors(p - 1); c = p ** (1 / 3)
        hA = min(ds, key=lambda h: abs(math.log(h / c))); hB = min(ds, key=lambda h: abs(math.log(h / (2 * c))))
        score = abs(math.log(hA / c)) + abs(math.log(hB / (2 * c)))
        if best is None or score < best[0]: best = (score, p, hA, hB)
    return best[1], best[2], best[3]

def subgroup_gen(r, p, h):
    pf = list(factorize(h))
    while True:
        w = pow(r.randrange(2, p), (p - 1) // h, p)
        if w != 1 and all(pow(w, h // q, p) != 1 for q in pf): return w

def valid_xs(E):
    """map x -> y (one sign) for affine points with y != 0"""
    p = E.p; sq = {}
    for y in range(1, p): sq.setdefault(y * y % p, y)
    m = {}
    for x in range(p):
        v = (x ** 3 + E.a * x + E.b) % p
        if v in sq: m[x] = sq[v]
    return m

def pkm_xs(r, E, ymap, h):
    p = E.p; w = subgroup_gen(r, p, h); g = r.randrange(1, p)
    xs = []; t = g
    for _ in range(h):
        if t in ymap: xs.append(t)
        t = t * w % p
    return xs, g, w

def build_sets(E, ymap, hA, hB, r):
    sets = {}
    for lab, h in (('A', hA), ('B', hB)):
        xs, g, w = pkm_xs(r, E, ymap, h)
        n = len(xs); allx = sorted(ymap)
        sets['PKM-' + lab] = dict(xs=xs, h=h, g=g)
        sets['SX-' + lab] = dict(xs=allx[:n])
        sets['RND-' + lab] = dict(xs=r.sample(allx, n))
    return sets

# ---------------------------------------------------------------- M1 table method
class Cost:
    def __init__(s): s.M = 0; s.I = 0
    def tot(s, wI=1): return s.M + wI * s.I

def pair_x(x1, y1, x2, y2, p, c):
    """x(P1+P2), x(P1-P2) sharing one inversion: 1I+4M. requires x1 != x2"""
    d = pow(x2 - x1, -1, p); c.I += 1
    l1 = (y2 - y1) * d % p; l2 = (-y2 - y1) * d % p; c.M += 4
    return (l1 * l1 - x1 - x2) % p, (l2 * l2 - x1 - x2) % p

class M1:
    def __init__(s, E, xs, ymap):
        s.E, s.p, s.xs, s.ymap = E, E.p, xs, ymap; s.build = Cost(); p = s.p
        T = {INF: None}; n = len(xs)
        for i in range(n):
            x1 = xs[i]; y1 = ymap[x1]
            # doubling: x(2P); 1I+3M
            lam = (3 * x1 * x1 + E.a) * pow(2 * y1, -1, p) % p; s.build.I += 1; s.build.M += 3
            T.setdefault((lam * lam - 2 * x1) % p, (i, i))
            for j in range(i + 1, n):
                x2 = xs[j]; xa, xb = pair_x(x1, y1, x2, ymap[x2], p, s.build)
                T.setdefault(xa, (i, j)); T.setdefault(xb, (i, j))
        s.T = T
    def attempt(s, R, c):
        """returns (i3, X) on hit else None; counts into c"""
        p = s.p; xr, yr = R
        for k, x3 in enumerate(s.xs):
            if x3 == xr: return (k, INF)
            xa, xb = pair_x(xr, yr, x3, s.ymap[x3], p, c)
            if xa in s.T: return (k, xa)
            if xb in s.T: return (k, xb)
        return None
    def decompose(s, R, hit):
        E = s.E; k, X = hit; y = s.ymap
        P3 = (s.xs[k], y[s.xs[k]])
        if X == INF: return [(P3, 1 if E.add(R, E.neg(P3)) is None else -1)]
        i, j = s.T[X]; P1, P2 = (s.xs[i], y[s.xs[i]]), (s.xs[j], y[s.xs[j]])
        for sg in itertools.product((1, -1), repeat=3):
            Q = None
            for si, Pi in zip(sg, (P1, P2, P3)): Q = E.add(Q, Pi if si == 1 else E.neg(Pi))
            if Q == R: return list(zip((P1, P2, P3), sg))
        return None

def exact_sumset(E, xs, ymap):
    V = []
    for x in xs: V += [(x, ymap[x]), (x, (-ymap[x]) % E.p)]
    A = set()
    for P in V:
        for Q in V: A.add(E.add(P, Q))
    S = set()
    for Q in A:
        for P in V: S.add(E.add(Q, P))
    S.discard(None)
    return S

def eval_set(E, pts, ymap, xs, r, nsamp=200):
    p = E.p; nE = len(pts); n = len(xs)
    S = exact_sumset(E, xs, ymap); pi = len(S) / (nE - 1)
    m1 = M1(E, xs, ymap); c = Cost(); succ = 0; disagree = 0; bad = 0
    for _ in range(nsamp):
        R = affine_pt(E, r, pts)
        hit = m1.attempt(R, c)
        if (hit is not None) != (R in S): disagree += 1
        if hit is not None:
            succ += 1
            if m1.decompose(R, hit) is None: bad += 1
    cm, ci = c.M / nsamp, c.I / nsamp
    d = dict(n=n, pi_exact=pi, M1_sample_success=succ / nsamp, M1_disagree_vs_exact=disagree, M1_decomp_failed=bad,
             attempt_M=cm, attempt_I=ci, table_M=m1.build.M, table_I=m1.build.I)
    for wI in (1, 10):
        att = cm + wI * ci; tab = m1.build.M + wI * m1.build.I
        T = att / pi if pi > 0 else float('inf'); la = 3 * n * n
        d[f'T_w{wI}'] = T; d[f'total_w{wI}'] = tab + (n + 10) * T + la
        d[f'LA_model'] = la
    return d

def run_k(k, curves=None):
    p, hA, hB = find_prime(k); nc = curves or (2 if k == 20 else 4)
    t0 = time.time(); res = dict(k=k, p=p, hA=hA, hB=hB, curves=[])
    rho_cache = []
    for ci in range(nc):
        r = rng(f"run-{k}-{ci}"); E = rand_curve(r, p); pts = E.points(); N = len(pts); ymap = valid_xs(E)
        sets = build_sets(E, ymap, hA, hB, r)
        if k == 20: sets = {k_: v for k_, v in sets.items() if k_.endswith('-B')}
        cr = dict(a=E.a, b=E.b, order=N, rho_units_w1=math.sqrt(math.pi * N / 2) * 4, sets={})
        for name, s in sets.items():
            cr['sets'][name] = eval_set(E, pts, ymap, s['xs'], rng(f"samp-{k}-{ci}-{name}"))
            cr['sets'][name]['_t'] = round(time.time() - t0, 1)
            print(k, ci, name, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in cr['sets'][name].items()}, flush=True)
        res['curves'].append(cr)
    res['runtime_s'] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(HERE, f'results_k{k}.json'), 'w'), indent=1)

# ---------------------------------------------------------------- M2: S_4 pair scan with counted polynomial arithmetic
class PC:
    M = 0; I = 0
def pmul(f, g, p):
    r = [0] * (len(f) + len(g) - 1)
    for i, u in enumerate(f):
        for j, v in enumerate(g): r[i + j] = (r[i + j] + u * v) % p; PC.M += 1
    return r
def psub(f, g, p):
    n = max(len(f), len(g)); f = f + [0] * (n - len(f)); g = g + [0] * (n - len(g))
    return [(u - v) % p for u, v in zip(f, g)]
def ptrim(f):
    while f and f[-1] == 0: f = f[:-1]
    return f
def pscale(c, f, p):
    PC.M += len(f); return [c * u % p for u in f]
def pmod(f, g, p):
    """f mod g, g nonzero (made monic internally); counts"""
    g = ptrim(g); f = ptrim(f[:]); dg = len(g) - 1
    if len(f) - 1 < dg: return f
    inv = pow(g[-1], -1, p); PC.I += 1
    while len(f) - 1 >= dg and f:
        c = f[-1] * inv % p; PC.M += 1
        for i in range(dg + 1): f[len(f) - 1 - dg + i] = (f[len(f) - 1 - dg + i] - c * g[i]) % p; PC.M += 1
        f = ptrim(f)
    return f
def pgcd(f, g, p):
    f, g = ptrim(f), ptrim(g)
    while g: f, g = g, pmod(f, g, p)
    return f
def ppow_x_mod(h, q, p):
    """x^h mod q by left-to-right square and multiply (multiply by x is a shift)"""
    r = [1]
    for bit in bin(h)[2:]:
        r = pmod(pmul(r, r, p), q, p)
        if bit == '1': r = pmod([0] + r, q, p)
    return r

def quartic(x1, x2, xr, a, b, p, Bpoly):
    """q(x3)=S_4(x1,x2,x3,xr) as coefficient list (low->high); counted"""
    x2s = x1 - x2; m = x1 * x2; s = x1 + x2
    A2 = x2s * x2s % p; A1 = (-2 * (m + a) * s - 4 * b) % p; A0 = ((m - a) ** 2 - 4 * b * s) % p; PC.M += 5 + 0
    B2, B1, B0 = Bpoly
    t1 = psub(pscale(A2, B0, p), pscale(A0, B2, p), p)
    t2 = psub(pscale(A2, B1, p), pscale(A1, B2, p), p)
    t3 = psub(pscale(A1, B0, p), pscale(A0, B1, p), p)
    return ptrim(psub(pmul(t1, t1, p), pmul(t2, t3, p), p))

def Bpolys(xr, a, b, p):
    B2 = [xr * xr % p, -2 * xr % p, 1]
    B1 = [(-2 * (a * xr + 2 * b)) % p, (-2 * (a + xr * xr)) % p, (-2 * xr) % p]
    B0 = [(a * a - 4 * b * xr) % p, (-(2 * a * xr + 4 * b)) % p, xr * xr % p]
    PC.M += 8
    return B2, B1, B0

def peval(q, x, p):
    v = 0
    for cf in reversed(q): v = (v * x + cf) % p; PC.M += 1
    return v

def m2_attempt(E, xs, ymap, R, mode, h=None, g=None):
    """mode 'eval' or 'gcd'. returns (hit_triple or None, spurious count, ops_M, ops_I)"""
    p = E.p; a, b = E.a, E.b; PC.M = PC.I = 0; xr = R[0]
    Bp = Bpolys(xr, a, b, p); spur = 0; n = len(xs)
    c = pow(g, h, p) if mode == 'gcd' else None
    for i in range(n):
        for j in range(i, n):
            q = quartic(xs[i], xs[j], xr, E.a, E.b, p, Bp)
            if len(q) < 2: continue  # zero or nonzero constant: no (usable) root
            if mode == 'eval':
                roots = [x for x in xs if peval(q, x, p) == 0]  # (no early exit inside; early exit across pairs below)
            else:
                xh = ppow_x_mod(h, q, p)
                gd = pgcd(q, psub(xh, [c], p), p)
                roots = [x for x in xs if sum(cf * pow(x, e, p) for e, cf in enumerate(q)) % p == 0] if len(gd) > 1 else []  # uncounted verification
            for x3 in roots:
                if verify_triple(E, ymap, xs[i], xs[j], x3, R): return (xs[i], xs[j], x3), spur, PC.M, PC.I
                spur += 1
    return None, spur, PC.M, PC.I

def verify_triple(E, ymap, x1, x2, x3, R):
    Ps = [(x, ymap[x]) for x in (x1, x2, x3) if x in ymap]
    if len(Ps) < 3: return False
    for sg in itertools.product((1, -1), repeat=3):
        Q = None
        for si, Pi in zip(sg, Ps): Q = E.add(Q, Pi if si == 1 else E.neg(Pi))
        if Q == R: return True
    return False

def run_m2(k, nsamp=40, ncurves=2):
    p, hA, hB = find_prime(k); out = dict(k=k, p=p, rows=[])
    for ci in range(ncurves):
        r = rng(f"run-{k}-{ci}"); E = rand_curve(r, p); pts = E.points(); ymap = valid_xs(E)
        sets = build_sets(E, ymap, hA, hB, r)
        for name in ('PKM-B', 'SX-B', 'PKM-A'):
            s = sets[name]; xs = s['xs']; n = len(xs); S = exact_sumset(E, xs, ymap)
            m1 = M1(E, xs, ymap); rs = rng(f"m2-{k}-{ci}-{name}")
            modes = ['eval', 'gcd'] if name.startswith('PKM') else ['eval']
            for mode in modes:
                tot = Cost(); agree = dis = hits = spur = rinv = 0; xs0 = set(xs)
                for _ in range(nsamp):
                    R = affine_pt(E, rs, pts)
                    tri, sp, M, I = m2_attempt(E, xs, ymap, R, mode, s.get('h'), s.get('g'))
                    tot.M += M; tot.I += I; spur += sp
                    if tri is not None: hits += 1
                    if R[0] in xs0: rinv += 1; continue  # R itself in V (trivial/degenerate class): excluded from agreement count
                    if (tri is not None) != (R in S): dis += 1
                pi = len(S) / (len(pts) - 1)
                row = dict(curve=ci, set=name, mode=mode, n=n, attempts=nsamp, hits=hits, R_in_V_excluded=rinv, disagree_vs_exact=dis, spurious_candidates=spur,
                           attempt_M=tot.M / nsamp, attempt_I=tot.I / nsamp, pi_exact=pi,
                           pairs=n * (n + 1) // 2, T_w1=(tot.M / nsamp + tot.I / nsamp) / pi)
                out['rows'].append(row); print(row, flush=True)
    json.dump(out, open(os.path.join(HERE, f'results_m2_k{k}.json'), 'w'), indent=1)

# ---------------------------------------------------------------- sweep of |V| (M1, small-x)
def run_sweep(k=16, curves=2):
    p, hA, hB = find_prime(k); out = dict(k=k, p=p, rows=[]); c0 = p ** (1 / 3)
    for ci in range(curves):
        r = rng(f"sweep-{k}-{ci}"); E = rand_curve(r, p); pts = E.points(); ymap = valid_xs(E); allx = sorted(ymap)
        for cf in (0.5, 0.75, 1.0, 1.5, 2.0):
            n = int(round(cf * c0)); d = eval_set(E, pts, ymap, allx[:n], rng(f"sw-{k}-{ci}-{cf}"), 100)
            d.update(c=cf, curve=ci, sqrtp=math.sqrt(p)); out['rows'].append(d); print(cf, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in d.items()}, flush=True)
    json.dump(out, open(os.path.join(HERE, f'results_sweep_k{k}.json'), 'w'), indent=1)

# ---------------------------------------------------------------- end to end
def solve_mod(rows, rhs, N, ncols):
    """RREF mod prime N of augmented system; columns [0..ncols-1], last column (ncols-1) is k. returns k or None"""
    M = [row[:] + [rv] for row, rv in zip(rows, rhs)]; piv = []; r = 0
    for c in range(ncols):
        pr = next((i for i in range(r, len(M)) if M[i][c] % N), None)
        if pr is None: continue
        M[r], M[pr] = M[pr], M[r]; inv = pow(M[r][c], -1, N); M[r] = [v * inv % N for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] % N:
                f = M[i][c]; M[i] = [(u - f * v) % N for u, v in zip(M[i], M[r])]
        piv.append(c); r += 1
    kc = ncols - 1
    if kc in piv:
        row = M[piv.index(kc)]
        if all(row[c] % N == 0 for c in range(ncols - 1)): return row[-1]
    return None

def run_e2e(k=12):
    p, hA, hB = find_prime(k); r = rng(f"e2e-{k}")
    while True:
        E = rand_curve(r, p); pts = E.points(); N = len(pts)
        if is_prime(N) and N > 100: break
    ymap = valid_xs(E); sets = build_sets(E, ymap, hA, hB, r)
    # choose configuration: lowest total_w1 among sets by quick eval
    best = None; evals = {}
    for name, s in sets.items():
        d = eval_set(E, pts, ymap, s['xs'], rng(f"e2e-eval-{name}"), 100); evals[name] = d
        if best is None or d['total_w1'] < evals[best]['total_w1']: best = name
    xs = sets[best]['xs']; n = len(xs); m1 = M1(E, xs, ymap)
    P = affine_pt(E, r, pts); kk = r.randrange(2, N - 1); Q = E.mul(kk, P)
    idx = {x: i for i, x in enumerate(xs)}; rows = []; rhs = []; c = Cost(); att = 0; found = 0; kfound = None
    # unknowns: l_i = log of (x_i, ymap[x_i]) w.r.t. P (i<n), then k. relation: u + v k = sum s_i l_i  =>  sum s_i l_i - v k = u
    while True:
        att += 1; u, v = r.randrange(N), r.randrange(N); R = E.add(E.mul(u, P), E.mul(v, Q))
        if R is None: continue
        hit = m1.attempt(R, c)
        if hit is None: continue
        dec = m1.decompose(R, hit)
        row = [0] * (n + 1)
        for (Pi, sg) in dec:
            # logs of the stored sign: stored point (x, ymap[x]); sg refers to that stored point
            row[idx[Pi[0]]] = (row[idx[Pi[0]]] + sg) % N
        row[n] = (-v) % N; rows.append(row); rhs.append(u % N); found += 1
        if found >= n + 10 and (found - n - 10) % 5 == 0:
            kfound = solve_mod(rows, rhs, N, n + 1)
            if kfound is not None or found > 4 * n + 200: break
    bs = dlog_bsgs(E, P, Q, N)
    out = dict(k=k, p=p, order=N, config=best, n=n, evals=evals, attempts=att, relations=found, ops_M=c.M, ops_I=c.I, table_M=m1.build.M, table_I=m1.build.I,
               recovered=kfound, true_k=kk, bsgs=bs, Q_equals_kP=(E.mul(kfound, P) == Q) if kfound is not None else None,
               ok=(kfound is not None and kfound % N == bs % N and E.mul(kfound, P) == Q), sqrt_p=math.sqrt(p))
    json.dump(out, open(os.path.join(HERE, 'results_e2e.json'), 'w'), indent=1); print(out)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'verify':
        o = verify(); json.dump(o, open(os.path.join(HERE, 'results_verify.json'), 'w'), indent=1); print(json.dumps(o, indent=1))
    elif cmd == 'run': run_k(int(sys.argv[2]))
    elif cmd == 'm2': run_m2(int(sys.argv[2]))
    elif cmd == 'sweep': run_sweep()
    elif cmd == 'e2e': run_e2e()
