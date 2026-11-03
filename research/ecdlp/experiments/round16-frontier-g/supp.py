"""POST-HOC supplementary (not pre-registered): extrapolation beyond 2^16 and overhead model fit for programs that passed the gate."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsl import *
progs = {n: f() for n, f in BASELINES.items() if n in ('bsgs', 'rho_dp')}
for tag in sys.argv[1:]:
    ch = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'out_evolve_{tag}.json')))['champions'][0]['prog']
    progs[tag] = ([tuple(x) for x in ch[0]], [tuple(x) for x in ch[1]])
res = {n: [] for n in progs}
for tb in (13, 14, 15, 16, 17, 18):
    c = make_curve(tb, 300)
    for n, p in progs.items():
        ks = instances(c, 80 if tb < 18 else 50, 7); tot = 0; ok = 0
        for k, s in ks:
            r_, cost, _ = run(p, c, k, s); tot += cost; ok += r_ == k
        res[n].append((tb, c['r'], tot / len(ks), ok / len(ks)))
        print(n, tb, c['r'], round(tot / len(ks) / math.sqrt(c['r']), 3), 'succ', round(ok / len(ks), 2), flush=True)
def fit(rows, lo, hi):
    rs = [(r, c) for tb, r, c, _ in rows if lo <= tb <= hi]
    xs = [math.log(r) for r, c in rs]; ys = [math.log(c) for r, c in rs]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
for n, rows in res.items():
    # model cost = alpha*sqrt(r) + gamma by least squares
    pts = [(math.sqrt(r), c) for tb, r, c, _ in rows]
    sx = sum(a for a, _ in pts); sy = sum(b for _, b in pts); sxx = sum(a * a for a, _ in pts); sxy = sum(a * b for a, b in pts); m = len(pts)
    al = (m * sxy - sx * sy) / (m * sxx - sx * sx); ga = (sy - al * sx) / m
    print(n, 'slope13-16 %.3f slope17-18 %.3f slope13-18 %.3f' % (fit(rows, 13, 16), fit(rows, 17, 18), fit(rows, 13, 18)), '| cost=%.2f*sqrt(r)+%.1f' % (al, ga))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_supp_extrap.json'), 'w'))
