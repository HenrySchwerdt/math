import json, glob, random
import numpy as np
from math import log2
rng = np.random.default_rng(7)
def fit(xs, ys):
    A = np.vstack([xs, np.ones(len(xs))]).T
    return np.linalg.lstsq(A, ys, rcond=None)[0]
def boot_slope(xs, samples, B=2000):
    """samples: list per size of arrays of ops; returns slope, CI"""
    ys = [log2(np.mean(s)) for s in samples]; sl = fit(xs, ys)[0]
    bs = []
    for _ in range(B):
        yb = [log2(np.mean(rng.choice(s, len(s)))) for s in samples]; bs.append(fit(xs, yb)[0])
    return sl, np.percentile(bs, [2.5, 97.5])
def boot_diff(xs, sa, sb, B=2000):
    """slope(a)-slope(b) with paired resampling (same instance indices), and pooled geometric ratio b/a"""
    ya = [log2(np.mean(s)) for s in sa]; yb = [log2(np.mean(s)) for s in sb]
    d0 = fit(xs, ya)[0] - fit(xs, yb)[0]
    ratio0 = np.exp(np.mean([log2(np.mean(b)/np.mean(a)) * np.log(2) for a, b in zip(sa, sb)]))
    ds, rs = [], []
    for _ in range(B):
        ia = [rng.integers(0, len(s), len(s)) for s in sa]
        ya_ = [log2(np.mean(s[i])) for s, i in zip(sa, ia)]; yb_ = [log2(np.mean(s[i])) for s, i in zip(sb, ia)]
        ds.append(fit(xs, ya_)[0] - fit(xs, yb_)[0])
        rs.append(np.exp(np.mean([(y2 - y1) * np.log(2) for y1, y2 in zip(ya_, yb_)])))
    return d0, np.percentile(ds, [2.5, 97.5]), ratio0, np.percentile(rs, [2.5, 97.5])
def verdict(d_ci_hi, ratio_ci, cens):
    if d_ci_hi < -0.03 and cens <= 0.10: return 'ASYMPTOTIC-IMPROVEMENT evidence'
    if ratio_ci[0] > 1.15: return 'CONSTANT-FACTOR ADVANTAGE'
    if ratio_ci[1] < 0.87: return 'WORSE'
    return 'NO ADVANTAGE'
def load(pat):
    rows = []
    for f in sorted(glob.glob(pat)): rows += [json.loads(l) for l in open(f)]
    return rows
out = []
print('== T1')
for kind in ('j0', 'j1728'):
    rows = load(f'out_t1_{kind}_*.jsonl')
    bits = sorted({r['bits'] for r in rows})
    xs = [np.mean([r['rbits'] for r in rows if r['bits'] == b]) for b in bits]
    data = {m: [np.array([r['ops'] for r in sorted(rows, key=lambda r: r['seed']) if r['bits'] == b and r['method'] == m], float) for b in bits] for m in ('none', 'neg', 'aut')}
    fails = {m: sum(1 for r in rows if r['method'] == m and not r['ok']) for m in data}
    tot = len(rows)//3
    print(kind, 'rbits', xs, 'N/size', [len(s) for s in data['none']], 'fails', fails)
    print(' ratio r values', [r for r in sorted({r['r'] for r in rows})])
    for m in data:
        sl, ci = boot_slope(xs, data[m])
        print(f'  {m:5s} slope {sl:.3f} CI [{ci[0]:.3f},{ci[1]:.3f}]  mean ops/sqrt(r):', [round(np.mean(s)/2**(x/2), 2) for s, x in zip(data[m], xs)])
    for m in ('neg', 'aut'):
        d, dci, rt, rci = boot_diff(xs, data[m], data['none'])
        print(f'  {m} vs none: dslope {d:+.3f} CI [{dci[0]:+.3f},{dci[1]:+.3f}] pooled ratio none/{m} {rt:.2f} CI [{rci[0]:.2f},{rci[1]:.2f}] -> {verdict(dci[1], rci, fails[m]/tot/len(bits))}')
        print('   per-size ratio', [round(np.mean(a)/np.mean(b), 2) for a, b in zip(data['none'], data[m])])
