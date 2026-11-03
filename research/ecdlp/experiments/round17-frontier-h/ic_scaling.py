"""Scaling record (outside the success rule): hand index-calculus program prog_ic_ms with cap 400*sqrt(r) and rho_dp, sizes 10-14,
curve seeds {600,601,602}-style new seeds 800-802, 20 instances/curve. Fits cost = alpha*r^beta is NOT used; prints cost/sqrt(r), cost/r, success."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsl2 import *
out = {}
for tb in range(10, 15):
    row = {}
    for nm, f, cf in (('rho_dp', prog_rho_dp, 12.0), ('ic_ms', prog_ic_ms, 400.0)):
        tot = ok = n = 0
        for sd in (800, 801, 802):
            c = make_curve(tb, sd)
            for k, s in instances(c, 20, 3):
                res, cost, _ = run(f(), c, k, s, cf); tot += cost / c['r'] ** .5; ok += res == k; n += 1
        row[nm] = dict(cost_over_sqrt_r=tot / n, success=ok / n)
    out[tb] = row; print(tb, row, flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_ic_scaling.json'), 'w'))
