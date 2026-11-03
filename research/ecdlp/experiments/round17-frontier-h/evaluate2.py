"""Held-out evaluation per PROTOCOL.md. Usage: evaluate2.py TAG [TAG...]  | controls
FIT sizes 13-16 (seeds 600-602), HELD sizes 17-20 (seeds 700-702), 40 instances/curve, same instances for every program.
Writes out_eval_<TAG>.json."""
import sys, os, json, math, random, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsl2 import *
HERE = os.path.dirname(os.path.abspath(__file__))
FIT = [(tb, sd) for tb in (13, 14, 15, 16) for sd in (600, 601, 602)]
HELD = [(tb, sd) for tb in (17, 18, 19, 20) for sd in (700, 701, 702)]
NINST, B = 40, 2000
def measure(prog, spec):
    res = {}
    for tb, sd in spec:
        c = make_curve(tb, sd)
        for k, s in instances(c, NINST, 5):
            out, cost, _ = run(prog, c, k, s); res.setdefault(tb, []).append((cost, out == k, c['r']))
    return res
def fit_ab(rs, cs):
    """OLS cost = alpha*sqrt(r) + gamma"""
    xs = [math.sqrt(r) for r in rs]; mx, my = sum(xs) / len(xs), sum(cs) / len(cs)
    a = sum((x - mx) * (y - my) for x, y in zip(xs, cs)) / sum((x - mx) ** 2 for x in xs); return a, my - a * mx
def means(res, idx=None):
    sz = sorted(res)
    return ([sum(t[2] for t in res[s]) / len(res[s]) for s in sz],
            [sum((res[s][i] if idx is None else res[s][idx[s][j]])[0] for j, i in enumerate(range(len(res[s])))) / len(res[s]) for s in sz])
def analyse(cand, ctrl, tag_c):
    """cand/ctrl = dict(fit=res, held=res). Joint bootstrap over instance indices (same instances for both programs)."""
    rng = random.Random(12345)
    sf, sh = sorted(cand['fit']), sorted(cand['held'])
    rf = [sum(t[2] for t in cand['fit'][s]) / len(cand['fit'][s]) for s in sf]
    rh = [sum(t[2] for t in cand['held'][s]) / len(cand['held'][s]) for s in sh]
    def mc(d, s, idx): return sum(d[s][i][0] for i in idx) / len(idx)
    def stats(idx_f, idx_h):
        out = {}
        for nm, P in (('cand', cand), ('ctrl', ctrl)):
            a, g = fit_ab(rf, [mc(P['fit'], s, idx_f[s]) for s in sf])
            obs = [mc(P['held'], s, idx_h[s]) for s in sh]
            pred = [a * math.sqrt(r) + g for r in rh]
            out[nm] = dict(alpha=a, gamma=g, obs=obs, ratio=[o / q for o, q in zip(obs, pred)])
        rr = [out['cand']['obs'][i] / out['ctrl']['obs'][i] for i in range(4)]
        xs = [math.log2(r) for r in rh]; ys = [math.log(v) for v in rr]; mx, my = sum(xs) / 4, sum(ys) / 4
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        Q = [out['cand']['ratio'][i] / out['ctrl']['ratio'][i] for i in range(4)]
        return out, rr, slope, Q
    full = {s: list(range(len(cand['fit'][s]))) for s in sf}; fullh = {s: list(range(len(cand['held'][s]))) for s in sh}
    o, rr, slope, Q = stats(full, fullh)
    bs, bQ, bR, bA = [], [[] for _ in range(4)], [[] for _ in range(4)], []
    for _ in range(B):
        idf = {s: [rng.randrange(len(cand['fit'][s])) for _ in cand['fit'][s]] for s in sf}
        idh = {s: [rng.randrange(len(cand['held'][s])) for _ in cand['held'][s]] for s in sh}
        try: _, rb, sb, Qb = stats(idf, idh)
        except ZeroDivisionError: continue
        bs.append(sb); bA.append(0)
        for i in range(4): bQ[i].append(Qb[i]); bR[i].append(rb[i])
    q = lambda v, f: sorted(v)[min(len(v) - 1, max(0, int(f * len(v))))]
    succ = {s: sum(t[1] for t in cand['fit'][s]) / len(cand['fit'][s]) for s in sf}
    succ.update({s: sum(t[1] for t in cand['held'][s]) / len(cand['held'][s]) for s in sh})
    T1 = all(v >= 0.9 for v in succ.values())
    T2 = q(bs, .995) < 0
    T3 = q(bQ[3], .995) < 1
    T4 = rr[3] < 1
    return dict(tag=tag_c, success=succ, alpha_gamma_cand=[o['cand']['alpha'], o['cand']['gamma']], alpha_gamma_ctrl=[o['ctrl']['alpha'], o['ctrl']['gamma']],
                obs_ratio_pred_cand=o['cand']['ratio'], obs_ratio_pred_ctrl=o['ctrl']['ratio'],
                cost_ratio_to_rho_held=rr, cost_ratio_ci99=[[q(bR[i], .005), q(bR[i], .995)] for i in range(4)],
                logratio_slope_per_log2r=slope, slope_ci99=[q(bs, .005), q(bs, .995)],
                Q_double_ratio=Q, Q_ci99=[[q(bQ[i], .005), q(bQ[i], .995)] for i in range(4)],
                T1_success=T1, T2_slope_upper99_lt0=T2, T3_Q2^20_upper99_lt1=T3 if False else None, T3=T3, T4_ratio_lt1=T4, counts=T1 and T2 and T3 and T4)
