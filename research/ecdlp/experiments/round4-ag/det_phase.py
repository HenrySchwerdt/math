# Phase of det = lambda1*lambda2 / p on the rank-2 pieces: g=x (e2 from p1,p2) and g=y (e2=(A^2-B)/2, A=zeta*S1,B=conj(zeta)*S2).
import json, cmath, math, numpy as np
import ext_field_test as T
from common import *
rng = T.rng
res = []
for p in [13, 19, 23, 29]:
    L = legendre_table(p)
    for _ in range(2):
        c = random_prime_order_curve(p, rng, L)
        if not c or c[2] < 5: continue
        a, b, r = c; out = T.run_curve(p, a, b, r)
        p1, p2 = [-(out[n][1] + 1) for n in (1, 2)]
        ex = (p1*p1 - p2)/2/p
        z = cmath.exp(2j*math.pi/3)
        best = None
        for zz in (z, z.conjugate()):
            A = zz*out[1][0]; B = zz.conjugate()*out[2][0]; ey = (A*A - B)/2/p
            best = ey if best is None else best
        res.append(dict(p=p, r=r, x_det_over_p_distinct=sorted(set(np.round(ex.real, 4).tolist()))[:6], x_det_imag_max=round(float(np.abs(ex.imag).max()), 6),
                        y_det_phase_sample=[round(float(cmath.phase(v)/math.pi), 3) for v in best[:6]] if False else None))
for rr in res: print(json.dumps(rr))
