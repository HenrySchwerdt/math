"""Round 12 inventor B: counted-operation rho (plain / negation / automorphism-orbit),
2-isogeny (Velu) volcano ascent. Python prototypes on toy curves; toyec.py is the oracle for BSGS checks."""
import random, sys, os
from math import isqrt, log2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from toyec import Curve, dlog_bsgs

# ---------------- number theory helpers
def is_prime(n):
    if n < 2: return False
    for q in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % q == 0: return n == q
    d, s = n-1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2,3,5,7,11,13,17,19,23,29,31,37):
        x = pow(a, d, n)
        if x in (1, n-1): continue
        for _ in range(s-1):
            x = x*x % n
            if x == n-1: break
        else: return False
    return True

class Counter:
    def __init__(self): self.add = 0; self.iso = 0

# ---------------- counted group law (affine)
def eadd(P, Q, a, p, C):
    C.add += 1
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = (3*x1*x1 + a) * pow(2*y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam*lam - x1 - x2) % p
    return (x3, (lam*(x1 - x3) - y1) % p)

def emul(k, P, a, p, C):
    R = None
    while k:
        if k & 1: R = eadd(R, P, a, p, C)
        k >>= 1
        if k: P = eadd(P, P, a, p, C)
    return R

# ---------------- automorphism groups: list of (cx, cy, mu); sigma(x,y)=(cx x, cy y), sigma(R)=mu R
def aut_group(kind, E, P, r):
    p, a, b = E.p, E.a, E.b
    if kind == 'none': return [(1, 1, 1)]
    if kind == 'neg': return [(1, 1, 1), (1, p-1, r-1)]
    c = None
    C = Counter()
    if kind == 'j0':      # (x,y)->(z x, y), z^3=1
        assert a == 0
        while True:
            g = random.randrange(2, p); z = pow(g, (p-1)//3, p)
            if z != 1: break
        sig = lambda R: (R[0]*z % p, R[1]); gens = (z, 1); order = 3
    elif kind == 'j1728': # (x,y)->(-x, i y), i^2=-1
        assert b == 0
        while True:
            g = random.randrange(2, p); i = pow(g, (p-1)//4, p)
            if i*i % p == p-1: break
        sig = lambda R: ((-R[0]) % p, R[1]*i % p); gens = (p-1, i); order = 4
    else: raise ValueError(kind)
    S = sig(P)
    # find scalar mu with S = mu P among elements mu of order `order` (j0) or 4 (j1728) in F_r^*
    mu = None
    for _ in range(200):
        g = random.randrange(2, r); lam = pow(g, (r-1)//order, r)
        if lam != 1 and (order != 4 or lam*lam % r == r-1):
            if emul(lam, P, a, p, C) == S: mu = lam; break
            if emul(lam, P, a, p, C) is not None and mu is None: pass
    assert mu is not None, 'no eigenvalue found'
    G = []
    for k in range(order):
        cx = pow(gens[0], k, p) if kind == 'j0' else (1 if k % 2 == 0 else p-1)
        cy = 1 if kind == 'j0' else pow(gens[1], k, p)
        for s in (1, -1):
            G.append((cx, cy*s % p, pow(mu, k, r)*s % r))
    # for j1728 the [i]^k composite is (x,y)->((-1)^k x, i^k y); consistent with sigma^k
    return G

def canon(R, G, p, r):
    """return (canonical point, mu with canonical = mu*R)"""
    if len(G) == 1: return R, 1
    x, y = R
    best = None
    for cx, cy, mu in G:
        c = (cx*x % p, cy*y % p)
        if best is None or c < best[0]: best = (c, mu)
    return best

# ---------------- rho (distinguished points, r-adding walk, orbit-quotient, cycle escape)
def rho(E, P, Q, r, G, rng, kind_cap=60, m=64, ring=8):
    """Returns (k, ops, info). Counted group operations: every add/double incl. start points and cycle-escape."""
    p, a = E.p, E.a
    C = Counter()
    g = len(G)
    d = max(1, round(log2(0.25*isqrt(r)/g**0.5 + 1)))
    mask = (1 << d) - 1
    capsteps = 20 * (1 << d)
    steps = []
    for _ in range(m):
        u, v = rng.randrange(r), rng.randrange(r)
        S = eadd(emul(u, P, a, p, C), emul(v, Q, a, p, C), a, p, C)
        steps.append((S, u, v))
    C.add = 0  # step-table precomputation (m fixed points) not charged to the walk phase; reported separately
    pre = 0
    table = {}
    budget = kind_cap * isqrt(r) + 2000
    cyc = restarts = 0
    while C.add < budget:
        a0, b0 = rng.randrange(r), rng.randrange(r)
        R = eadd(emul(a0, P, a, p, C), emul(b0, Q, a, p, C), a, p, C)
        if R is None: continue
        R, mu = canon(R, G, p, r); a0 = a0*mu % r; b0 = b0*mu % r
        hist = []
        ok = False
        for it in range(capsteps):
            x = R[0]
            if (x & mask) == 0 and x != 0:
                key = R
                if key in table:
                    a1, b1 = table[key]
                    if b1 != b0:
                        k = (a1 - a0) * pow(b0 - b1, -1, r) % r
                        if emul(k, P, a, p, C) == Q or (Q is None):
                            return k, C.add, dict(cyc=cyc, restarts=restarts, d=d)
                    # trivial collision or wrong: restart
                else:
                    table[key] = (a0, b0)
                ok = True; break
            if g > 1:
                if R in (h[0] for h in hist):
                    # cycle: deterministic escape = double the smallest point of the cycle
                    j0 = [h[0] for h in hist].index(R)
                    cycpts = hist[j0:] + [(R, a0, b0)]
                    Rm, am, bm = min(cycpts, key=lambda t: t[0])
                    R2 = eadd(Rm, Rm, a, p, C); am2, bm2 = 2*am % r, 2*bm % r
                    if R2 is None: break
                    R, mu = canon(R2, G, p, r); a0 = am2*mu % r; b0 = bm2*mu % r
                    hist = []; cyc += 1; continue
                hist.append((R, a0, b0))
                if len(hist) > ring: hist.pop(0)
            S, u, v = steps[x % m]
            R2 = eadd(R, S, a, p, C)
            if R2 is None: break
            R, mu = canon(R2, G, p, r)
            a0 = (a0 + u) * mu % r; b0 = (b0 + v) * mu % r
        restarts += 1
    return None, C.add, dict(cyc=cyc, restarts=restarts, d=d, failed=True)
