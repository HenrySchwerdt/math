"""Aggregate results_k*.json -> table + log-log fits -> results_summary.json (readable reference; no new experiments)"""
import json, math, os, glob
H = os.path.dirname(os.path.abspath(__file__))
def fit(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sl = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return sl
S = {'rows': [], 'fits': {}}
byset = {}
for f in sorted(glob.glob(os.path.join(H, 'results_k*.json'))):
    d = json.load(open(f)); p = d['p']; k = d['k']
    names = sorted({n for c in d['curves'] for n in c['sets']})
    for nm in names:
        cs = [c['sets'][nm] for c in d['curves']]; rho = [c['rho_units_w1'] for c in d['curves']]
        m = lambda key: sum(c[key] for c in cs) / len(cs)
        T = m('T_w1'); tot = m('total_w1')
        row = dict(k=k, p=p, set=nm, curves=len(cs), n=m('n'), pi=m('pi_exact'), T_w1=T, T_w10=m('T_w10'), p16=p ** (1 / 6), T_over_p16=T / p ** (1 / 6),
                   total_w1=tot, total_over_sqrtp=tot / math.sqrt(p), rho_w1=sum(rho) / len(rho), total_over_rho=tot / (sum(rho) / len(rho)),
                   LA=m('LA_model'), LA_over_sqrtp=m('LA_model') / math.sqrt(p), T_min_curve=min(c['T_w1'] for c in cs), T_max_curve=max(c['T_w1'] for c in cs),
                   n_over_p13=m('n') / p ** (1 / 3), Mattempt=m('attempt_M') + m('attempt_I'), disagree=sum(c['M1_disagree_vs_exact'] for c in cs))
        S['rows'].append(row); byset.setdefault(nm, []).append(row)
for nm, rs in byset.items():
    rs = [r for r in rs if r['k'] <= 18] if len(rs) > 1 else rs
    lp = [math.log(r['p']) for r in rs]
    S['fits'][nm] = dict(k_range=[rs[0]['k'], rs[-1]['k']], exp_T=fit(lp, [math.log(r['T_w1']) for r in rs]), exp_total=fit(lp, [math.log(r['total_w1']) for r in rs]),
                         exp_n=fit(lp, [math.log(r['n']) for r in rs]), exp_attempt=fit(lp, [math.log(r['Mattempt']) for r in rs]),
                         exp_T_over_n=fit(lp, [math.log(r['T_w1'] / r['n']) for r in rs]))
# include k=20 for B sets in 12..20 fit
for nm in ('PKM-B', 'SX-B', 'RND-B'):
    rs = byset[nm]; lp = [math.log(r['p']) for r in rs]
    S['fits'][nm + '_k12-20'] = dict(exp_T=fit(lp, [math.log(r['T_w1']) for r in rs]), exp_total=fit(lp, [math.log(r['total_w1']) for r in rs]))
json.dump(S, open(os.path.join(H, 'results_summary.json'), 'w'), indent=1)
print('%3s %8s %6s %6s %6s %9s %7s %8s %9s %9s %9s' % ('k', 'set', 'n', 'pi', 'T', 'p^1/6', 'T/p16', 'tot/sqp', 'tot/rho', 'LA/sqp', 'n/p^1/3'))
for r in S['rows']: print('%3d %8s %6.1f %6.3f %6.1f %9.2f %7.1f %8.1f %9.2f %9.2f %9.2f' % (r['k'], r['set'], r['n'], r['pi'], r['T_w1'], r['p16'], r['T_over_p16'], r['total_over_sqrtp'], r['total_over_rho'], r['LA_over_sqrtp'], r['n_over_p13']))
for k, v in S['fits'].items(): print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()})
