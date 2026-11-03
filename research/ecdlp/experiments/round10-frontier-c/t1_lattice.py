"""T1: lattice decomposition of S_3 relations. See PROTOCOL.md."""
import sys, random, math, json
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime
from fractions import Fraction

def lll(Bm, delta=Fraction(99, 100)):
    """Integral LLL (Cohen 2.6.7). Bm: list of integer row vectors (independent)."""
    b = [list(r) for r in Bm]; n = len(b)
    dot = lambda u, v: sum(x * y for x, y in zip(u, v))
    d = [0] * (n + 1); d[0] = 1
    lam = [[0] * n for _ in range(n)]
    d[1] = dot(b[0], b[0])
    k, kmax = 1, 0
    def red(k, l):
        if 2 * abs(lam[k][l]) > d[l + 1]:
            q = (2 * lam[k][l] + d[l + 1]) // (2 * d[l + 1])
            b[k] = [x - q * y for x, y in zip(b[k], b[l])]
            lam[k][l] -= q * d[l + 1]
            for i in range(l): lam[k][i] -= q * lam[l][i]
    def swap(k):
        b[k], b[k - 1] = b[k - 1], b[k]
        for j in range(k - 1): lam[k][j], lam[k - 1][j] = lam[k - 1][j], lam[k][j]
        l = lam[k][k - 1]
        B = (d[k - 1] * d[k + 1] + l * l) // d[k]
        for i in range(k + 1, kmax + 1):
            t = lam[i][k]
            lam[i][k] = (d[k + 1] * lam[i][k - 1] - l * t) // d[k]
            lam[i][k - 1] = (B * t + l * lam[i][k]) // d[k + 1]
        d[k] = B
    while k < n:
        if k > kmax:
            kmax = k
            for j in range(k + 1):
                u = dot(b[k], b[j])
                for i in range(j):
                    u = (d[i + 1] * u - lam[k][i] * lam[j][i]) // d[i]
                if j < k: lam[k][j] = u
                else: d[k + 1] = u
        red(k, k - 1)
        if Fraction(d[k + 1] * d[k - 1] + lam[k][k - 1] ** 2, 1) < delta * d[k] * d[k]:
            swap(k); k = max(1, k - 1)
        else:
            for l in range(k - 2, -1, -1): red(k, l)
            k += 1
    return b

# ---- polynomial arithmetic: dict {(i,j): coeff} over Z
def pmul(A, B, mod=None):
    R = {}
    for (i, j), u in A.items():
        for (k, l), v in B.items():
            key = (i + k, j + l); R[key] = R.get(key, 0) + u * v
    if mod: R = {k: v % mod for k, v in R.items() if v % mod}
    return R

def S3(a, b, c, p):
    # (x-y)^2 c^2 - 2[(x+y)(xy+a)+2b] c + (xy-a)^2 - 4b(x+y)
    X, Y = {(1, 0): 1}, {(0, 1): 1}
    def add(*Ps):
        R = {}
        for s, P in Ps:
            for k, v in P.items(): R[k] = R.get(k, 0) + s * v
        return {k: v % p for k, v in R.items() if v % p}
    xmy = add((1, X), (-1, Y)); xpy = add((1, X), (1, Y))
    xy = pmul(X, Y); xyma = add((1, xy), (-a, {(0, 0): 1})); xya = add((1, xy), (a, {(0, 0): 1}))
    t1 = pmul(pmul(xmy, xmy), {(0, 0): c * c % p})
    t2 = pmul(pmul(xpy, xya), {(0, 0): -2 * c % p})
    t2 = add((1, t2), (-4 * b * c, {(0, 0): 1}))
    t3 = pmul(xyma, xyma); t4 = pmul(xpy, {(0, 0): -4 * b % p})
    return add((1, t1), (1, t2), (1, t3), (1, t4))

def ev(P, x, y): return sum(v * x ** i * y ** j for (i, j), v in P.items())

