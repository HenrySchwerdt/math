"""Round 21 tournament explorer C: experiments E1..E6 (see PROTOCOL.md). Toy curves only."""
import sys, os, json, math, random, time
import numpy as np
sys.path.insert(0, '/home/user/math/research/ecdlp/experiments/round12-inventor-c')
sys.path.insert(0, '/home/user/math/research/ecdlp/experiments/lib')
from lib12 import find_prime_order_curve, Ops
from toyec import Curve, is_prime
HERE = os.path.dirname(os.path.abspath(__file__))

def seq_points(E, P, n):
    """points kP for k=1..n as arrays X, Y (python loop, inline affine add)."""
    p, a = E.p, E.a
    X = np.zeros(n + 1, dtype=np.int64); Y = np.zeros(n + 1, dtype=np.int64)
    x0, y0 = P; x, y = x0, y0
    X[1], Y[1] = x, y
    for k in range(2, n + 1):
        if x == x0:
            if (y + y0) % p == 0:
                X[k] = -1; Y[k] = -1; x = None
                # infinity: next is P again
                x, y = x0, y0; continue
            lam = (3 * x * x + a) * pow(2 * y, -1, p) % p
        else:
            lam = (y0 - y) * pow(x0 - x, -1, p) % p
        x3 = (lam * lam - x - x0) % p
        y3 = (lam * (x - x3) - y) % p
        x, y = x3, y3
        X[k], Y[k] = x, y
    return X, Y

# ---------------- E1: Berlekamp-Massey ----------------
def bm_lc(s, p):
    s = np.asarray(s, dtype=np.int64) % p
    n = len(s)
    C = np.zeros(n + 2, dtype=np.int64); B = np.zeros(n + 2, dtype=np.int64)
    C[0] = B[0] = 1; L = 0; m = 1; b = 1
    for i in range(n):
        if L:
            d = (int(s[i]) + int(np.dot(C[1:L + 1], s[i - 1::-1][:L] if i > 0 else s[:0]) % p)) % p
        else:
            d = int(s[i]) % p
        if d == 0:
            m += 1; continue
        coef = d * pow(b, -1, p) % p
        if 2 * L <= i:
            T = C[:L + 2].copy()
            C[m:m + len(B[:n + 2 - m])][:n + 2 - m] = (C[m:n + 2] - coef * B[:n + 2 - m]) % p
            L2 = i + 1 - L
            B = np.zeros(n + 2, dtype=np.int64); B[:len(T)] = T
            L = L2; b = d; m = 1
        else:
            C[m:n + 2] = (C[m:n + 2] - coef * B[:n + 2 - m]) % p
            m += 1
    return L

def e1():
    out = []
    for bits in (10, 12, 14):
        for seed in (1, 2, 3):
            E, P, r = find_prime_order_curve(bits, 100 + seed)
            n = 2 * r + 10
            # sequence over k=1..n: x(kP) with P of order r; wrap correctly using periodicity
            X, Y = seq_points(E, P, r)
            xs = np.tile(X[1:r + 1], 3)[:n]; ys = np.tile(Y[1:r + 1], 3)[:n]
            rng = np.random.default_rng(seed + bits)
            rs = np.tile(rng.integers(0, E.p, r), 3)[:n]
            # planted order-L recurrence
            Lp = r // 4
            c = rng.integers(1, E.p, Lp); sq = list(rng.integers(0, E.p, Lp)); 
            for i in range(Lp, n):
                sq.append(int(np.dot(c, np.array(sq[i - Lp:i][::-1], dtype=np.int64)) % E.p))
            t0 = time.time()
            row = dict(bits=bits, seed=seed, p=E.p, r=r,
                       LC_x=bm_lc(xs, E.p), LC_y=bm_lc(ys, E.p), LC_random_periodic=bm_lc(rs, E.p),
                       LC_planted=bm_lc(np.array(sq), E.p), planted_L=Lp, sec=round(time.time() - t0, 1))
            row['LC_x_over_r'] = row['LC_x'] / r
            print(json.dumps(row), flush=True); out.append(row)
    json.dump(out, open(os.path.join(HERE, 'results_e1.json'), 'w'), indent=1)

