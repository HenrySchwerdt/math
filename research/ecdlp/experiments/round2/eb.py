"""E-B: independence of coordinate predicates of [k]P from k mod m, lag-1 autocorrelation, DFT. See PROTOCOL.md."""
import sys, os, json, math, random, time
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from toyec import Curve, is_prime
import stats

NCURVES, PLO, PHI = 120, 1000, 100000
MODS = (2, 3, 4, 5, 8)
PREDS = ('A_x_QR', 'B_y_QR', 'C_x_even')
TESTS = [f'{pr}:{t}' for pr in PREDS for t in [f'chi2_m{m}' for m in MODS] + ['lag1', 'dft']]
ALPHA = 0.01
SEED = None


def gen_curve(rng):
    while True:
        p = int(math.exp(rng.uniform(math.log(PLO), math.log(PHI))))
        if not (PLO <= p <= PHI) or not is_prime(p):
            continue
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            continue
        E = Curve(a, b, p)
        pts = E.points()
        r = len(pts)
        if r == p or r < 5 or not is_prime(r):
            continue
        return E, r, pts[rng.randrange(1, r)]


def half_sequence(E, P, h):
    out, R = [], P
    for _ in range(h):
        out.append(R)
        R = E.add(R, P)
    return out


def tests_for(bits, k):
    """bits: 0/1 numpy array indexed by k (k array holds the integers k). Returns {test: p}."""
    N = len(bits)
    res = {}
    for m in MODS:
        tab = np.zeros((2, m))
        for v in (0, 1):
            tab[v] = np.bincount(k[bits == v] % m, minlength=m)
        rows, cols = tab.sum(1), tab.sum(0)
        if rows.min() == 0:
            res[f'chi2_m{m}'] = 1.0
            continue
        exp = np.outer(rows, cols) / N
        res[f'chi2_m{m}'] = stats.chi2_sf(float(((tab - exp) ** 2 / exp).sum()), m - 1)
    s = 2.0 * bits - 1.0
    s = s - s.mean()
    var = float((s * s).mean())
    if var == 0:
        res['lag1'] = res['dft'] = 1.0
        return res
    r1 = float((s[:-1] * s[1:]).sum()) / float((s * s).sum())
    res['lag1'] = stats.norm_two_sided(r1 * math.sqrt(N))
    S = np.fft.rfft(s)
    M = (N - 1) // 2
    t = float((np.abs(S[1:M + 1]) ** 2).max()) / (N * var)
    res['dft'] = stats.max_exp_p(t, M)
    return res


def controls(rng, N, k):
    ctl = {}
    u = lambda: np.array([rng.random() for _ in range(N)])
    ctl['null_iid'] = [(u() < 0.5).astype(int) for _ in range(3)]
    ctl['inject_period3'] = [(u() < np.where(k % 3 == 0, 0.6, 0.45)).astype(int) for _ in range(1)]
    seqs = []
    b = [1 if rng.random() < 0.5 else 0]
    for i in range(1, N):
        b.append(b[-1] if rng.random() < 0.55 else 1 - b[-1])
    ctl['inject_lag1'] = [np.array(b)]
    ctl['inject_sinusoid'] = [(u() < 0.5 + 0.05 * np.cos(2 * np.pi * 0.1237 * k)).astype(int)]
    return ctl


def one_curve(ci):
    rng = random.Random(f'{SEED}-{ci}')
    E, r, P = gen_curve(rng)
    p = E.p
    h = (r - 1) // 2
    pts = half_sequence(E, P, h)
    k = np.arange(1, h + 1)
    X = np.array([q[0] for q in pts])
    Y = np.array([q[1] for q in pts])
    isqr = np.zeros(p, dtype=bool)
    isqr[(np.arange(p, dtype=np.int64) ** 2) % p] = True      # x = 0 counted as residue
    preds = {'A_x_QR': isqr[X].astype(int), 'B_y_QR': isqr[Y].astype(int), 'C_x_even': (X % 2 == 0).astype(int)}
    pv = {}
    for name, bits in preds.items():
        for t, v in tests_for(bits, k).items():
            pv[f'{name}:{t}'] = v
    ctl = {}
    for cname, seqs in controls(rng, h, k).items():
        ctl[cname] = [tests_for(bits, k) for bits in seqs]
    return {'index': ci, 'p': p, 'a': E.a, 'b': E.b, 'r': r, 'P': list(P), 'h': h,
            'freq': {n: float(b.mean()) for n, b in preds.items()}, 'pvals': pv, 'controls': ctl}


