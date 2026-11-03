import json, glob, collections
from common import *
def load(pattern):
    rows = []
    for fn in sorted(glob.glob(os.path.join(HERE, pattern))):
        rows += [json.loads(l) for l in open(fn)]
    return rows
meth = {'rho': load('out_rho.jsonl')}
for m in ['l2', 'l3', 'm3', 'm3x']: meth[m] = load(f'out_a1_{m}_*.jsonl')
res = {}
for m, rows in meth.items():
    ok = [r for r in rows if r['correct']]
    res[m] = fit([math.log2(r['r']) for r in ok], [math.log2(r['adds']) for r in ok])
    print(f"{m}: n={len(ok)}/{len(rows)} alpha={res[m]['alpha']:.3f} se={res[m]['se']:.3f} CI95=[{res[m]['lo']:.3f},{res[m]['hi']:.3f}] c={res[m]['c']:.2f}")
print()
sizes = SIZES
def gm(rows, b, key='adds'):
    v = [math.log2(r[key]) for r in rows if r['bits'] == b and r['correct']]
    return 2 ** (sum(v) / len(v)) if v else None
hdr = '| bits | rho U1 | ' + ' | '.join(f'{m} U1 (succ)' for m in ['l2', 'l3', 'm3', 'm3x']) + ' | l2/rho | l3/rho | m3/rho |'
print(hdr); print('|' + '---|' * (hdr.count('|') - 1))
for b in sizes:
    g = {m: gm(meth[m], b) for m in meth}
    sc = {m: f"{sum(1 for r in meth[m] if r['bits']==b and r['correct'])}/{sum(1 for r in meth[m] if r['bits']==b)}" for m in meth}
    f = lambda m: '-' if g[m] is None else f"{g[m]:.0f} ({sc[m]})"
    ra = lambda m: '-' if g[m] is None else f"{g[m]/g['rho']:.1f}"
    print(f"| {b} | {g['rho']:.0f} ({sc['rho']}) | " + ' | '.join(f(m) for m in ['l2', 'l3', 'm3', 'm3x']) + f" | {ra('l2')} | {ra('l3')} | {ra('m3')} |")
print()
for m in ['l2', 'l3', 'm3']:
    print(m, 'median s per size', {b: sorted(r['s'] for r in meth[m] if r['bits'] == b and r['correct'])[len([1 for r in meth[m] if r['bits']==b and r['correct']])//2] for b in sizes if gm(meth[m], b)},
          'mean attempts', round(sum(r.get('attempts',1) for r in meth[m])/len(meth[m]),2))
    print(m, 'LA mulmods gm', {b: round(gm(meth[m], b, 'mulmods') or 0) for b in sizes if gm(meth[m], b)})
json.dump(res, open(os.path.join(HERE, 'fits.json'), 'w'), indent=1)
# model check: s*p / adds etc
for m in ['l2', 'l3']:
    print(m, 'adds/sqrt(p*s):', {b: round(sum(r['adds']/math.sqrt(r['r']*r['s']) for r in meth[m] if r['bits']==b and r['correct'])/max(1,len([1 for r in meth[m] if r['bits']==b and r['correct']])),2) for b in sizes})