# ---------------- E2: P-recursive guess ----------------
def nullity_mod(M, p):
    M = M.copy() % p; rows, cols = M.shape; rk = 0
    for c in range(cols):
        piv = None
        for i in range(rk, rows):
            if M[i, c] % p: piv = i; break
        if piv is None: continue
        M[[rk, piv]] = M[[piv, rk]]
        M[rk] = M[rk] * pow(int(M[rk, c]), -1, p) % p
        nz = np.nonzero(M[:, c])[0]
        for i in nz:
            if i != rk: M[i] = (M[i] - M[i, c] * M[rk]) % p
        rk += 1
    return cols - rk

def guess(u, p, d, e):
    """u: dict-like array with u[k], k=1..; returns nullity of recurrence system"""
    n = (d + 1) * (e + 1) + 60
    ks = np.arange(1, n + 1, dtype=np.int64)
    cols = []
    for i in range(d + 1):
        for t in range(e + 1):
            cols.append((pow_arr(ks, t, p) * u[ks + i]) % p)
    return nullity_mod(np.stack(cols, axis=1), p)

def pow_arr(a, t, p):
    r = np.ones_like(a)
    for _ in range(t): r = r * a % p
    return r

def e2():
    res = []
    # positive controls
    p0 = 1000003
    n0 = 200
    fact = np.ones(n0 + 20, dtype=np.int64)
    for k in range(1, n0 + 20): fact[k] = fact[k - 1] * k % p0
    cat = np.zeros(n0 + 20, dtype=np.int64); cat[0] = 1
    for k in range(0, n0 + 19): cat[k + 1] = cat[k] * 2 * (2 * k + 1) % p0 * pow(k + 2, -1, p0) % p0
    for name, u in (('factorial', fact), ('catalan', cat)):
        nl = {(d, e): guess(u, p0, d, e) for d in (1, 2) for e in (1, 2)}
        row = dict(seq=name, control=True, nullities={f'{d},{e}': v for (d, e), v in nl.items()})
        print(json.dumps(row), flush=True); res.append(row)
    for bits in (14, 18):
        for seed in (1, 2):
            E, P, r = find_prime_order_curve(bits, 200 + seed)
            n = 7 * 7 + 60 + 20
            X, Y = seq_points(E, P, n + 10)
            rng = random.Random(bits * 10 + seed)
            X0 = rng.randrange(E.p)
            while X0 in set(X[1:n + 10].tolist()): X0 = rng.randrange(E.p)
            g = np.ones(n + 10, dtype=np.int64)
            for m in range(1, n + 10): g[m] = g[m - 1] * ((X0 - int(X[m])) % E.p) % E.p
            for name, u in (('x', X), ('y', Y), ('prod', g)):
                u = np.concatenate([u, np.zeros(10, dtype=np.int64)])
                found = []; mn = 0
                for d in range(1, 7):
                    for e in range(0, 7):
                        nu = guess(u, E.p, d, e)
                        if nu > 0: found.append((d, e, nu))
                row = dict(bits=bits, seed=seed, p=E.p, r=r, seq=name, control=False, found=found, grid='d1-6,e0-6')
                print(json.dumps(row), flush=True); res.append(row)
    json.dump(res, open(os.path.join(HERE, 'results_e2.json'), 'w'), indent=1)

# ---------------- E3: structural checks ----------------
def rank_mod(M, p):
    return min(M.shape) - 0 if False else (M.shape[1] - nullity_mod(M, p))

