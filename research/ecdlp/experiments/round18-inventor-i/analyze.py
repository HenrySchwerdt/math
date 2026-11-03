"""Fit T = alpha p^beta + gamma (beta scan, relative-error LS), bootstrap CI over curves. Per PROTOCOL.md."""
import json, glob, math, random, sys
import numpy as np
rows = {}
for f in sorted(glob.glob('out_ttest_*_*.jsonl')):
    o = json.loads(open(f).read())
    rows.setdefault(o['bits'], []).append(o)
bits = sorted(rows)
def curvemeans(key, per):
    """per-curve means of key over random targets"""
    return {b: [np.mean([r[key] for r in o['rand']]) for o in rows[b]] for b in bits}
ps = {b: np.mean([o['p'] for o in rows[b]]) for b in bits}
def fit(p, T, betas=np.arange(0.0, 1.5001, 0.005)):
    best = None
    for be in betas:
        x = p ** be; A = np.vstack([x / T, 1.0 / T]).T; y = np.ones(len(T))   # relative error: (alpha x + gamma)/T = 1
        sol, *_ = np.linalg.lstsq(A, y, rcond=None); res = np.sum((A @ sol - y) ** 2)
        if best is None or res < best[0]: best = (res, be, sol[0], sol[1])
    return best
def boot(key, name):
    cm = curvemeans(key, None)
    P = np.array([ps[b] for b in bits]); T = np.array([np.mean(cm[b]) for b in bits])
    r, be, al, ga = fit(P, T)
    rng = random.Random(5); bs = []
    for _ in range(2000):
        Tb = np.array([np.mean([rng.choice(cm[b]) for _ in cm[b]]) for b in bits])
        bs.append(fit(P, Tb, np.arange(0.0, 1.5001, 0.01))[1])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    sl = np.polyfit(np.log(P), np.log(T), 1)[0]
    print(f'{name}: beta={be:.3f} CI95 [{lo:.2f},{hi:.2f}] alpha={al:.3g} gamma={ga:.3g} relres={math.sqrt(r/len(T)):.3f} (naive loglog slope {sl:.3f}, warning only)')
    # also fit against s^2 (s = |B|): exponent in p implied by T ~ s^e
    S = np.array([np.mean([o['s'] for o in rows[b]]) for b in bits]); e = np.polyfit(np.log(S), np.log(T), 1)[0]
    print(f'   T vs s: naive slope {e:.3f} => in p: {e/5:.3f} (s = p^(1/5))')
    return T
print('bits  p  s  npairsums  | per-target means')
print('bits', bits)
Tm = boot('adds_mitm', 'MITM counted EC adds (deterministic ~ 2*#pairsums)')
Tw = boot('t_mitm', 'MITM wall seconds (pure Python)')
Tt = boot('t_tower', 'TOWER wall seconds (flint poly product tree + gcd)')
for i, b in enumerate(bits):
    o = rows[b]
    pre_t = np.mean([x['t_pre_tower'] for x in o]); pre_m = np.mean([x['t_pre_mitm'] for x in o])
    sf = np.mean([sum(r['found_mitm'] for r in x['rand']) / len(x['rand']) for x in o])
    ok = all(r.get('ok_mitm', True) and r.get('ok_tower', True) for x in o for k in ('rand', 'planted') for r in x[k])
    pl = all(r['found_mitm'] and r['found_tower'] for x in o for r in x['planted'])
    print(f"{b} p={ps[b]:.3g} s={np.mean([x['s'] for x in o]):.0f} M={np.mean([x['npairsums'] for x in o]):.0f} adds={Tm[i]:.0f} mitm_s={Tw[i]:.4f} tower_s={Tt[i]:.4f} tower/mitm={Tt[i]/Tw[i]:.2f} pre_mitm={pre_m:.3f} pre_tower={pre_t:.3f} succ_rand={sf:.3f} planted_all_found={pl} all_verified={ok}")
