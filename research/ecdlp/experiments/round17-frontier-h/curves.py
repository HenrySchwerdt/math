"""Round 17 / frontier H: fast prime-order toy-curve generation up to 2^20 (numpy point count + table build).
Curve params are deterministic in (tb, seed); tables cached under cache/ (git-ignored, regenerable)."""
import os, sys, math, random, pickle
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.environ.get('CURVE_CACHE', os.path.join(HERE, 'cache'))
_MEM = {}

def is_prime(n):
    if n < 2: return False
    if n % 2 == 0: return n == 2
    for q in range(3, math.isqrt(n) + 1, 2):
        if n % q == 0: return False
    return True

def count_points(p, a, b):
    xs = np.arange(p, dtype=np.int64)
    sq = np.zeros(p, dtype=bool); sq[(xs * xs) % p] = True
    v = (((xs * xs) % p) * xs + a * xs + b) % p
    return int(1 + np.where(v == 0, 1, np.where(sq[v], 2, 0)).sum()), sq, xs

def sqrt_mod(n, p):
    n %= p
    if n == 0: return 0
    if pow(n, (p - 1) // 2, p) != 1: return None
    if p % 4 == 3: return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1: z += 1
    m, c, t, R = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1: t2 = t2 * t2 % p; i += 1
        b = pow(c, 1 << (m - i - 1), p); m, c = i, b * b % p; t = t * c % p; R = R * b % p
    return R

def make_curve(tb, seed):
    key = (tb, seed)
    if key in _MEM: return _MEM[key]
    f = os.path.join(CACHE_DIR, f'curve_{tb}_{seed}.pkl')
    if os.path.exists(f):
        c = pickle.load(open(f, 'rb')); _MEM[key] = c; return c
    rng = random.Random(1000003 * tb + seed)
    lo, hi = int(2 ** tb * 0.94), int(2 ** tb * 1.06)
    while True:
        p = rng.randrange(lo, hi)
        if p < 5 or not is_prime(p): continue
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a ** 3 + 27 * b ** 2) % p == 0: continue
        r, sq, xs = count_points(p, a, b)
        if r == p or not (2 ** (tb - .2) <= r < 2 ** (tb + .2)) or not is_prime(r): continue
        break
    # generator: first random x with rhs square
    ysq = np.zeros(p, dtype=np.int64); ysq[(xs * xs) % p] = xs
    while True:
        x0 = rng.randrange(p); rhs = (x0 ** 3 + a * x0 + b) % p
        if rhs and sq[rhs]: y0 = int(ysq[rhs]); break
    xt = [-1] * r; X, Y = x0, y0
    for i in range(1, r):
        xt[i] = X
        if i == r - 1: break
        # add (x0,y0) to (X,Y)
        if X == x0:
            if (Y + y0) % p == 0: raise AssertionError('order < r')
            lam = (3 * X * X + a) * pow(2 * Y, -1, p) % p
        else:
            lam = (y0 - Y) * pow(x0 - X, -1, p) % p
        X3 = (lam * lam - X - x0) % p
        Y = (lam * (X - X3) - Y) % p; X = X3
    assert X == x0 and (Y + y0) % p == 0   # xt[r-1] = -P, so order is r
    xi = np.full(p, -1, dtype=np.int64); xi[np.array(xt[1:], dtype=np.int64)] = np.arange(1, r)
    c = dict(r=r, p=p, a=a, b=b, tb=tb, seed=seed, xt=xt, xinv=xi.tolist(), gx=x0, gy=y0)
    os.makedirs(CACHE_DIR, exist_ok=True); pickle.dump(c, open(f, 'wb')); _MEM[key] = c
    return c

if __name__ == '__main__':
    import time
    for tb in map(int, sys.argv[1:]):
        t = time.time(); c = make_curve(tb, 1); print(tb, c['p'], c['r'], round(time.time() - t, 1), 's')
