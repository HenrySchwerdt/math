import json, glob, os
O = 'out/'; L = []
def load(b, t, c):
    f = f'{O}{b}_{t}_{c}.json'
    try: return json.load(open(f)) if os.path.getsize(f) else None
    except Exception: return None
def cell(v): return f"{v['adv']:+.4f} [{v['adv_lo']:+.4f},{v['adv_hi']:+.4f}] n={v['n']}"
L.append('## A. MSB classification: advantage acc-1/2 with Wilson 99% CI (TEST-A: train curves, held-out k; TEST-B: held-out curves)')
for ctl in (0, 1):
    L.append(f"\n### {'PLANTED-LEAK CONTROL (eps=0.05)' if ctl else 'REAL curves'}")
    L.append('| bits | model | TEST-A | TEST-B | flag A&B (lo>0) |'); L.append('|---|---|---|---|---|')
    for b in (12, 16, 20, 24, 28):
        d = load(b, 'msb', ctl)
        if not d: L.append(f'| {b} | (missing) | | | |'); continue
        for m in ('M1_hgb', 'M2_mlp', 'M3_logit', 'M4_single'):
            a, bb = d[f'{m}_A'], d[f'{m}_B']
            L.append(f"| {b} | {m} | {cell(a)} | {cell(bb)} | {'YES' if a['adv_lo'] > 0 and bb['adv_lo'] > 0 else 'no'} |")
L.append('\n## C. Closeness detector (|d|<=w vs d uniform); advantage on balanced test; beyond-table = class a restricted to |d|>16')
for ctl in (0, 1):
    L.append(f"\n### {'PLANTED CONTROL' if ctl else 'REAL'}")
    L.append('| bits | w | model | TEST-A | TEST-B | beyond-table B |'); L.append('|---|---|---|---|---|---|')
    for b in (12, 16, 20, 24, 28):
        for w in (16, 256, 4096):
            d = load(b, f'close{w}', ctl)
            if not d: L.append(f'| {b} | {w} | (missing) | | | |'); continue
            if 'skipped' in d: L.append(f'| {b} | {w} | skipped (w>r/16) | | | |'); continue
            for m in ('M1_hgb', 'M3_logit'):
                bt = d['beyond_table']; btc = cell(bt[f'{m}_B']) if isinstance(bt, dict) else bt
                L.append(f"| {b} | {w} | {m} | {cell(d[f'{m}_A'])} | {cell(d[f'{m}_B'])} | {btc} |")
L.append('\n## B. Regression of theta=k/r (circular error; random guess median 0.25, q90 0.45)')
L.append('| bits | which | split | R2 sin | R2 cos | median err [CI] | w50 | w90 | n |'); L.append('|---|---|---|---|---|---|---|---|---|')
for b in (12, 16, 20, 24, 28):
    for ctl, key in ((0, 'real_regress'), (1, 'control_regress')):
        d = load(b, 'regress', ctl)
        if not d or key not in d: L.append(f'| {b} | {key} | (missing) | | | | | | |'); continue
        for s, v in d[key].items():
            L.append(f"| {b} | {key} | {s} | {v['R2_sin']:.4f} | {v['R2_cos']:.4f} | {v['med_err']:.4f} [{v['med_ci'][0]:.4f},{v['med_ci'][1]:.4f}] | {v['w50']:.3f} | {v['w90']:.3f} | {v['n']} |")
L.append('\n## C2. Closeness at w = r/32 (post-hoc addendum 8): advantage with Wilson 99% CI')
L.append('| bits | w | control | M1 TEST-A | M1 TEST-B | M3 TEST-B | M1 beyond-table B |'); L.append('|---|---|---|---|---|---|---|')
for b, w in ((16, 2048), (20, 32768), (24, 524288), (28, 8388608)):
    for ctl in (0, 1):
        d = load(b, f'close{w}', ctl)
        if not d: L.append(f'| {b} | {w} | {ctl} | missing | | | |'); continue
        L.append(f"| {b} | {w} | {'planted' if ctl else 'real'} | {cell(d['M1_hgb_A'])} | {cell(d['M1_hgb_B'])} | {cell(d['M3_logit_B'])} | {cell(d['beyond_table']['M1_hgb_B'])} |")
open('results_learn.md', 'w').write('\n'.join(L)); print('\n'.join(L))