print('== T2')
rows = load('out_t2_*.jsonl')
As = sorted({r['a'] for r in rows}); xs = [np.mean([r['rbits'] for r in rows if r['a'] == a]) for a in As]
def col(f): return [np.array([f(r) for r in sorted(rows, key=lambda r: r['seed']) if r['a'] == a], float) for a in As]
none = col(lambda r: r['none']['ops']); neg = col(lambda r: r['neg']['ops'])
iso = col(lambda r: r['b2']['iso']); stp = col(lambda r: r['b2']['steps']); rho_a = col(lambda r: r['b2']['rho_ops'])
for W in (0, 10):
    b2 = [ra + 2*s + W*i for ra, s, i in zip(rho_a, stp, iso)]
    d, dci, rt, rci = boot_diff(xs, b2, none)
    cens = sum(1 for r in rows if not r['b2']['ok'])/len(rows)
    sl, ci = boot_slope(xs, b2)
    print(f' B2 total W={W}: slope {sl:.3f} CI [{ci[0]:.3f},{ci[1]:.3f}] vs none dslope {d:+.3f} CI [{dci[0]:+.3f},{dci[1]:+.3f}] pooled ratio none/B2 {rt:.2f} CI [{rci[0]:.2f},{rci[1]:.2f}] -> {verdict(dci[1], rci, cens)}')
    print('   per-size none/B2', [round(np.mean(a)/np.mean(b), 2) for a, b in zip(none, b2)], 'mean B2', [round(np.mean(b)) for b in b2])
sl, ci = boot_slope(xs, none); print(' none slope', round(sl, 3), ci.round(3), 'mean', [round(np.mean(b)) for b in none])
sl, ci = boot_slope(xs, neg); print(' neg slope', round(sl, 3), ci.round(3))
sl, ci = boot_slope(xs, rho_a); print(' B2 orbit-rho-only slope', round(sl, 3), ci.round(3), 'ratio none/orbit', [round(np.mean(a)/np.mean(b), 2) for a, b in zip(none, rho_a)])
sl, ci = boot_slope(xs, iso); print(' iso evals vs r: slope', round(sl, 3), ci.round(3), 'mean iso', [round(np.mean(b), 1) for b in iso], 'steps', [round(np.mean(b), 1) for b in stp])
la = [log2(a) for a in As]; sl2 = fit(la, [log2(np.mean(b)) for b in iso])[0]
print(' iso evals vs a (=~log r/2): slope', round(sl2, 3))
print(' B2 fails', sum(1 for r in rows if not r['b2']['ok']), 'none fails', sum(1 for r in rows if not r['none']['ok']), 'N', len(rows))
print('== T3')
t3 = json.load(open('out_t3.json')); xs = [log2(r['p']) for r in t3]; ys = [log2(r['frac']) for r in t3]
sl = fit(xs, ys)[0]; bs = []
for _ in range(2000):
    yb = [log2(max(rng.binomial(r['tot'], r['frac']), 1)/r['tot']) for r in t3]; bs.append(fit(xs, yb)[0])
print(' fraction exponent', round(sl, 3), np.percentile(bs, [2.5, 97.5]).round(3), [(r['p'], r['frac']) for r in t3])
print('== POST-HOC (not pre-registered; diagnostics for the T2 W=10 verdict)')
rowsB = load('out_t2_*.jsonl'); xs = [np.mean([r['rbits'] for r in rowsB if r['a'] == a]) for a in As]
for W in (0, 10):
    b2 = [ra + 2*s + W*i for ra, s, i in zip(rho_a, stp, iso)]
    ov = [W*np.mean(i)/np.mean(b) for i, b in zip(iso, b2)]
    print(f' W={W}: mean ops/sqrt(r) B2', [round(np.mean(b)/2**(x/2), 2) for b, x in zip(b2, xs)], 'overhead share', [round(o, 2) for o in ov])
print(' none mean ops/sqrt(r)', [round(np.mean(b)/2**(x/2), 2) for b, x in zip(none, xs)])
print(' none median ops/sqrt(r)', [round(np.median(b)/2**(x/2), 2) for b, x in zip(none, xs)], 'orbit-only median', [round(np.median(b)/2**(x/2), 2) for b, x in zip(rho_a, xs)])
print(' none sd/mean', [round(np.std(b)/np.mean(b), 2) for b in none])
