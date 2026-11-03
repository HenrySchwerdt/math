"""Round 16 inventor G: closure measurement on toy prime-field curves y^2=x^3+ax+b, p = 3 mod 4, prime order N.
All arithmetic vectorised int64 (p < 2^31). Points are (x,y) arrays; O is excluded."""
import random, math, sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'round13-inventor-d'))
from d2lib import is_prime

def vpow(b, e, p):
    r = np.ones_like(b); b = b % p
    while e:
        if e & 1: r = r * b % p
        b = b * b % p; e >>= 1
    return r
def vinv(x, p): return vpow(x, p - 2, p)

def all_points(p, a, b):
    """All affine points as (X,Y) arrays (both signs of y), plus N = #E (incl. O)."""
    X = np.arange(p, dtype=np.int64)
    rhs = (X * X % p * X + a * X + b) % p
    leg = vpow(rhs, (p - 1) // 2, p)
    sq = leg == 1; zero = rhs == 0
    n_aff = 2 * int(sq.sum()) + int(zero.sum())
    xs = X[sq]; y = vpow(rhs[sq], (p + 1) // 4, p)
    Xs = np.concatenate([xs, xs, X[zero]]); Ys = np.concatenate([y, (p - y) % p, np.zeros(int(zero.sum()), dtype=np.int64)])
    return Xs, Ys, n_aff + 1

def gen_curve(bits, seed, need_prime=True):
    rng = random.Random(16000 * bits + seed)
    while True:
        p = rng.randrange(int(0.75 * 2 ** bits), 2 ** bits) | 3
        if p % 4 != 3 or not is_prime(p): continue
        for _ in range(40):
            a, b = rng.randrange(p), rng.randrange(p)
            if (4 * a ** 3 + 27 * b * b) % p == 0: continue
            # cheap order via Legendre sum
            X = np.arange(p, dtype=np.int64); rhs = (X * X % p * X + a * X + b) % p
            leg = vpow(rhs, (p - 1) // 2, p)
            N = p + 1 + int(np.where(leg == 1, 1, 0).sum() - np.where(leg == p - 1, 1, 0).sum())
            if (not need_prime) or is_prime(N): return dict(p=p, a=a, b=b, N=N, bits=bits, seed=seed)

def add_vec(p, a, x1, y1, x2, y2):
    """Vectorised affine addition; returns (x3,y3,valid) where valid excludes P+Q=O (and uses doubling where P==Q)."""
    dx = (x2 - x1) % p; same = (dx == 0) & (y1 == y2); neg = (dx == 0) & ~same
    num = np.where(same, (3 * x1 % p * x1 + a) % p, (y2 - y1) % p)
    den = np.where(same, 2 * y1 % p, dx)
    den = np.where(den == 0, 1, den)  # neg / 2-torsion masked below
    lam = num * vinv(den, p) % p
    x3 = (lam * lam - x1 - x2) % p; y3 = (lam * (x1 - x3) - y1) % p
    valid = ~neg & ~(same & (y1 == 0))
    return x3, y3, valid

def keys_of(p, X, Y): return X * p + Y

def closure_count(p, a, X, Y, chunk=1 << 22):
    """Number of ORDERED pairs (u,v), u!=v, u+v != O, both in V with u+v in V.  V = points (X,Y) (distinct)."""
    s = len(X); key = np.sort(keys_of(p, X, Y)); tot = 0
    rows = max(1, chunk // s)
    for i0 in range(0, s, rows):
        i1 = min(s, i0 + rows); I = np.repeat(np.arange(i0, i1), s); J = np.tile(np.arange(s), i1 - i0)
        m = I != J; I, J = I[m], J[m]
        x3, y3, ok = add_vec(p, a, X[I], Y[I], X[J], Y[J])
        k3 = keys_of(p, x3[ok], y3[ok]); pos = np.searchsorted(key, k3); pos[pos == s] = s - 1
        tot += int((key[pos] == k3).sum())
    return tot

def predicted_closure(s, N):
    """E[#ordered (u,v) u!=v, u+v!=O, u+v in V] for V a uniformly random s-subset of E\\{O}: ordered pairs with u+v!=O ~ s(s-1) - (#v=-u, 0 for random),
    u+v uniform on E\\{u,v... } -> (s-2)/(N-1)-ish. Use s(s-1)(s-2)/(N-2)."""
    return s * (s - 1) * (s - 2) / (N - 2)

def sym_window(scores, s, rng):
    """Given a score array over all affine points (to be +-symmetric by the caller), choose a rank window of length ~s at random offset."""
    o = np.argsort(scores, kind='stable'); n = len(o); st = rng.randrange(0, max(1, n - s))
    return o[st:st + s]
