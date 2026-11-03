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
            M.append((a, b, E.add(E.mul(a, P), E.mul(b, Q)))); ops += 3 * 2 * int(log(r, 2) + 1) // 2
        a0, b0 = rng.randrange(r), rng.randrange(r)
        R = E.add(E.mul(a0, P), E.mul(b0, Q)); ops += 3 * int(log(r, 2) + 1)
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
