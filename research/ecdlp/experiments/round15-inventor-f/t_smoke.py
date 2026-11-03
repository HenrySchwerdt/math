import sys, random, time
sys.path.insert(0, '.')
from f_lib import *
from toyec import Curve
import numpy as np
# correctness of table/decompose against the group law, and supply formula smoke test
inst = gen_instance(16, 1); p, a, b, r = inst['p'], inst['a'], inst['b'], inst['r']
rng = random.Random(1); V = base_coset(p, a, b, inst['d'], rng); E = Curve(a, b, p)
F = Finder3(inst, V); xs = [int(x) for x in F.xs]; print('p', p, 'r', r, 'd', inst['d'], 's', F.s)
bad = tot = 0
for _ in range(400):
    T = E.mul(rng.randrange(1, r), inst['P'])
    for co in F.decompose(T):
        R = None
        for col, c in co.items():
            R = E.add(R, E.mul(c, (xs[col], V[xs[col]])))
        tot += 1; bad += (R != T)
print('decompositions', tot, 'bad', bad)
t = time.time(); res = solve_k(inst, V, 1); print(res, time.time() - t)
