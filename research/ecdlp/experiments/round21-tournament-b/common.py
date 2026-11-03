import random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
from toyec import Curve, is_prime
import numpy as np

def find_curves(lo, hi, n, tag, need_1mod6=True):
    rng = random.Random(f'r21b-{tag}')
    out = []
    while len(out) < n:
        p = rng.randrange(lo, hi) | 1
        if not is_prime(p) or (need_1mod6 and p % 6 != 1):
            continue
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        try:
            E = Curve(a, b, p)
        except ValueError:
            continue
        r = E.order()
        if not is_prime(r) or r < 100:
            continue
        P = E.points()[1 + rng.randrange(r - 1)]
        out.append((E, P, r))
    return out

def chain(E, P, r):
    """multiples jP for j=0..r-1 as arrays (x,y) with j=0 -> (-1,-1)."""
    xs = np.full(r, -1, dtype=np.int64); ys = np.full(r, -1, dtype=np.int64)
    R = None
    for j in range(r):
        if R is not None:
            xs[j], ys[j] = R
        R = E.add(R, P)
    return xs, ys
