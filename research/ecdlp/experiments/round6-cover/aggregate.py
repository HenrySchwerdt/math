"""Aggregate results_bits*.json into results.json (medians, scaling fits, decision rule)."""
import json, glob, math, statistics as st
import numpy as np

files = sorted(glob.glob('results_bits*.json'))
curves = []
for f in files:
    curves += json.load(open(f))['curves']
by = {}
for c in curves:
    by.setdefault(c['bits'], []).append(c)
out = dict(master_seed=20261109, sizes={}, fit={}, decision={})
for bits in sorted(by):
    cs = by[bits]
    p = cs[0]['p']
    row = dict(p=p, n_curves=len(cs), sqrt_p=math.sqrt(p),
               bsgs_ec_adds_median=st.median(c['bsgs']['ec_adds'] for c in cs),
               checks_all_pass=all(c['checks'].get('Lpoly_ok', True) and c['checks']['assoc_fail'] == 0 and
                                   c['checks']['comm_fail'] == 0 and c['checks']['inv_fail'] == 0 and
                                   c['checks']['hom_fail'] == 0 and c['checks']['order_fail'] == 0 and
                                   c['checks']['r_piP_is_zero'] for c in cs),
               lpoly_checked=sum('Lpoly_ok' in c['checks'] for c in cs))
    for v in ('A', 'B', 'Bhalf'):
        vs = [c['variants'][v] for c in cs if v in c['variants']]
        if not vs:
            continue
        d = dict(k_correct=sum(x.get('k_correct', False) for x in vs), n=len(vs))
        for key in ('relations', 'trials', 'cantor', 'ec', 'la', 'total', 'time_s', 'rank', 'unknowns_active'):
            d[key + '_median'] = st.median(x[key] for x in vs)
        if v == 'A':
            d['dedup_k_determined'] = sum(x['dedup']['k_determined'] for x in vs)
            d['dedup_rank_median'] = st.median(x['dedup']['rank'] for x in vs)
            d['first_collision_ec_median'] = st.median(x['first_collision_ec'] for x in vs)
            d['first_collision_trial_median'] = st.median(x['first_collision_trial'] for x in vs)
        row[v] = d
    out['sizes'][bits] = row
def fit(vals):
    xs = np.log([out['sizes'][b]['p'] for b in vals]); 
    return xs
for v, key in (('B', 'total'), ('B', 'cantor'), ('B', 'la'), ('B', 'ec'), ('Bhalf', 'total'), ('A', 'total')):
    bs = [b for b in out['sizes'] if v in out['sizes'][b]]
    if len(bs) >= 2:
        xs = np.log([out['sizes'][b]['p'] for b in bs])
        ys = np.log([out['sizes'][b][v][key + '_median'] for b in bs])
        out['fit'][f'{v}.{key}'] = dict(sizes=bs, slope=float(np.polyfit(xs, ys, 1)[0]))
bs = sorted(out['sizes'])
big = out['sizes'][bs[-1]]
ok = {v: (big[v]['k_correct'] == big[v]['n']) for v in ('A', 'B') if v in big}
for v in ok:
    tot = big[v]['total_median']
    ex = out['fit'].get(f'{v}.total', {}).get('slope')
    out['decision'][v] = dict(all_k_correct_at_largest=ok[v], total_median=tot, half_sqrt_p=0.5 * big['sqrt_p'],
                              ratio_total_over_half_sqrt_p=tot / (0.5 * big['sqrt_p']), exponent=ex,
                              falsifies=bool(ok[v] and tot < 0.5 * big['sqrt_p'] and ex is not None and ex < 0.5))
out['decision']['hypothesis_falsified'] = any(d['falsifies'] for k, d in out['decision'].items() if isinstance(d, dict))
json.dump(out, open('results.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
