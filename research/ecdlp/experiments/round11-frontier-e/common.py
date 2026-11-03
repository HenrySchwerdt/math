import sys, random
import numpy as np
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime

def prime_order_curve(rng, lo=1 << 19):
    p = lo
    while True:
        p += 1
        if not is_prime(p):
            continue
        xs = np.arange(p, dtype=np.int64)
        sq = np.zeros(p, dtype=np.int32)
        np.add.at(sq, (xs * xs) % p, 1)
        for _ in range(60):
            a, b = rng.randrange(p), rng.randrange(p)
            if (4 * a ** 3 + 27 * b * b) % p == 0:
                continue
            f = ((xs * xs % p) * xs + a * xs + b) % p
            r = 1 + int(sq[f].sum())
            if r != p and is_prime(r) and r > 1000:
                return Curve(a, b, p), r

def half_orbit(E, r):
    P = None
    for x in range(2, E.p):
        v = (x ** 3 + E.a * x + E.b) % E.p
        if pow(v, (E.p - 1) // 2, E.p) == 1:
            for y in range(E.p):
                if y * y % E.p == v:
                    P = (x, y); break
            break
    M = (r - 1) // 2
    vals = np.zeros(M + 1, dtype=np.int64)
    R = None
    for k in range(1, r):
        R = E.add(R, P)
        if k <= M:
            vals[k] = R[0]
        elif k == M + 1:
            assert R[0] == vals[M]  # x_{M+1} = x_{r-M-1} = x_M
    return vals[1:]            # vals[k-1] = x_k, k=1..M

def fold(vals, r):
    """full sequence X[0..r-1], X[0]=0 (unused), X[k]=X[r-k]=vals[k-1]"""
    M = len(vals)
    X = np.zeros(r, dtype=np.int64)
    X[1:M + 1] = vals
    X[r - np.arange(1, M + 1)] = vals
    return X
