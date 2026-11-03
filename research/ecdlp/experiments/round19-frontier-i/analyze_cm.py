import json, glob, os, random
from analyze import fit, ev
rows = []
for d in ev:
    if d['argv'][2] == 'CM':
        rows += [json.loads(l) for l in d['output'].splitlines() if l.startswith('{')]
rows.sort(key=lambda r: r['p'])
xs = [r['p'] for r in rows]; ys = [r['P_cm'] for r in rows]
f = fit(xs, ys, betas=[b / 100 for b in range(-120, -10, 1)] and [-b / 100 for b in range(10, 120)])
# fit() uses x**b with negative beta: gamma free
print('P_cm ~ alpha p^beta + gamma:', f, ' n=', len(xs))
rng = random.Random(3); bs = []
for _ in range(400):
    idx = [rng.randrange(len(xs)) for _ in xs]
    xx = [xs[i] for i in idx]; yy = [ys[i] for i in idx]
    if len(set(xx)) < 6: continue
    bs.append(fit(xx, yy, betas=[-b / 100 for b in range(10, 120)])[1])
bs.sort(); print('beta 95% CI (bootstrap over primes):', bs[int(.025 * len(bs))], bs[int(.975 * len(bs))])
g0 = fit(xs, ys, betas=[-0.5]); print('fixed beta=-1/2:', g0)
print('P_cm*sqrt(p):', [round(y * x ** .5, 2) for x, y in zip(xs, ys)])
w = [r['weight_frac_ascent_lt_sqrtp'] for r in rows]
print('weight fraction of CM classes with ascent cost < sqrt p: min %.2f mean %.3f' % (min(w), sum(w) / len(w)))
print('max min_ascent_cost', max(r['min_ascent_cost'] for r in rows), ' at largest p', rows[-1]['p'])
