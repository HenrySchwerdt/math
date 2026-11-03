import json, glob, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'round12-inventor-a'))
from common import fit
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
def L(pat):
    out = []
    for f in sorted(glob.glob(os.path.join(H, pat))):
        out += [json.loads(l) for l in open(f)]
    return out
gm = lambda v: math.exp(sum(math.log(x) for x in v)/len(v))
def tot(d, w=10): return d['adds_finder'] + d['adds_target'] + (d['fb_mults'] + d['la_mults'])/w
lines = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); lines.append(s)
for g, name in [(0, 'D2a (d~sqrt p)'), (1, 'D2b (d~p^1/3)')]:
    rho = [d for d in L(f'out_rho_{g}_*.jsonl')]
    full = [d for d in L(f'out_full_{g}_*.jsonl')]
    P(f'## {name}')
    P('kind | bits | n | success | s(|V|) | pi_hat | targets | relations | finder adds | LA mults | total(w=10) | rho U1 | ratio | total/p | rho walk model')
    for kind in ('coset', 'smallx'):
        for b in sorted({d['bits'] for d in full}):
            F = [d for d in full if d['bits'] == b and d['kind'] == kind]
            if not F: continue
            R = [d for d in rho if d['bits'] == b]
            same = [d for d in R]
            P(kind, b, len(F), f"{sum(d['ok'] for d in F)}/{len(F)}", f"{gm([d['s'] for d in F]):.0f}",
              f"{sum(d['hit_targets'] for d in F)/sum(d['targets'] for d in F):.3f}", f"{gm([d['targets'] for d in F]):.0f}",
              f"{gm([d['relations'] for d in F]):.0f}", f"{gm([d['adds_finder'] for d in F]):.3g}", f"{gm([d['la_mults'] for d in F]):.3g}",
              f"{gm([tot(d) for d in F]):.3g}", f"{gm([d['U1'] for d in R]):.0f}" if R else '-',
              f"{gm([tot(d) for d in F])/gm([d['U1'] for d in R]):.0f}" if R else '-',
              f"{gm([tot(d)/d['p'] for d in F]):.2f}", f"{gm([d['rho_walk_model'] for d in R]):.0f}" if R else '-')
    for kind in ('coset', 'smallx'):
        for lo, hi, tag in [(16, 24, 'pre-registered 16-24'), (16, 28, 'incl. post-hoc 26/28 full')]:
            F = [d for d in full if d['kind'] == kind and lo <= d['bits'] <= hi]
            if len(F) < 4: continue
            f = fit([math.log2(d['r']) for d in F], [math.log2(tot(d)) for d in F]); fs = fit([math.log2(d['r']) for d in F], [math.log2(d['adds_finder']) for d in F])
            P(f'FIT {name} {kind} {tag}: alpha_total={f["alpha"]:.3f} se {f["se"]:.3f} CI[{f["lo"]:.3f},{f["hi"]:.3f}] n={f["n"]}; alpha_finder_adds={fs["alpha"]:.3f} CI[{fs["lo"]:.3f},{fs["hi"]:.3f}]')
    R = [d for d in rho if d['bits'] <= 24]
    if R:
        f = fit([math.log2(d['r']) for d in R], [math.log2(d['U1']) for d in R]); P(f'FIT rho (same bits<=24, U1 incl. setup): alpha={f["alpha"]:.3f} CI[{f["lo"]:.3f},{f["hi"]:.3f}]')
        R = [d for d in rho if d['bits'] >= 16]
        f = fit([math.log2(d['r']) for d in R], [math.log2(d['rho_walk_model']) for d in R]); P(f'rho analytic walk model sqrt(pi r/2) exponent {f["alpha"]:.3f} (by construction 0.5)')
        R = [d for d in rho if d['bits'] >= 22]
        f = fit([math.log2(d['r']) for d in R], [math.log2(d['U1']) for d in R]); P(f'POST-HOC rho U1 sizes>=22: alpha={f["alpha"]:.3f} CI[{f["lo"]:.3f},{f["hi"]:.3f}]')
P('## per-relation only (protocol: 26, 28 bits; 40 targets x 3 seeds)')
pr = L('out_perrel_0_*.jsonl')
for kind in ('coset', 'smallx'):
    for b in (26, 28):
        F = [d for d in pr if d['bits'] == b and d['kind'] == kind]
        if not F: continue
        hit = sum(d['hit_targets'] for d in F); T = sum(d['targets'] for d in F); rel = sum(d['relations'] for d in F)
        s = gm([d['s'] for d in F]); r = gm([d['r'] for d in F]); add = sum(d['adds_finder'] for d in F)
        cpr = add/rel
        P(f'{kind} {b}: s={s:.0f} pi_hat={hit/T:.3f} rel/target={rel/T:.2f} adds/relation={cpr:.3g} = {cpr/math.sqrt(r):.1f} sqrt(r); model total ~ s*adds/rel={s*cpr:.3g} = {s*cpr/math.sqrt(r):.0f} sqrt(r) (extrapolation)')
open(os.path.join(H, 'analysis.txt'), 'w').write('\n'.join(lines) + '\n')
