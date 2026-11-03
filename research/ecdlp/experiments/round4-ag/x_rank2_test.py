# g=x: sum over affine Q = -tr(F^n|H^1) - 1 (O contributes chi(1)=1). Test rank<=2 via Newton: p3=(3 p1 p2 - p1^3)/2 and |e2|=p.
import random, json, numpy as np
import ext_field_test as T
from common import *
rng = T.rng
rows = []
for p in [11, 13, 17, 19, 23, 29, 31]:
    L = legendre_table(p)
    for _ in range(2):
        res = random_prime_order_curve(p, rng, L)
        if not res or res[2] < 5: continue
        a, b, r = res
        out = T.run_curve(p, a, b, r)
        P = [-(out[n][1] + 1) for n in (1, 2, 3)]   # p_n = tr F^n on H^1 (c = 1..r-1; O adds chi=1*psi(O)=1)
        p1, p2, p3 = P
        e2 = (p1*p1 - p2)/2
        rows.append(dict(p=p, a=a, b=b, r=r, newton_resid_max=round(float(np.max(np.abs(p3 - (3*p1*p2 - p1**3)/2))/p**1.5), 8),
                         weight_dev_max=round(float(np.max(np.abs(np.abs(e2) - p))/p), 8)))
for rw in rows: print(json.dumps(rw))
