import sys, random
from lib18 import *
rng = random.Random(1)
for bits in (12, 16, 20):
    I = gen_instance(bits, 0, 1.5); E = I['E']; p = I['p']; a = I['a']; b = I['b']
    assert all(E.on(c) for c in I['cls']); print(bits, p, I['d'], len(I['cls']))
    for _ in range(50):
        u, v, w = [rng.randrange(p) for _ in range(3)]
        c2, c1, c0 = S3_coeffs_in_v(a, b, p, u, w)
        assert (c2 * v * v + c1 * v + c0) % p == S3(a, b, p, u, v, w)
    # S3 vanishes on collinear triples
    P, Q = E.rand_point(rng), E.rand_point(rng); Rr = E.add(P, Q)
    assert S3(a, b, p, P[0], Q[0], Rr[0]) == 0
    D = pair_sums(E, I['cls']); print(len(D), len(I['cls']) ** 2)
    cl = I['cls']; pts = [rng.choice(cl) for _ in range(4)]
    R = E.add(E.add(pts[0], pts[1]), E.add(pts[2], pts[3]))
    if R is not None: assert mitm_test(E, D, R) is not None
print('ok')
