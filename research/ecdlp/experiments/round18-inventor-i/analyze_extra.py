import json, glob, math, numpy as np
# Groebner summary (Singular)
print('Singular std, grevlex, S_3-tower system: m, d, p, time_ms, vdim')
G = {}
for f in sorted(glob.glob('out_gbs_*.jsonl')):
    o = json.loads(open(f).read() or '{}'); 
    if 'm' in o: G[(o['m'], o['d'])] = o
for m in (2, 3, 4):
    row = []
    for d in (4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40):
        o = G.get((m, d))
        row.append(f"d={d}:" + ('TO' if o is None or 'timeout_s' in o else f"{o['sing_ms']}ms/vdim{o['vdim']}"))
    print(' m=%d  ' % m + '  '.join(row))
# local growth exponents in d for completed points with >= 100 ms
for m in (3, 4):
    pts = [(d, G[(m, d)]['sing_ms']) for d in (4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40) if (m, d) in G and 'sing_ms' in G[(m, d)] and G[(m, d)]['sing_ms'] >= 50]
    if len(pts) >= 2:
        x = np.log([a for a, _ in pts]); y = np.log([b for _, b in pts]); print(f'm={m}: points>=50ms {pts}  log-log slope in d (rough, not a fit-with-CI): {np.polyfit(x, y, 1)[0]:.2f}')
# MITM 3+1
rows = {}
for f in sorted(glob.glob('out_m31_*.jsonl')):
    o = json.loads(open(f).read()); rows.setdefault(o['bits'], []).append(o)
print('MITM 3+1 (table of triple sums): bits s ntriples adds_pre(avg) T_test adds(avg) T_test wall(avg s) planted_found')
bs = sorted(rows); P = []; Tt = []; Pre = []
for b in bs:
    o = rows[b]; ta = np.mean([r['adds'] for x in o for r in x['rand']]); tw = np.mean([r['t'] for x in o for r in x['rand']])
    pre = np.mean([x['adds_pre'] for x in o]); pf = all(r['found'] for x in o for r in x['planted'])
    p = np.mean([x['p'] for x in o]); P.append(p); Tt.append(ta); Pre.append(pre)
    print(b, np.mean([x['s'] for x in o]), np.mean([x['ntriples'] for x in o]), f'{pre:.0f}', f'{ta:.0f}', f'{tw:.2e}', pf)
if len(P) > 2:
    print('naive slopes (deterministic counts): T_test', np.polyfit(np.log(P), np.log(Tt), 1)[0], ' precompute', np.polyfit(np.log(P), np.log(Pre), 1)[0])
