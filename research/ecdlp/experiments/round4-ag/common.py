import sys, random
import numpy as np
sys.path.insert(0, '/home/user/math/research/ecdlp/experiments/lib')
from toyec import Curve, is_prime

def legendre_table(p):
    t = -np.ones(p, dtype=np.int64); t[0] = 0
    t[(np.arange(1, p, dtype=np.int64) ** 2) % p] = 1
    return t

def count_points(a, b, p, L):
    x = np.arange(p, dtype=np.int64)
    return 1 + p + int(L[(x**3 + a*x + b) % p].sum())

def random_prime_order_curve(p, rng, L):
    for _ in range(4000):
        a, b = rng.randrange(p), rng.randrange(p)
        if (4*a**3 + 27*b**2) % p == 0: continue
        n = count_points(a, b, p, L)
        if is_prime(n) and n > 2:
            return a, b, n
    return None

def orbit(E, r):
    """x,y of kP for k=0..r-1 (k=0 -> None) with P a point; r prime so any non-O point generates."""
    p = E.p; L = legendre_table(p)
    while True:
        x = random.randrange(p); rhs = (x**3 + E.a*x + E.b) % p
        if L[rhs] == 1:
            y = next(y for y in range(p) if y*y % p == rhs); break
    P = (x, y); pts = [None]; Q = None
    for k in range(1, r):
        Q = E.add(Q, P); pts.append(Q)
    return pts
