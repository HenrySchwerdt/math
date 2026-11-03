"""Collect evidence outputs (runs/*.evidence for RUN-eaefc23d) and fit cost models. No scipy: grid over beta, linear LS for (alpha,gamma)."""
import json, glob, os, random, statistics as st, math
RUN = 'RUN-eaefc23d-d4ef-4a82-a3d1-42b2ca008b1e'
rdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'runs')
ev = []
for f in sorted(glob.glob(os.path.join(rdir, RUN + '-command-*.evidence'))):
    d = json.load(open(f)); ev.append(d)
def lines(prefix_pred):
    out = []
    for d in ev:
        if prefix_pred(d['argv']):
            assert not d.get('truncated'), ('truncated', d['argv'])
            for ln in d['output'].splitlines():
                if ln.startswith('{'): out.append(json.loads(ln))
    return out
here = os.path.dirname(os.path.abspath(__file__))

def fit(xs, ys, w=None, betas=None):
    """y ~ alpha x^beta + gamma ; weights 1/y^2 (relative error); returns (sse, beta, alpha, gamma)"""
    betas = betas or [b / 100 for b in range(20, 141, 2)]
    best = None
    for b in betas:
        u = [x ** b for x in xs]; wt = [1 / (y * y) for y in ys]
        S = sum(wt); Su = sum(w_ * a for w_, a in zip(wt, u)); Sy = sum(w_ * a for w_, a in zip(wt, ys))
        Suu = sum(w_ * a * a for w_, a in zip(wt, u)); Suy = sum(w_ * a * c for w_, a, c in zip(wt, u, ys))
        det = S * Suu - Su * Su
        if abs(det) < 1e-30: continue
        al = (S * Suy - Su * Sy) / det; ga = (Suu * Sy - Su * Suy) / det
        sse = sum(w_ * (al * a + ga - c) ** 2 for w_, a, c in zip(wt, u, ys))
        if best is None or sse < best[0]: best = (sse, b, al, ga)
    return best

def fit_sqrt(xs, ys):
    b = fit(xs, ys, betas=[0.5]); return b

def boot(rows_by_bits, B=300, seed=1, fixed=None):
    """bootstrap over instances inside each size; returns beta samples"""
    rng = random.Random(seed); res = []
    keys = sorted(rows_by_bits)
    for _ in range(B):
        xs = []; ys = []
        for k in keys:
            rows = rows_by_bits[k]; samp = [rows[rng.randrange(len(rows))] for _ in rows]
            xs.append(st.mean(r for r, _ in samp)); ys.append(st.mean(o for _, o in samp))
        res.append(fit(xs, ys)[1])
    res.sort(); return res[int(.025 * B)], res[int(.975 * B)]

def collect(rows, alg):
    by = {}
    for d in rows:
        if d['alg'] == alg: by.setdefault(d['bits'], []).append((d['r'], d['ops']))
    return by

# raw rows: SMALL/RHO from raw_*.jsonl files; LOG* from evidence
rows = []
for f in glob.glob(os.path.join(here, 'raw_*.jsonl')):
    rows += [json.loads(l) for l in open(f)]
rows += lines(lambda a: len(a) > 3 and a[2] in ('LOGMITM',)) + lines(lambda a: len(a) > 3 and a[2] in ('LOGEXH',))
# the earlier non-truncated SMALL 12 18 run
rows += lines(lambda a: len(a) > 3 and a[2] == 'SMALL' and a[4] == '18')
rep = {}
for alg in ('RHO', 'EXH', 'MITM'):
    by = collect(rows, alg)
    keys = sorted(by)
    xs = [st.mean(r for r, _ in by[k]) for k in keys]; ys = [st.mean(o for _, o in by[k]) for k in keys]
    ysm = [st.median(o for _, o in by[k]) for k in keys]
    free = fit(xs, ys); sq = fit_sqrt(xs, ys); lin = fit(xs, ys, betas=[1.0])
    lo, hi = boot(by)
    rep[alg] = dict(bits=keys, n=[len(by[k]) for k in keys], mean_r=[round(x) for x in xs], mean_ops=[round(y, 1) for y in ys],
                    mean_ops_over_sqrt_r=[round(y / x ** .5, 2) for x, y in zip(xs, ys)], mean_ops_over_r=[round(y / x, 3) for x, y in zip(xs, ys)],
                    free_fit=dict(beta=free[1], alpha=round(free[2], 3), gamma=round(free[3], 1), rel_sse=round(free[0], 4)), beta_ci95=[lo, hi],
                    sqrt_fit=dict(alpha=round(sq[2], 3), gamma=round(sq[3], 1), rel_sse=round(sq[0], 4)),
                    lin_fit=dict(alpha=round(lin[2], 3), gamma=round(lin[3], 1), rel_sse=round(lin[0], 4)))
print(json.dumps(rep, indent=1))
json.dump(rep, open(os.path.join(here, 'analysis_e3.json'), 'w'), indent=1)

# E2 per-pass success
e2 = lines(lambda a: len(a) > 3 and a[2].isdigit() and a[3].isdigit())
agg = {}
for d in e2:
    key = (d['n_prime'])
    agg.setdefault(key, []).append(d)
print('E2 per-pass Algorithm-2 success P2, normalised c = P2 * r / l^2  (paper claims P2 ~ 0.6 l^2/r with l~log p)')
cs = []
for d in sorted(e2, key=lambda d: d['r']):
    P = d['alg2_hit_passes'] / d['passes']; Pu = d['alg2_useful'] / d['passes']
    # for r<C the exhaustive-pass saturates; report anyway
    se = (P * (1 - P) / d['passes']) ** .5
    print(d['n_prime'], d['q'], d['r'], 'C', d['C'], 'P2=%.5f' % P, 'useful=%.5f' % Pu, 'c=P*r/l^2=%.2f' % (P * d['r'] / d['l'] ** 2), 'cands/pass=%.1f' % d['candidates_per_pass'], 'se_c=%.2f' % (se * d['r'] / d['l'] ** 2))
