import json, glob, math, collections, sys
import numpy as np
sys.path.insert(0, '../round12-inventor-a')
from common import fit
rows = [json.loads(l) for f in sorted(glob.glob('out_e2_[abc].jsonl')) for l in open(f)]
ctl = [json.loads(l) for l in open('out_e2_ctl.jsonl')]
print('E2 COS: n=%d success %d/%d (index calculus), rho_dp success %d' % (len(rows), sum(r['ok'] for r in rows), len(rows), sum(r['rho_k_ok'] for r in rows)))
gm = lambda v: math.exp(sum(map(math.log, v)) / len(v))
print('bits  s(avg)  s/p^1/3  targets  relations  perrel_finder_adds  p^1/6  total_model(gm)  total/r^(2/3)  rho_analytic  ratio  rho_dp(gm)  tot_meas(gm)')
by = collections.defaultdict(list)
for r in rows: by[r['bits']].append(r)
for b in sorted(by):
    rs = by[b]; r_ = gm([x['r'] for x in rs]); p_ = gm([x['p'] for x in rs])
    perrel = gm([(x['finder_adds']) / x['relations'] for x in rs])
    print(b, round(sum(x['s'] for x in rs) / len(rs), 1), round(gm([x['s'] / x['p'] ** (1 / 3) for x in rs]), 2), round(sum(x['targets'] for x in rs) / 3), round(sum(x['relations'] for x in rs) / 3),
          round(perrel, 1), round(p_ ** (1 / 6), 2), round(gm([x['total_model'] for x in rs])), round(gm([x['total_model'] / x['r'] ** (2 / 3) for x in rs]), 2),
          round(gm([x['rho_analytic'] for x in rs])), round(gm([x['total_model'] / x['rho_analytic'] for x in rs]), 1), round(gm([x['rho_adds'] for x in rs])), round(gm([x['total_meas'] for x in rs])))
X = [math.log2(r['r']) for r in rows]
for name, key in (('model (Wiedemann LA)', 'total_model'), ('measured dense elimination', 'total_meas'), ('finder-only (build+per-target adds)', None)):
    Y = [math.log2(r[key] if key else r['build_adds'] + r['finder_adds']) for r in rows]
    f = fit(X, Y); print('fit %-38s alpha=%.3f [%.3f, %.3f] n=%d' % (name, f['alpha'], f['lo'], f['hi'], f['n']))
f = fit(X, [math.log2(r['rho_analytic']) for r in rows]); print('rho analytic', round(f['alpha'], 3))
f = fit(X, [math.log2(r['rho_adds']) for r in rows]); print('rho_dp measured (setup-dominated at small r)', round(f['alpha'], 3), '[%.3f, %.3f]' % (f['lo'], f['hi']))
f = fit(X, [math.log2(r['total_model'] / r['rho_analytic']) for r in rows]); print('ratio F/rho_analytic exponent', round(f['alpha'], 3), '[%.3f, %.3f]' % (f['lo'], f['hi']), '(theory 1/6=0.167)')
print('controls (total_model, geometric mean) vs COS same bits:')
for b in (20, 24, 28):
    base = gm([x['total_model'] for x in rows if x['bits'] == b])
    for k in ('RND', 'SX'):
        c = [x for x in ctl if x['bits'] == b and x['base'] == k]
        print(b, k, len(c), 'ok', all(x['ok'] for x in c), 'ratio to COS %.2f' % (gm([x['total_model'] for x in c]) / base), 's', [x['s'] for x in c], 'rel/target', [round(x['relations'] / x['targets'], 2) for x in c])
# decision
bits_max = max(by); ratio30 = gm([x['total_model'] / x['rho_analytic'] for x in by[bits_max]])
fm = fit(X, [math.log2(r['total_model']) for r in rows])
print('DECISION: success', all(r['ok'] for r in rows), 'alpha_hi', round(fm['hi'], 3), 'ratio@max', round(ratio30, 1),
      '->', 'WINS' if (all(r['ok'] for r in rows) and fm['hi'] < 0.5 and ratio30 < 1) else ('CONSTANT-ONLY' if ratio30 < 1 else 'NO-ADVANTAGE'))
# LA bound: smallest r where 4 s^2 with s=(3r)^(1/3) exceeds sqrt(r)
for r in (2 ** 10, 2 ** 20, 2 ** 40, 2 ** 80, 2 ** 160):
    s = (3 * r) ** (1 / 3); print('r=2^%d: s_floor=%.3g  LA 4s^2=%.3g  sqrt(r)=%.3g  ratio=%.3g' % (math.log2(r), s, 4 * s * s, math.sqrt(r), 4 * s * s / math.sqrt(r)))
