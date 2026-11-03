import json, sys, math
import numpy as np
d = json.load(open(sys.argv[1])); rows = d['rows']
preds = []
for r in rows:
    if r['pred'] not in preds: preds.append(r['pred'])
T99 = 2.687  # t df=46 two-sided 99%
out = []
print('seed', d['seed'])
print('%-11s %-5s %8s %8s %8s %8s %8s %8s' % ('pred', 'bkt', 'meanM', 'maxM', 'M/lnr', 'mean', 'm2', 'M/(p/r)'))
summ = {}
for pr in preds:
    rs = [r for r in rows if r['pred'] == pr]
    for b in range(4):
        q = [r for r in rs if r['bucket'] == b]
        print('%-11s %-5d %8.2f %8.2f %8.3f %8.3f %8.3f %8.2f' % (pr, b, np.mean([r['M'] for r in q]), max(r['M'] for r in q),
              np.mean([r['M_over_lnr'] for r in q]), np.mean([r['mean'] for r in q]), np.mean([r['m2'] for r in q]),
              max(r['M'] * r['r'] / r['p'] for r in q)))
    lr = np.array([math.log(r['r']) for r in rs]); M = np.array([r['M'] for r in rs])
    A = np.vstack([lr, np.ones_like(lr)]).T
    beta, res, *_ = np.linalg.lstsq(A, M, rcond=None)
    resid = M - A @ beta; s2 = resid @ resid / (len(M) - 2)
    se = math.sqrt(s2 / ((lr - lr.mean()) ** 2).sum())
    m2 = np.array([r['m2'] for r in rs]); mean_m2 = m2.mean(); se_m2 = m2.std(ddof=1) / math.sqrt(len(m2))
    deg = rs[0]['deg']
    bound_ok = all(r['M'] <= 4 * (deg or 0) ** 2 * r['p'] / r['r'] for r in rs) if deg else None
    summ[pr] = dict(slope=beta[0], ci=[beta[0] - T99 * se, beta[0] + T99 * se], m2=mean_m2, m2_se=se_m2, bound4d2_all=bound_ok,
                    max_parseval_err=max(r['parseval_err'] for r in rs), mean_dev=max(abs(r['mean'] - r['mean_expected']) for r in rs))
    print('  ->', pr, {k: (np.round(v, 3).tolist() if not isinstance(v, (bool, type(None))) else v) for k, v in summ[pr].items()})
orc = d['oracle']; print('oracle n=%d max abs diff %.3e' % (len(orc), max(o['abs_diff'] for o in orc)))
lk = d['leak']
for pr in preds:
    q = [l for l in lk if l['pred'] == pr]
    print('leak %-11s mean chi2 mod2 %.2f (df1) mod3 %.2f (df2) max %.2f/%.2f' % (pr, np.mean([l['chi2_mod2'] for l in q]), np.mean([l['chi2_mod3'] for l in q]),
          max(l['chi2_mod2'] for l in q), max(l['chi2_mod3'] for l in q)))
