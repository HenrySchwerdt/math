import numpy as np, json, random
from math import log2
from ecinv import is_prime
rng = np.random.default_rng(12345)
res = []
for e in range(10, 17):
    p = (1 << e) + 1
    while not (is_prime(p) and p % 3 == 1): p += 1
    # j=0 traces: p = x^2 + 3 y^2
    for y in range(1, int((p/3)**.5) + 2):
        x2 = p - 3*y*y
        if x2 >= 0 and int(x2**.5 + .5)**2 == x2: x = int(x2**.5 + .5); break
    T = {2*x, -2*x, x+3*y, -(x+3*y), x-3*y, -(x-3*y)}
    xs = np.arange(p, dtype=np.int64)
    chi = np.full(p, -1, dtype=np.int64); chi[0] = 0
    chi[(xs*xs) % p] = 1; chi[0] = 0
    x3 = (xs**3) % p
    hit = tot = 0
    while tot < 4000:
        A, B = int(rng.integers(0, p)), int(rng.integers(0, p))
        if (4*A**3 + 27*B*B) % p == 0: continue
        v = (x3 + A*xs + B) % p
        tr = -int(chi[v].sum())
        tot += 1; hit += tr in T
    res.append(dict(p=p, hit=hit, tot=tot, frac=hit/tot))
    print(res[-1], flush=True)
json.dump(res, open('out_t3.json', 'w'))