def main():
    h = hashlib.sha256(open(os.path.join(HERE, 'PROTOCOL.md'), 'rb').read()).hexdigest()
    assert h == open(os.path.join(HERE, 'PROTOCOL.sha256')).read().split()[0]
    ctrl_f = os.path.join(HERE, 'out_measure_rho_dp.json')
    def get(name, prog):
        f = os.path.join(HERE, f'out_measure_{name}.json')
        if os.path.exists(f): d = json.load(open(f)); return {k: {int(s): [tuple(t) for t in v] for s, v in dd.items()} for k, dd in d.items()}
        d = dict(fit=measure(prog, FIT), held=measure(prog, HELD)); json.dump(d, open(f, 'w')); return d
    ctrl = get('rho_dp', prog_rho_dp())
    for tag in sys.argv[1:]:
        if tag == 'controls':
            progs = {'bsgs': prog_bsgs(), 'rho_floyd': prog_rho_floyd_restart(), 'rho_dp_nb3': prog_rho_dp(3, 2), 'rho_dp_nb5': prog_rho_dp(4, 3), 'ic_ms_cap12': prog_ic_ms()}
        else:
            ch = json.load(open(os.path.join(HERE, f'out_evolve_{tag}.json')))['champions'][0]['prog']
            progs = {tag: ([tuple(x) for x in ch[0]], [tuple(x) for x in ch[1]])}
        out = {}
        for n, pr in progs.items():
            d = get(n, pr); a = analyse(d, ctrl, n); a['prog'] = pr; out[n] = a
            print(n, 'succ', {k: round(v, 2) for k, v in a['success'].items()}, 'a,g cand %.2f %.0f ctrl %.2f %.0f' % (*a['alpha_gamma_cand'], *a['alpha_gamma_ctrl']),
                  '\n   cost/rho', [round(x, 3) for x in a['cost_ratio_to_rho_held']], 'slope %.3f ci99 [%.3f,%.3f]' % (a['logratio_slope_per_log2r'], *a['slope_ci99']),
                  'Q', [round(x, 3) for x in a['Q_double_ratio']], 'Q20 ci99', [round(x, 3) for x in a['Q_ci99'][3]],
                  'T1-4', a['T1_success'], a['T2_slope_upper99_lt0'], a['T3'], a['T4_ratio_lt1'], 'COUNTS', a['counts'], flush=True)
        json.dump(dict(protocol_sha256=h, results=out), open(os.path.join(HERE, f'out_eval_{tag}.json'), 'w'))
main()
