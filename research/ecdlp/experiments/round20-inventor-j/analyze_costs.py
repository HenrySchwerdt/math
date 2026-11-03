"""Fits (alpha sqrt(x)+gamma, no log-log) and advantage bars. Reads out/*.json. Writes results_costs.md"""
import json, math, random, numpy as np, os
O = 'out/'
def fit(xs, ys, B=2000, seed=1):
    xs, ys = np.array(xs, float), np.array(ys, float)
    def ols(a, b):
        A = np.stack([np.sqrt(a), np.ones_like(a)], 1); return np.linalg.lstsq(A, b, rcond=None)[0]
    co = ols(xs, ys); rg = np.random.default_rng(seed); bs = []
    for _ in range(B):
        i = rg.integers(0, len(xs), len(xs)); bs.append(ols(xs[i], ys[i]))
    bs = np.array(bs); return co, np.percentile(bs, [2.5, 97.5], axis=0)
L = []
rho = json.load(open(O + 'rho.json')); kg = json.load(open(O + 'kang.json'))
(ar, gr), ci_r = fit([x['r'] for x in rho], [x['ops'] for x in rho])
(ak, gk), ci_k = fit([x['w'] for x in kg], [x['ops'] for x in kg])
L.append(f"rho control (same Ops, {len(rho)} instances, r 2^12..2^27.3): ops = {ar:.3f} sqrt(r) + {gr:.1f}; alpha 95% CI [{ci_r[0][0]:.3f},{ci_r[1][0]:.3f}], gamma CI [{ci_r[0][1]:.0f},{ci_r[1][1]:.0f}]")
L.append(f"kangaroo control ({len(kg)} instances, w 2^8..2^24, success {np.mean([x['ok'] for x in kg]):.3f}): ops = {ak:.3f} sqrt(w) + {gk:.1f}; alpha CI [{ci_k[0][0]:.3f},{ci_k[1][0]:.3f}], gamma CI [{ci_k[0][1]:.0f},{ci_k[1][1]:.0f}]")
rhof = lambda r: ar * math.sqrt(r) + gr
kf = lambda w: ak * math.sqrt(w) + gk
# interval bar: width w*(r) with kangaroo cost = rho cost
L.append("interval bar: max w/r for kangaroo(w) < rho(r):")
for b in (12, 16, 20, 24, 28, 32, 40, 64, 128):
    r = 2.0 ** b; lo, hi = 1.0, r
    for _ in range(80):
        mid = math.sqrt(lo * hi)
        if kf(mid) < rhof(r): lo = mid
        else: hi = mid
    L.append(f"  r=2^{b}: w*/r = {lo / r:.3g} (rho {rhof(r):.3g} ops)")
# P1 model: rounds * (N(1+mq)+c_round)
calib = dict(nu=2.0, kappa=2.0)
def N_of(eps, nu=2.0):
    N = 200
    for _ in range(30): N = nu * math.log(4 * N) / eps ** 2
    return N
def p1_model(r, eps, mq=7, nu=2.0, kappa=2.0):
    N = N_of(eps, nu); W = r / 2; R = 0; cost = 0
    if N / (2 * kappa) <= 1.05: return float('inf')
    while W > 3:
        cost += N * (1 + mq) + 3 * 1.5 * math.log2(r) + 1.5 * math.log2(max(2, r / (2 * W))) ; W = kappa * 2 * W / N; R += 1
        if R > 200: return float('inf')
    return cost + 8 * 3
rows = []
for eps in (0.2, 0.1, 0.05):
    d = []
    for fn in (f'p1_main_{eps}.json',) + tuple(f'p1_main_{eps}_b{b}.json' for b in (12, 16, 20, 24, 28)):
        if os.path.exists(O + fn): d += json.load(open(O + fn))
    if d:
        for b in sorted(set(x['bits'] for x in d)):
            xs = [x for x in d if x['bits'] == b]; r = xs[0]['r']
            rows.append((eps, b, r, sum(x['ok'] for x in xs), len(xs), np.mean([x['ops'] for x in xs]), np.mean([x['ops_feat'] if 'ops_feat' in x else x['ops'] for x in xs]), np.mean([x['q'] for x in xs]), p1_model(r, eps), rhof(r)))
L.append("P1 stride-ML (planted MSB oracle, nu=2, kappa=2): eps | bits | r | ok/n | core ops | ops+7/query features | queries | model ops(+feat) | rho fit")
for x in rows: L.append("  %.2f | %d | %d | %d/%d | %.0f | %.0f | %.0f | %.0f | %.0f" % x)
L.append("epsilon bar: smallest eps with modelled P1 cost (m_q=7 feature ops/query) < rho fit (and with m_q=0, m_q=50):")
for mq in (0, 7, 50):
    for b in (12, 16, 20, 24, 28, 32, 40, 64, 128):
        r = 2.0 ** b; lo, hi = 1e-6, 0.5
        if p1_model(r, 0.5, mq) >= rhof(r): L.append(f"  mq={mq} r=2^{b}: no eps<=0.5 beats rho"); continue
        for _ in range(60):
            mid = math.sqrt(lo * hi)
            if p1_model(r, mid, mq) < rhof(r): hi = mid
            else: lo = mid
        L.append(f"  mq={mq} r=2^{b}: eps_bar = {hi:.4g}   (eps_bar*r^(1/4) = {hi * r ** .25:.3g})")
