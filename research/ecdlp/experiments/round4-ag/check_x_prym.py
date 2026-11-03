# Check 1: psi trivial, g=x:  sum_{Q affine} chi(x(Q)) = -a(E'') ?  E'': Y^2 = X^3 + a X^2 + b^2
# Also sum_{x} chi(x f(x)) vs the twist. Seeds recorded.
import random, numpy as np
from common import *
rng = random.Random(20261103)
bad_plain = bad_twist = tot = 0
for p in [101, 211, 503, 1009, 2003, 4001]:
    L = legendre_table(p); x = np.arange(p, dtype=np.int64)
    for _ in range(20):
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        if (4*a**3+27*b**2) % p == 0: continue
        Sx = int(sum(L[xx] * (1 + L[(xx**3+a*xx+b) % p]) for xx in range(p)))  # sum over affine Q of chi(x(Q))
        a2 = -int(L[(x**3 + a*x*x + b*b) % p].sum())   # trace of E''
        tot += 1
        if Sx == -a2 - 1: pass
        elif Sx == a2 - 1: bad_plain += 1   # would indicate quadratic twist
        else: bad_twist += 1
print("curves", tot, "S==-a(E'')-1", tot-bad_plain-bad_twist, "S==a(E'')-1", bad_plain, "other", bad_twist)
