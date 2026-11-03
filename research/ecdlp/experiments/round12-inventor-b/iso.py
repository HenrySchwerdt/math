"""2-isogeny (Velu, rational 2-torsion kernel) volcano tools over F_p, short Weierstrass y^2=x^3+Ax+B."""
import random
from ecinv import *

def pmulmod(f, g, h, p):
    """polys as coefficient lists low->high, reduce modulo monic h"""
    res = [0]*(len(f)+len(g)-1)
    for i, a in enumerate(f):
        for j, b in enumerate(g): res[i+j] = (res[i+j] + a*b) % p
    return pmod(res, h, p)
def pmod(f, h, p):
    f = f[:]; dh = len(h)-1; inv = pow(h[-1], -1, p)
    while len(f)-1 >= dh and any(f):
        c = f[-1]*inv % p
        if c:
            for i in range(dh+1): f[len(f)-1-dh+i] = (f[len(f)-1-dh+i] - c*h[i]) % p
        f.pop()
    while f and f[-1] == 0: f.pop()
    return f
def pgcd(f, g, p):
    while g:
        f, g = g, pmod(f, g, p)
    return f
def ppow(base, e, h, p):
    r = [1]; b = pmod(base, h, p)
    while e:
        if e & 1: r = pmulmod(r, b, h, p) if r else []
        e >>= 1
        if e: b = pmulmod(b, b, h, p) if b else []
    return r
def roots_cubic(A, B, p, rng):
    """rational roots of x^3 + A x + B over F_p"""
    h = [B % p, A % p, 0, 1]
    xp = ppow([0, 1], p, h, p)
    xp = (xp + [0]*2)[:2] if len(xp) < 2 else xp
    diff = [(xp[i] if i < len(xp) else 0) - (1 if i == 1 else 0) for i in range(max(len(xp), 2))]
    diff = [c % p for c in diff]
    while diff and diff[-1] == 0: diff.pop()
    g = pgcd(h, diff, p) if diff else h   # product of (x - root)
    return split(g, p, rng)
def split(g, p, rng):
    if len(g) <= 1: return []
    if len(g) == 2: return [(-g[0]*pow(g[1], -1, p)) % p]
    while True:
        d = rng.randrange(p)
        w = ppow([d, 1], (p-1)//2, g, p)
        w = (w + [0])[:1] if not w else w
        w1 = w[:]; w1[0] = (w1[0] - 1) % p
        while w1 and w1[-1] == 0: w1.pop()
        if not w1: continue
        f1 = pgcd(g, w1, p)
        if 1 < len(f1) < len(g):
            f2 = pdiv(g, f1, p)
            return split(f1, p, rng) + split(f2, p, rng)
def pdiv(f, g, p):
    f = f[:]; q = [0]*(len(f)-len(g)+1); inv = pow(g[-1], -1, p)
    for i in range(len(q)-1, -1, -1):
        c = f[i+len(g)-1]*inv % p; q[i] = c
        for j in range(len(g)): f[i+j] = (f[i+j] - c*g[j]) % p
    return q

def velu2(A, B, x0, p):
    t = (3*x0*x0 + A) % p; w = x0*t % p
    return (A - 5*t) % p, (B - 7*w) % p, (x0, t)
def velu2_map(R, data, p):
    if R is None: return None
    x0, t = data; x, y = R
    iv = pow(x - x0, -1, p)
    return ((x + t*iv) % p, y*(1 - t*iv*iv) % p)
def neighbors(A, B, p, rng, C):
    C.iso += 1
    return [(velu2(A, B, x0, p), x0) for x0 in roots_cubic(A, B, p, rng)]

def jinv(A, B, p):
    num = 4*pow(A, 3, p) % p
    den = (4*pow(A, 3, p) + 27*B*B) % p
    return 1728*num*pow(den, -1, p) % p

def step_options(v, prev_j, p, rng, C):
    """non-backtracking neighbors of v=(A,B,...) : list of (A',B',dat)"""
    nb = neighbors(v[0], v[1], p, rng, C)
    out = []; skipped = False
    for (A2, B2, dat), x0 in nb:
        if prev_j is not None and not skipped and jinv(A2, B2, p) == prev_j:
            skipped = True; continue
        out.append((A2, B2, dat))
    return out

def deadend_len(v, prev_j, p, rng, C, cap=200):
    """length of one random non-backtracking walk starting at v (already having left prev) until dead end"""
    L = 0
    A, B = v
    pj = prev_j
    while L < cap:
        opts = step_options((A, B), pj, p, rng, C)
        if not opts: return L
        pj = jinv(A, B, p)
        A, B, _ = rng.choice(opts); L += 1
    return cap

def ascend(A, B, p, rng, C, Ps, stop=lambda A, B: A == 0 or B == 0, maxsteps=400):
    """climb the 2-volcano to a curve with j=0 or 1728; carry points Ps. Returns (A,B,points,steps) or None"""
    prev_j = None; steps = 0
    while steps < maxsteps:
        if stop(A, B): return A, B, Ps, steps
        opts = step_options((A, B), prev_j, p, rng, C)
        if not opts: return None
        if len(opts) == 1: pick = opts[0]
        else:
            Ls = []
            for (A2, B2, dat) in opts:
                Ls.append(max(deadend_len((A2, B2), jinv(A, B, p), p, rng, C) for _ in range(2)))
            pick = opts[max(range(len(opts)), key=lambda i: Ls[i])]
        A2, B2, dat = pick
        Ps = [velu2_map(R, dat, p) for R in Ps]
        prev_j = jinv(A, B, p); A, B = A2, B2; steps += 1
    return None
