"""POST-HOC (not pre-registered) symmetry-aware recalibration of the E-A Fourier null. See report, 'Deviation'."""
import sys, os, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stats
from ea import fourier, FAMILY


def sym_class(c):
    al, be, ga, de = c
    if be == 0 and ga == 0:
        return 'even'    # f(-Q) = f(Q)
    if al == 0 and de == 0:
        return 'odd'     # f(-Q) = -f(Q)
    return 'generic'


def p_sym(F, r, cls):
    t = r * F * F
    if cls == 'odd':     # real S, S^2/r ~ chi2_1, r-1 distinct frequencies
        q = math.erfc(math.sqrt(t / 2))
        M = r - 1        # S_c real but S_c != S_{-c}: r-1 distinct real coefficients
    elif cls == 'even':  # |S|^2/r ~ Exp(1), (r-1)/2 distinct frequencies
        q = math.exp(-t)
        M = (r - 1) // 2
    else:
        q = math.exp(-t)
        M = r - 1
    return -math.expm1(M * math.log1p(-q)) if q < 1 else 1.0


def null_fn(rng, r, cls, M=2 ** 30):
    n = rng.integers(0, M, size=r)
    n[0] = 0
    if cls != 'generic':
        h = (r - 1) // 2
        n[r - h:] = (n[1:h + 1][::-1] * (1 if cls == 'even' else -1)) % M
    return n % M, M


out = {}
for tag, fn, seed in (('S1', 'ea_S1.json', 1), ('S2', 'ea_S2.json', 2)):
    d = json.load(open(os.path.join(HERE, fn)))
    rng = np.random.default_rng(777 + seed)
    rows = []
    for c in d['curves']:
        for f in c['family']:
            cls = sym_class(f['coef'])
            rows.append((cls, f['F'], c['r'], p_sym(f['F'], c['r'], cls), f['p_F'], f['coef'], c['index'], c['p']))
    n = len(rows)
    res = {'n_tests': n, 'by_class': {}}
    for cls in ('even', 'odd', 'generic'):
        sub = [x for x in rows if x[0] == cls]
        ps = [x[3] for x in sub]
        D, P = stats.ks_uniform(ps)
        res['by_class'][cls] = {'n_functions': len(set(tuple(x[5]) for x in sub)), 'n': len(sub),
                                'KS_D': D, 'KS_p': P, 'min_p_sym': min(ps),
                                'KS_p_preregistered_null': stats.ks_uniform([x[4] for x in sub])[1]}
    allp = [x[3] for x in rows]
    res['KS_all_sym'] = stats.ks_uniform(allp)
    res['min_p_sym'] = min(allp)
    res['min_p_sym_bonferroni'] = min(1.0, min(allp) * n)
    res['n_reject_sym_bonferroni'] = sum(p < 0.01 / n for p in allp)
    # symmetric empirical null: matched random functions, same curve sizes
    emp = {}
    for cls in ('even', 'odd', 'generic'):
        ps = []
        for c in d['curves']:
            r = c['r']
            for _ in range(150):
                nn, M = null_fn(rng, r, cls)
                ps.append(p_sym(fourier(nn, M)[0], r, cls))
        emp[cls] = {'n': len(ps), 'KS_p_sym_calibration': stats.ks_uniform(ps)[1], 'min_p': min(ps),
                    'frac_below_0.01': sum(p < 0.01 for p in ps) / len(ps)}
    res['empirical_symmetric_null_calibration'] = emp
    out[tag] = res
    pass
json.dump(out, open(os.path.join(HERE, 'ea_posthoc.json'), 'w'), indent=1)
