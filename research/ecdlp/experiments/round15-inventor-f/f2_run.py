"""E2: end-to-end m=3 index calculus (hash 2+1 finder over pair table, sparse-incremental elimination) vs rho_dp on the same instance.
Usage: f2_run.py BITS SEED BASE   (BASE in COS,RND,SX)"""
import sys, json, random, math, time
from f_lib import *
sys.path.insert(0, os.path.join(HERE, '..', 'round12-inventor-a'))
from common import rho_dp
bits, seed, kind = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
inst = gen_instance(bits, seed, cfac=1.6); p, a, b, r = inst['p'], inst['a'], inst['b'], inst['r']
rng = random.Random(99991 * seed + bits)
Vc = base_coset(p, a, b, inst['d'], rng)
V = Vc if kind == 'COS' else (base_random(p, a, b, len(Vc), rng) if kind == 'RND' else base_smallx(p, a, b, len(Vc)))
t0 = time.time(); res = solve_k(inst, V, seed); wall = time.time() - t0
s = res['s']; fb_mults = inst['d'] * 2 * int(math.log2(p) + 1)
la_model = 4 * s * s                       # Wiedemann-style model: 4 nonzeros/row, s^2 matrix-vector work (favours candidate)
total_model = res['build_adds'] + res['finder_adds'] + res['gen_adds'] + (fb_mults + la_model) / 10.0
total_meas = res['build_adds'] + res['finder_adds'] + res['gen_adds'] + (fb_mults + res['la_mults']) / 10.0
out = dict(exp='e2', bits=bits, seed=seed, base=kind, p=p, r=r, d=inst['d'], **res, fb_mults=fb_mults, la_model=la_model,
           total_model=total_model, total_meas=total_meas, wall=wall, rho_analytic=math.sqrt(math.pi * r / 2))
if kind == 'COS':
    kk, n = rho_dp(inst, rng_seed=seed); out['rho_k_ok'] = (kk == inst['k']); out['rho_adds'] = n
print(json.dumps(out), flush=True)