def build(f, p, B, D, m):
    rows, mons = [], [(a, b) for a in range(D + 1) for b in range(D + 1)]
    fp = [{(0, 0): 1}]
    for k in range(m): fp.append(pmul(fp[-1], f, p))
    ks = {}
    for (a, b) in mons:
        k = min(m, min(a, b) // 2); i, j = a - 2 * k, b - 2 * k
        P = {(u + i, v + j): c * p ** (m - k) for (u, v), c in fp[k].items()}
        rows.append(P); ks[(a, b)] = k
    idx = {mm: t for t, mm in enumerate(mons)}
    M = []
    for P in rows:
        r = [0] * len(mons)
        for (u, v), c in P.items():
            if (u, v) not in idx: raise ValueError('monomial outside set %s' % ((u, v),))
            r[idx[(u, v)]] = c * B ** u * B ** v
        M.append(r)
    return M, mons, ks

def analytic(alpha, D, m):
    # log_p of det / n  (Howgrave-Graham: need < m, up to small-n slack)
    n = (D + 1) ** 2; tot = 0.0
    for a in range(D + 1):
        for b in range(D + 1):
            k = min(m, min(a, b) // 2); tot += (m - k) + alpha * (a + b)
    return tot / n

def alpha_hg(D, m):
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if analytic(mid, D, m) < m: lo = mid
        else: hi = mid
    return lo

def rand_prime(rng, bits):
    while True:
        q = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime_big(q): return q

def is_prime_big(n):
    if n < 4: return n in (2, 3)
    if n % 2 == 0: return False
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if a % n == 0: continue
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

def sqrt_mod(n, p):  # p = 3 mod 4 assumed, else Tonelli
    n %= p
    if n == 0: return 0
    if pow(n, (p - 1) // 2, p) != 1: return None
    if p % 4 == 3: return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1: z += 1
    M, c, t, R = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, tt = 0, t
        while tt != 1: tt = tt * tt % p; i += 1
        bb = pow(c, 1 << (M - i - 1), p); M, c = i, bb * bb % p; t = t * c % p; R = R * bb % p
    return R

def add_pts(a, p, P, Q):
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    lam = ((3 * x1 * x1 + a) * pow(2 * y1, -1, p) if P == Q else (y2 - y1) * pow(x2 - x1, -1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

def run():
    # sanity of S3 on toy curve
    rng = random.Random(7)
    E = Curve(3, 5, 10007) if (4 * 27 + 27 * 25) % 10007 else None
    pts = [P for P in E.points() if P]
    ok = 0
    for _ in range(20):
        P1, P2 = rng.choice(pts), rng.choice(pts)
        R = E.add(P1, P2)
        if R is None or P1[0] == P2[0]: continue
        f = S3(E.a, E.b, R[0], E.p)
        ok += ev(f, P1[0], P2[0]) % E.p == 0
    print('S3 sanity: %d/20 pairs satisfy S3=0 (some skipped)' % ok, flush=True)
    # analytic
    best = max(((alpha_hg(D, m), D, m) for D in range(2, 41) for m in range(1, D // 2 + 2)))
    print('analytic max alpha_HG over D<=40: %.4f at D=%d m=%d' % best, flush=True)
    for D in (2, 3, 4, 5, 8, 12, 20, 40):
        print('  D=%d m=D//2: alpha_HG=%.4f' % (D, alpha_hg(D, max(1, D // 2))))
    # empirical
    rng = random.Random(1)
    p = rand_prime(rng, 61)
    print('p =', p, flush=True)
    results = {}
    for D in (2, 3, 4, 5):
        m = max(1, D // 2)
        for ai in range(1, 11):
            alpha = 0.05 * ai
            B = int(p ** alpha)
            succ = negs = 0
            T = 5
            for t in range(T):
                while True:
                    a, b = rng.randrange(p), rng.randrange(p)
                    if (4 * a ** 3 + 27 * b * b) % p: break
                def rpt():
                    while True:
                        x = rng.randrange(B); y = sqrt_mod(x ** 3 + a * x + b, p)
                        if y is not None: return (x, y)
                P1, P2 = rpt(), rpt()
                R = add_pts(a, p, P1, P2)
                if R is None: continue
                f = S3(a, b, R[0], p)
                M, mons, ks = build(f, p, B, D, m)
                red = lll(M)
                def vanish(root):
                    polys = []
                    for r in red:
                        P = {mm: r[t] // (B ** mm[0] * B ** mm[1]) for t, mm in enumerate(mons) if r[t]}
                        assert all(r[t] % (B ** mm[0] * B ** mm[1]) == 0 for t, mm in enumerate(mons))
                        if P and ev(P, root[0], root[1]) == 0: polys.append(P)
                    # pairwise non-proportional
                    ind = []
                    for P in polys:
                        if not any(set(P) == set(Q) and all(P[k] * Q[next(iter(Q))] == Q[k] * P[next(iter(Q))] for k in P) for Q in ind): ind.append(P)
                    return len(ind)
                succ += vanish((P1[0], P2[0])) >= 2
                negs += vanish((rng.randrange(B), rng.randrange(B))) >= 2
            results[(D, m, round(alpha, 2))] = (succ, negs, T)
            print('D=%d m=%d alpha=%.2f B=2^%.1f success %d/%d  negctrl %d/%d' % (D, m, alpha, math.log2(B), succ, T, negs, T), flush=True)
    return results

if __name__ == '__main__':
    run()
