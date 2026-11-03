import json, glob, math, collections, sys
import numpy as np
def ols(xs, ys):
    xs, ys = np.array(xs, float), np.array(ys, float); n = len(xs)
    if n < 3: return None
    b = ((xs - xs.mean()) * (ys - ys.mean())).sum() / ((xs - xs.mean()) ** 2).sum(); a = ys.mean() - b * xs.mean()
    res = ys - a - b * xs; se = math.sqrt((res ** 2).sum() / (n - 2) / ((xs - xs.mean()) ** 2).sum())
    tq = {2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447}.get(n - 2, 2.0)
    return b, b - tq * se, b + tq * se
def load(pat):
    out = []
    for f in sorted(glob.glob(pat)):
        for l in open(f):
            l = l.strip()
            if l.startswith('{'): out.append(json.loads(l))
    return out
print("== E1 main: pooled ratio observed/pred per family and size (tri | quad/ctrl | cov/cov_rand)")
R = load('out_e1_main_*.jsonl'); fams = []
for r in R:
    if r['fam'] not in fams: fams.append(r['fam'])
bits = sorted({r['bits'] for r in R})
agg = collections.defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0, 0])
for r in R:
    a = agg[(r['fam'], r['bits'])]; a[0] += r['tri']; a[1] += r['tri_pred']; a[2] += r['quad']; a[3] += r['quad_pred']; a[4] += r['cov']; a[5] += r['cov_pred']; a[6] += 1; a[7] += r['s']
print('%-9s' % 'family' + ''.join('%22d' % b for b in bits) + '   slope(log2 tri/bit) [95%CI]  slope(quad)')
for f in fams:
    row = '%-9s' % f; ys = []; yq = []; xs = []
    for b in bits:
        a = agg.get((f, b));
        if not a: row += ' ' * 22; continue
        c = agg[('rand', b)]; tri = a[0] / a[1]; q = (a[2] / a[3]) / (c[2] / c[3]); cv = (a[4] / a[6]) / (a[5] / a[6])
        row += '%7.3f/%5.3f/%5.3f   ' % (tri, q, cv); ys.append(math.log2(tri)); yq.append(math.log2(q)); xs.append(b)
    o = ols(xs, ys); oq = ols(xs, yq)
    row += '  %+.3f [%+.3f,%+.3f]  %+.3f [%+.3f,%+.3f]' % (o + oq) if o else ''
    print(row)
print("counts: expected tri per rep at bits", {b: round(agg[('rand', b)][1] / agg[('rand', b)][6], 1) for b in bits})
print("\n== E1 best-of-many: max and mean ratio over reps (REPS=40) per family")
R = load('out_e1_many_*.jsonl')
for b in sorted({r['bits'] for r in R}):
    for f in fams:
        v = [r['tri'] / r['tri_pred'] for r in R if r['bits'] == b and r['fam'] == f]
        q = [r['quad'] / r['quad_pred'] for r in R if r['bits'] == b and r['fam'] == f]
        if v: print('bits %d %-9s n=%3d tri mean %.3f max %.3f | quad mean %.3f max %.3f | exp tri/rep %.0f' % (b, f, len(v), np.mean(v), max(v), np.mean(q), max(q), np.mean([r['tri_pred'] for r in R if r['bits'] == b and r['fam'] == f])))
print("\n== E2 lattice images")
R = load('out_e2_*.jsonl'); g = collections.defaultdict(list)
for r in R: g[(r['d'], r['bits'], r['B'])].append(r)
for k in sorted(g):
    v = g[k]; s = v[0]['s']; N = v[0]['N']
    tri = np.mean([r['tri'] for r in v]); nt = np.array([r['nontrivial'] for r in v]); pred = np.mean([r['rand_pred'] for r in v])
    print('d=%d bits=%d B=%d s=%d n=%d | tri/pred %.1f (trivial frac %.4f) | nontrivial: mean/pred %.2f, frac(k with >0) %.3f, max/pred %.1f | cov %.4f vs rand %.4f, ratio %.4f | N/s=%.0f' % (
        k[0], k[1], k[2], s, len(v), tri / pred, 1 - nt.mean() / tri, nt.mean() / pred, (nt > 0).mean(), nt.max() / pred, np.mean([r['cov'] for r in v]), np.mean([r['cov_rand'] for r in v]), np.mean([r['cov'] / r['cov_rand'] for r in v]), N / s))
print("\n== E3 local search")
R = load('out_e3_*.jsonl'); bb = sorted({r['bits'] for r in R}); xs = []; ys = []; ya = []
for b in bb:
    v = [r for r in R if r['bits'] == b]
    print('bits %d N~%d s=%d n=%d | ratio_final %.1f  ratio_AP %.1f  ratio_init %.2f | arc90/s found %.2f random %.1f | KS x %.3f ybar %.3f exp %.3f' % (b, v[0]['N'], v[0]['s'], len(v), np.mean([r['ratio_final'] for r in v]), np.mean([r['ratio_AP'] for r in v]), np.mean([r['ratio_init'] for r in v]), np.mean([r['best_arc90_over_s'] for r in v]), np.mean([r['random_arc90_over_s'] for r in v]), np.mean([r['ks_x'] for r in v]), np.mean([r['ks_ybar'] for r in v]), v[0]['ks_expected']))
    xs.append(b); ys.append(math.log2(np.mean([r['ratio_final'] for r in v])))
print('slope log2 ratio_final per bit', ols(xs, ys))

print("\n== E2 pooled nontrivial closure over all configs: sum(nontrivial)/sum(rand_pred)")
R = load('out_e2_*.jsonl'); print('n=%d  sum nontrivial %d  sum pred %.0f  ratio %.3f ; frac k with >0: %.3f' % (len(R), sum(r['nontrivial'] for r in R), sum(r['rand_pred'] for r in R), sum(r['nontrivial'] for r in R) / sum(r['rand_pred'] for r in R), np.mean([r['nontrivial'] > 0 for r in R])))
print("\n== E4 (post-hoc) fibre closure: means over reps/seeds per (family, sizing, bits)")
R = load('out_e4_*.jsonl'); g = collections.defaultdict(list)
for r in R: g[(r['sizing'], r['fam'], r['bits'])].append(r)
for sz in ('sqrt', 'cbrt'):
    for fam in ('rand', 'ywin', 'lin'):
        xs = []; ys = []
        for b in sorted({k[2] for k in g}):
            v = g.get((sz, fam, b))
            if not v: continue
            rt = np.mean([r['ratio'] for r in v]); rr = np.mean([r['resid_ratio'] for r in v])
            print('%-5s %-5s bits %2d s=%5d n=%2d | ratio %.2f resid %.2f | nrel %.0f nunk %.0f comps %.0f rank %s | pred/rep %.1f' % (sz, fam, b, v[0]['s'], len(v), rt, rr, np.mean([r['nrel'] for r in v]), np.mean([r['nunk'] for r in v]), np.mean([r['comps'] for r in v]), np.mean([r['rank'] for r in v if r['rank'] is not None]) if any(r['rank'] is not None for r in v) else None, np.mean([r['pred'] for r in v])))
            xs.append(b); ys.append(math.log2(max(rt, 1e-9)))
        print('   slope log2 ratio per bit', ols(xs, ys))