open('results_costs.md', 'w').write('\n'.join(L)); print('\n'.join(L))

# ---- closeness-detector cost model (P4 scan, nc=32, shrink nc/2 per round, finish enumeration of 2*300 ops) ----
def close_rounds_cost(r, delta, mq=7, nu=1.0, nc=32):
    T = max(1, math.ceil(nu * math.log(8 * nc) / delta ** 2 / 4)); W = r / 2; cost = 0
    while W > 300:
        cost += nc * T * (1 + mq) + 3 * 1.5 * math.log2(r) + T * 1.5 * math.log2(r) ; W = 2 * W / nc * 1.0
    return cost + 600
L2 = ["", "closeness P4 measured (planted detector, nu_d=1,2,4; 12 inst/cell; ok = verified k):"]
for fn in ('p4c.json',):
    for x in json.load(open(O + fn)):
        if x['nu'] == 1.0 or x['nu'] == 4.0:
            L2.append(f"  delta={x['delta']} nu={x['nu']} bits={x['bits']}: ok {x['ok']}/{x['n']} core ops {x['mean_ops']:.0f}, +7/query feats {x['mean_ops_feat']:.0f}, widths {x['widths']}, rho fit {rhof(2**x['bits'] * 0.6):.0f}")
L2.append("detector bar: smallest delta such that multi-level scan (nu_d=1, m_q=7 or 0 test ops) < rho fit(r) and < kangaroo(W=r) fit:")
for mq in (0, 7):
    for b in (20, 28, 40, 64, 128):
        r = 2.0 ** b; tgt = min(rhof(r), kf(r))
        if close_rounds_cost(r, 0.5, mq) >= tgt: L2.append(f"  mq={mq} r=2^{b}: no delta<=0.5 beats min(rho,kang)"); continue
        lo, hi = 1e-6, 0.5
        for _ in range(60):
            mid = math.sqrt(lo * hi)
            if close_rounds_cost(r, mid, mq) < tgt: hi = mid
            else: lo = mid
        L2.append(f"  mq={mq} r=2^{b}: delta_bar = {hi:.4g}  (delta_bar*r^(1/4) = {hi * r ** .25:.3g})")
# single-level scan then kangaroo on width 2w : delta needed vs w (W = r)
L2.append("single-level scan over W=r, test window w, then kangaroo(2w): delta needed to beat rho fit (kangaroo on full W costs 2.7x rho, so rho is the relevant bar); nu_d=1, m_q=7")
for b in (24, 28, 40, 64):
    r = 2.0 ** b; best = None
    for lw in range(4, b):
        w = 2.0 ** lw; nc = r / w
        for dl in np.logspace(-4, math.log10(0.5), 400):
            T = max(1, math.ceil(math.log(8 * nc) / dl ** 2 / 4)); c = nc * T * 8 + kf(2 * w)
            if c < rhof(r):
                if best is None or dl < best[0]: best = (dl, lw)
                break
    L2.append(f"  r=2^{b}: delta_min={best[0] if best else None} at w=2^{best[1] if best else None}" )
open('results_costs.md', 'a').write('\n'.join(L2)); print('\n'.join(L2))

L3 = ["", "P1 fitted cost vs r on the planted control: ops = alpha sqrt(r) + gamma (per-instance data, bootstrap 95%), compare alpha_rho:"]
for eps in (0.2, 0.1, 0.05):
    d = []
    for fn in (f'p1_main_{eps}.json',) + tuple(f'p1_main_{eps}_b{b}.json' for b in (12, 16, 20, 24, 28)):
        if os.path.exists(O + fn): d += json.load(open(O + fn))
    for key, nm in (('ops', 'core'), ('ops_feat', '+7/query')):
        xs = [x['r'] for x in d if x.get('ok')]; ys = [x[key] if key in x else x['ops'] for x in d if x.get('ok')]
        (a, g), ci = fit(xs, ys)
        L3.append(f"  eps={eps} {nm}: alpha={a:.4f} [{ci[0][0]:.4f},{ci[1][0]:.4f}] gamma={g:.0f} (n={len(xs)}, successes only); alpha_rho={ar:.3f}")
open('results_costs.md', 'a').write('\n'.join(L3)); print('\n'.join(L3))