def deciles(ps):
    return np.histogram(ps, bins=10, range=(0, 1))[0].tolist()


def summarize(curves):
    n = len(curves)
    ntests = len(TESTS) * n
    thr = ALPHA / ntests
    out = {'n_curves': n, 'n_tests': ntests, 'alpha_fwer': ALPHA, 'alpha_per_test': thr, 'per_test': {}}
    allp, rej = [], []
    for t in TESTS:
        ps = [c['pvals'][t] for c in curves]
        D, P = stats.ks_uniform(ps)
        out['per_test'][t] = {'min_p': min(ps), 'frac_lt_0.05': sum(p < 0.05 for p in ps) / n,
                              'frac_lt_0.01': sum(p < 0.01 for p in ps) / n, 'KS_D': D, 'KS_p': P,
                              'n_bonf_reject': sum(p < thr for p in ps), 'deciles': deciles(ps)}
        allp += ps
    D, P = stats.ks_uniform(allp)
    out['pooled'] = {'n': len(allp), 'min_p': min(allp), 'min_p_bonferroni': min(1.0, min(allp) * ntests),
                     'frac_lt_0.05': sum(p < 0.05 for p in allp) / len(allp), 'frac_lt_0.01': sum(p < 0.01 for p in allp) / len(allp),
                     'KS_D': D, 'KS_p': P, 'deciles': deciles(allp), 'n_bonf_reject': sum(p < thr for p in allp)}
    ks_all = [v['KS_p'] for v in out['per_test'].values()] + [P]
    out['n_KS_reject_bonf(0.01/22)'] = sum(p < 0.01 / 22 for p in ks_all)
    out['min_KS_p'] = min(ks_all)
    worst = sorted(((c['pvals'][t], c['index'], c['p'], t) for c in curves for t in TESTS))[:5]
    out['five_smallest_p'] = [{'p': w[0], 'curve': w[1], 'prime': w[2], 'test': w[3]} for w in worst]
    # controls
    ctl = {}
    for cname in curves[0]['controls']:
        ps_by = {t: [] for t in TESTS[:7]}
        for c in curves:
            for seqres in c['controls'][cname]:
                for t, v in seqres.items():
                    ps_by.setdefault(t, []).append(v)
        # control predicates use generic test names (no predicate prefix): recompute names
        allc = [v for t in ps_by for v in ps_by[t]]
        ctl[cname] = {'n': len(allc), 'KS_p_pooled': stats.ks_uniform(allc)[1], 'frac_lt_0.05': sum(v < 0.05 for v in allc) / len(allc),
                      'bonf_reject_rate_by_test': {t: sum(v < thr for v in ps_by[t]) / len(ps_by[t]) for t in ps_by if ps_by[t]},
                      'min_p': min(allc)}
    out['controls'] = ctl
    return out


if __name__ == '__main__':
    stats.selftest()
    SEED = int(sys.argv[1])
    t0 = time.time()
    with Pool(4) as pool:
        curves = pool.map(one_curve, range(NCURVES), chunksize=1)
    res = {'seed': SEED, 'curves': curves, 'summary': summarize(curves), 'runtime_s': time.time() - t0}
    json.dump(res, open(os.path.join(HERE, sys.argv[2]), 'w'))
    print(json.dumps(res['summary'], indent=1))
    print('runtime', res['runtime_s'])