def e3():
    res = {}
    for p in (211, 1009):
        rng = random.Random(p)
        while True:
            a, b = rng.randrange(p), rng.randrange(p)
            try: E = Curve(a, b, p); break
            except ValueError: continue
        pts = [P for P in E.points() if P is not None]
        # distinct x-labels split into two disjoint halves
        byx = {}
        for P in pts: byx.setdefault(P[0], P)
        xs = sorted(byx); rng.shuffle(xs)
        h = len(xs) // 2
        A = [byx[x] for x in xs[:min(h, 120)]]; B = [byx[x] for x in xs[h:h + min(h, 120)]]
        N = np.zeros((len(A), len(B)), dtype=np.int64); Dm = np.zeros_like(N); ident_ok = True
        for i, Pa in enumerate(A):
            for j, Pb in enumerate(B):
                s = E.add(Pa, Pb); t = E.add(Pa, E.neg(Pb))
                if s is None or t is None: raise RuntimeError('unexpected')
                N[i, j] = (s[0] + t[0]) % p
                dx = (Pa[0] - Pb[0]) % p
                Dm[i, j] = dx * dx % p
                num = 2 * ((Pa[0] + Pb[0]) * (Pa[0] * Pb[0] + a) + 2 * b) % p
                if (N[i, j] * Dm[i, j] - num) % p: ident_ok = False
        S = (N * Dm) % p
        res[f'cauchy_p{p}'] = dict(p=p, a=a, b=b, shape=list(N.shape), identity_ok=ident_ok,
                                   rank_scaled=rank_mod(S, p), rank_unscaled=rank_mod(N, p))
        print(json.dumps(res[f'cauchy_p{p}']), flush=True)
    for bits in (8, 10):
        E, P, r = find_prime_order_curve(bits, 5)
        n = int(math.floor(math.log2(r))); M = 2 ** n
        X, Y = seq_points(E, P, M + 1)
        pid = {}  # a -> point index: for a in [1,M) , a=0 -> infinity index 0
        idx = {None: 0}
        tid = np.zeros(M, dtype=np.int64)
        for a in range(1, M): tid[a] = a  # injective (a<M<=r): label by a itself is the point identity
        # verify injectivity of a -> aP on [0,M)
        pts = {(int(X[a]), int(Y[a])) for a in range(1, M)}
        inj = (len(pts) == M - 1)
        rows = []
        for j in range(1, n + 1):
            lo = 2 ** j
            Mat = np.zeros((lo, (M // lo) * r), dtype=np.float64) if lo * (M // lo) * r < 3e7 else None
            if Mat is None:
                rows.append(dict(cut=j, skipped='size')); continue
            # column (a_high, t) with t = scalar index a mod r (point identity)
            for a in range(M):
                al, ah = a % lo, a // lo
                Mat[al, ah * r + a] = 1.0
            s = np.linalg.svd(Mat, compute_uv=False)
            nz = s[s > 1e-9]
            rows.append(dict(cut=j, rank=int(len(nz)), sv_min=float(nz.min()), sv_max=float(nz.max()), flat=bool(abs(nz.max() - nz.min()) < 1e-9)))
        # a | target cut
        Mat = np.zeros((M, r)); 
        for a in range(M): Mat[a, a % r] = 1.0
        s = np.linalg.svd(Mat, compute_uv=False)
        res[f'schmidt_r{r}'] = dict(r=r, n=n, injective=inj, cuts=rows, a_vs_target_rank=int((s > 1e-9).sum()), a_vs_target_flat=bool(abs(s.max() - s.min()) < 1e-9))
        print(json.dumps(res[f'schmidt_r{r}']), flush=True)
    json.dump(res, open(os.path.join(HERE, 'results_e3.json'), 'w'), indent=1)

# ---------------- E4: multiplicative-character leak ----------------
def factor_small(n):
    f = []; d = 2
    while d * d <= n:
        if n % d == 0:
            f.append(d)
            while n % d == 0: n //= d
        d += 1
    if n > 1: f.append(n)
    return f

def find_curve_1mod30(bits, which):
    got = 0; s = 0
    while True:
        s += 1
        E, P, r = find_prime_order_curve(bits, 3000 + s)
        if r % 30 == 1:
            got += 1
            if got == which: return E, P, r, 3000 + s

def gen_of_unit(r):
    fs = factor_small(r - 1)
    g = 2
    while any(pow(g, (r - 1) // f, r) == 1 for f in fs): g += 1
    return g

def e4(bits_list, ncur=2):
    from scipy.stats import chi2
    out = []
    for bits in bits_list:
        for which in range(1, ncur + 1):
            t0 = time.time()
            E, P, r, cs = find_curve_1mod30(bits, which)
            p = E.p
            X, Y = seq_points(E, P, r - 1)   # X[1..r-1]
            X = X[1:]; Y = Y[1:]  # index k-1
            h = (r - 1) // 2
            ks = np.arange(1, h + 1, dtype=np.int64)   # ADDENDUM 1: one unit per +-pair
            # discrete log of k in (Z/r)^*
            g = gen_of_unit(r)
            ind = np.zeros(r, dtype=np.int64); v = 1
            for i in range(r - 1):
                ind[v] = i; v = v * g % r
            lab = {q: (ind[ks] % q) for q in (2, 3, 5)}
            def at(mult):   # coordinates of (mult*k)P, k=1..r-1
                idx = (ks * mult) % r
                z = idx == 0
                idx2 = np.where(z, 1, idx) - 1
                return X[idx2], Y[idx2], z
            def shift(j):
                idx = (ks + j) % r
                idx2 = np.where(idx == 0, 1, idx) - 1
                return X[idx2], Y[idx2]
            leg = np.zeros(p, dtype=np.int8)
            sq = (np.arange(p, dtype=np.int64) ** 2) % p
            leg[:] = -1; leg[sq] = 1; leg[0] = 0
            XH, YH = X[:h], Y[:h]
            arrays = {'x': XH, 'y': YH}
            for j in (1, -1, 2, -2):
                xs, ys = shift(j); arrays[f'x{j:+d}P'] = xs; arrays[f'y{j:+d}P'] = ys
            for m in (2, 3, 5):
                xs, ys, z = at(m); arrays[f'x[{m}]Q'] = xs; arrays[f'y[{m}]Q'] = ys
            feats = {}
            for nm, v in arrays.items():
                feats[f'{nm}:low8'] = v & 255
                feats[f'{nm}:b8_11'] = (v >> 8) & 15
                for m in (3, 5, 7, 9, 11, 13): feats[f'{nm}:mod{m}'] = v % m
                for c in (-2, -1, 0, 1, 2): feats[f'{nm}:leg{c:+d}'] = leg[(v + c) % p].astype(np.int64) + 1
                feats[f'{nm}:half'] = (v < p // 2).astype(np.int64)
            for j in (1, -1):
                xs, ys = shift(j)
                d = (xs - XH) % p
                feats[f'dx{j:+d}:par'] = d & 1; feats[f'dx{j:+d}:mod3'] = d % 3; feats[f'dx{j:+d}:leg'] = leg[d].astype(np.int64) + 1
                feats[f'carry{j:+d}'] = ((xs + XH) >= p).astype(np.int64)
            feats['leg(x-Px)'] = leg[(XH - P[0]) % p].astype(np.int64) + 1
            feats['leg(y-Py)'] = leg[(YH - P[1]) % p].astype(np.int64) + 1
            feats['leg(xy)'] = leg[(XH * YH) % p].astype(np.int64) + 1
            rng = np.random.default_rng(bits * 7 + which)
            planted = np.where(rng.random(h) < 0.55, lab[2], 1 - lab[2])
            feats['PLANTED_c2_eps0.05'] = planted
            n = h
            rows = []; perm_p = {}; perm_info = {}
            par = (np.arange(h) % 2).astype(bool)
            for q in (2, 3, 5):
                c = lab[q]
                perms = [rng.permutation(c) for _ in range(30)]
                maxT_null = []
                chis = {}
                for nm, f in feats.items():
                    A = int(f.max()) + 1
                    def chi_of(cc):
                        tab = np.bincount(f * q + cc, minlength=A * q).reshape(A, q).astype(float)
                        row_s = tab.sum(1, keepdims=True); col_s = tab.sum(0, keepdims=True)
                        expct = row_s * col_s / n; msk = expct > 0
                        chi = float((((tab - expct) ** 2)[msk] / expct[msk]).sum())
                        dof = (int((row_s > 0).sum()) - 1) * (q - 1)
                        return tab, chi, dof
                    tab, chi, dof = chi_of(c)
                    pv = float(chi2.sf(chi, dof)) if dof > 0 else 1.0
                    T = (chi - dof) / math.sqrt(2 * dof) if dof > 0 else 0.0
                    # cross-fit held-out accuracy gain
                    gains = []
                    for tr, te in ((~par, par), (par, ~par)):
                        t_tr = np.bincount(f[tr] * q + c[tr], minlength=A * q).reshape(A, q)
                        pred = t_tr.argmax(1)
                        gains.append(float((pred[f[te]] == c[te]).mean()) - 1.0 / q)
                    gain = float(np.mean(gains)); se = math.sqrt(0.25 / (n / 2) / 2)
                    chis[nm] = T
                    rows.append(dict(q=q, feat=nm, A=A, chi2=chi, dof=dof, p=pv, T=T, heldout_gain=gain, gain_se=se, gain_lo99=gain - 2.576 * se, gain_hi99=gain + 2.576 * se))
                for pc in perms:
                    mT = -1e9
                    for nm, f in feats.items():
                        if nm.startswith('PLANTED'): continue
                        A = int(f.max()) + 1
                        tab, chi, dof = chi_of(pc) if False else (None, None, None)
                        tab = np.bincount(f * q + pc, minlength=A * q).reshape(A, q).astype(float)
                        row_s = tab.sum(1, keepdims=True); col_s = tab.sum(0, keepdims=True)
                        expct = row_s * col_s / n; msk = expct > 0
                        chi = float((((tab - expct) ** 2)[msk] / expct[msk]).sum()); dof = (int((row_s > 0).sum()) - 1) * (q - 1)
                        if dof > 0: mT = max(mT, (chi - dof) / math.sqrt(2 * dof))
                    maxT_null.append(mT)
                realmax = max(v for k_, v in chis.items() if not k_.startswith('PLANTED'))
                perm_p[q] = (1 + sum(1 for v in maxT_null if v >= realmax)) / (1 + len(maxT_null))
                perm_info[q] = dict(real_maxT=realmax, null_maxT_mean=float(np.mean(maxT_null)), null_maxT_max=float(np.max(maxT_null)))
            nt = len(rows)
            thr = 0.01 / nt
            real = [x for x in rows if not x['feat'].startswith('PLANTED')]
            sig = [x for x in real if x['p'] < thr]
            leak = [x for x in sig if x['gain_lo99'] > 0]
            ctrl = [x for x in rows if x['feat'].startswith('PLANTED') and x['q'] == 2][0]
            best = max(real, key=lambda x: x['heldout_gain'])
            minp = min(real, key=lambda x: x['p'])
            summ = dict(bits=bits, which=which, curve_seed=cs, p=p, r=r, units=n, n_features=len(feats), n_tests=nt, bonf_threshold=thr,
                        n_significant_real=len(sig), n_leak_real=len(leak), significant=[(x['q'], x['feat'], x['p'], x['heldout_gain']) for x in sig[:8]],
                        min_p_real=(minp['q'], minp['feat'], minp['p']), max_heldout_gain_real=(best['q'], best['feat'], best['heldout_gain'], best['gain_hi99']),
                        perm_maxT_p_by_q=perm_p, perm_info=perm_info,
                        planted_control=dict(p=ctrl['p'], heldout_gain=ctrl['heldout_gain'], lo99=ctrl['gain_lo99'], flagged=bool(ctrl['p'] < thr and ctrl['gain_lo99'] > 0)), sec=round(time.time() - t0, 1))
            print(json.dumps(summ), flush=True); out.append(summ)
            json.dump(rows, open(os.path.join(HERE, f'e4_rows_{bits}_{which}.json'), 'w'))
    json.dump(out, open(os.path.join(HERE, f'results_e4_{"_".join(map(str, bits_list))}.json'), 'w'), indent=1)

# ---------------- E5: RS list-decoding alignment ----------------
def e5():
    res = []
    N = 1200
    for bits in (16, 18):
        for seed in (1, 2, 3):
            E, P, r = find_prime_order_curve(bits, 400 + seed)
            p = E.p
            X, Y = seq_points(E, P, N)
            x = X[1:N + 1]
            dx = (x[None, :] - x[:, None]) % p
            np.fill_diagonal(dx, 1)
            inv = np.ones_like(dx); base = dx.copy(); ex = p - 2
            while ex:
                if ex & 1: inv = inv * base % p
                base = base * base % p; ex >>= 1
            np.fill_diagonal(inv, 0)
            j = np.arange(1, N + 1, dtype=np.int64)
            def maxmult(t):
                num = (t[None, :] - t[:, None]) % p
                sl = num * inv % p
                np.fill_diagonal(sl, -1 - np.arange(N))   # unique sentinel per row: avoid diagonal collisions
                srt = np.sort(sl, axis=1)
                best = 1
                eq = (srt[:, 1:] == srt[:, :-1])
                # longest run of equal values per row
                m = 0
                for i in range(N):
                    e = eq[i]
                    if not e.any(): continue
                    idxs = np.nonzero(~e)[0]
                    # run lengths between breaks
                    edges = np.concatenate([[-1], idxs, [N - 2]])
                    rl = np.diff(edges).max()
                    m = max(m, int(rl))
                return m   # number of other points collinear with a pivot (>=1 if any equal slopes)
            rng = np.random.default_rng(bits + seed)
            for tname, t in (('j', j), ('j^2', j * j % p)):
                obs = maxmult(t)
                nulls = [maxmult(rng.permutation(t)) for _ in range(20)]
                # planted: 30% of labels replaced by a*x+b
                tp = t.copy(); sel = rng.random(N) < 0.3
                a_, b_ = int(rng.integers(1, p)), int(rng.integers(0, p))
                tp[sel] = (a_ * x[sel] + b_) % p
                pl = maxmult(tp)
                row = dict(bits=bits, seed=seed, p=p, r=r, target=tname, obs=obs, null_max=max(nulls), null_mean=float(np.mean(nulls)), planted=pl, planted_expected=int(sel.sum()) - 1)
                row['exceeds_null'] = obs > max(nulls)
                print(json.dumps(row), flush=True); res.append(row)
    json.dump(res, open(os.path.join(HERE, 'results_e5.json'), 'w'), indent=1)

# ---------------- E6: rho control ----------------
def rho(r, ops, P, Q, rng):
    nj = 20; steps = []
    for _ in range(nj):
        u, v = rng.randrange(r), rng.randrange(r)
        steps.append((u, v, ops.add(ops.mul(u, P), ops.mul(v, Q))))
    dpbits = max(1, int(math.log2(max(2, math.isqrt(r))) / 2) - 1); mask = (1 << dpbits) - 1
    c0 = ops.count; table = {}
    while True:
        a, b = rng.randrange(r), rng.randrange(r); R = ops.add(ops.mul(a, P), ops.mul(b, Q))
        for _ in range(40 * (mask + 1)):
            if R is None: break
            if (R[0] & mask) == 0:
                if R in table and table[R] != (a, b):
                    a2, b2 = table[R]; db = (b - b2) % r
                    if db:
                        k = (a2 - a) * pow(db, -1, r) % r
                        if ops.mul(k, P) == Q: return k, ops.count - c0
                    break
                table[R] = (a, b)
            u, v, S = steps[R[0] % nj]; R = ops.add(R, S); a = (a + u) % r; b = (b + v) % r

def e6(bits_list, nrep=10):
    out = []
    for bits in bits_list:
        for s in range(nrep):
            E, P, r = find_prime_order_curve(bits, 700 + s)
            ops = Ops(E.p, E.a); rng = random.Random(f'e6-{bits}-{s}')
            k = rng.randrange(1, r); Q = ops.mul(k, P)
            kk, c = rho(r, ops, P, Q, rng)
            assert ops.mul(kk, P) == Q
            out.append(dict(bits=bits, seed=s, r=r, ops=c))
        print(bits, np.mean([o['ops'] for o in out if o['bits'] == bits]), flush=True)
    json.dump(out, open(os.path.join(HERE, f'results_e6_{"_".join(map(str, bits_list))}.json'), 'w'), indent=1)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'e1': e1()
    elif cmd == 'e2': e2()
    elif cmd == 'e3': e3()
    elif cmd == 'e4': e4([int(b) for b in sys.argv[2].split(',')], int(sys.argv[3]) if len(sys.argv) > 3 else 2)
    elif cmd == 'e5': e5()
    elif cmd == 'e6': e6([int(b) for b in sys.argv[2].split(',')], int(sys.argv[3]) if len(sys.argv) > 3 else 10)
