"""E1: m=3 relation supply. N4 = #closed quadruples sum eps_i u_i = 0 (4 distinct base x), predicted 8*C(s,4)/r ~ s^4/(3r).
Bases of equal size s ~ 2.5 p^{1/3}: RND, SX (smallest x), COS (mu_d coset), PHI2/PHI3 (random monic poly of degree 2/3 on t=0,1,2..), POW3 (g t^3, t=1,2..).
Usage: f1_supply.py BITS SEED"""
import sys, json, random, math
from f_lib import *
bits, seed = int(sys.argv[1]), int(sys.argv[2])
inst = gen_instance(bits, seed, cfac=5.0); p, a, b, r = inst['p'], inst['a'], inst['b'], inst['r']
rng = random.Random(77 * bits + seed)
Vc = base_coset(p, a, b, inst['d'], rng); s = len(Vc)
bases = dict(COS=Vc, RND=base_random(p, a, b, s, rng), SX=base_smallx(p, a, b, s),
             PHI2=base_phi(p, a, b, s, 2, rng), PHI3=base_phi(p, a, b, s, 3, rng), POW3=base_phi_power(p, a, b, s, 3, rng))
for name, V in bases.items():
    xs, ys = arrays(V); s_ = len(xs)
    coll, adds = closed_quadruples(p, a, xs, ys)
    n4 = coll / 3.0
    pred = 8 * math.comb(s_, 4) / r
    print(json.dumps(dict(exp='supply', bits=bits, seed=seed, base=name, p=p, r=r, s=s_, s_over_p13=s_ / p ** (1 / 3), N4_coll=coll,
                          N4=n4, pred=pred, ratio=(n4 / pred if pred else None), pair_adds=adds)), flush=True)
