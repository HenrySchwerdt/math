"""POST-HOC (not pre-registered): rho steps-only cost and local slopes on sizes >= 18 bits."""
import json, glob
from common import *
def rho_split(inst, rng_seed):
    C = CC(inst['a'], inst['b'], inst['p']); r = inst['r']; P, Q = inst['P'], inst['Q']
    rng = random.Random(rng_seed); B = 32; T = []; ab = []
    for _ in range(B):
        a, b = rng.randrange(1, r), rng.randrange(1, r); T.append(C.add(C.mul(a, P), C.mul(b, Q))); ab.append((a, b))
    setup = C.n
    d = max(0, int(round(math.log2(max(1.0, math.sqrt(r) / 16))))); mask = (1 << d) - 1; seen = {}; steps = 0; starts = 0
    while True:
        a, b = rng.randrange(1, r), rng.randrange(1, r); c0 = C.n
        X = C.add(C.mul(a, P), C.mul(b, Q)); starts += C.n - c0
        for _ in range(20 * (mask + 1) + 50):
            if X is None: break
            steps += 1
            if X[0] & mask == 0:
                if X in seen:
                    a2, b2 = seen[X]
                    if (b - b2) % r != 0: return C.n, setup, starts, steps
                    break
                seen[X] = (a, b); break
            j = X[0] % B; X = C.add(X, T[j]); a = (a + ab[j][0]) % r; b = (b + ab[j][1]) % r
rows = []
for d in load_instances():
    n, setup, starts, steps = rho_split(d, d['seed'])
    rows.append(dict(bits=d['bits'], r=d['r'], total=n, setup=setup, starts=starts, steps=steps, walk=n - setup - starts))
json.dump(rows, open(os.path.join(HERE, 'out_rho_split.json'), 'w'))
print('rho: size, mean total, setup, starts, walk adds')
for b in SIZES:
    v = [x for x in rows if x['bits'] == b]; m = lambda k: sum(x[k] for x in v) / len(v)
    print(b, round(m('total')), round(m('setup')), round(m('starts')), round(m('walk')))
f_tot = fit([math.log2(x['r']) for x in rows], [math.log2(x['total']) for x in rows])
f_walk = fit([math.log2(x['r']) for x in rows], [math.log2(x['walk']) for x in rows])
f_steps = fit([math.log2(x['r']) for x in rows], [math.log2(x['total'] - x['setup']) for x in rows])
print('rho alpha total', f_tot['alpha'], f_tot['lo'], f_tot['hi']); print('rho alpha walk-only', f_walk['alpha'], f_walk['lo'], f_walk['hi'])
print('rho alpha total-minus-setup', f_steps['alpha'], f_steps['lo'], f_steps['hi'])
def load(pattern):
    out = []
    for fn in sorted(glob.glob(os.path.join(HERE, pattern))): out += [json.loads(l) for l in open(fn)]
    return out
print('local fits, sizes >= 18 bits (l2,l3) / >=16 (m3) / rho total-minus-setup >=18')
for m in ['l2', 'l3', 'm3']:
    rr = [r for r in load(f'out_a1_{m}_*.jsonl') if r['correct'] and r['bits'] >= (16 if m == 'm3' else 18)]
    f = fit([math.log2(r['r']) for r in rr], [math.log2(r['adds']) for r in rr]); print(m, round(f['alpha'], 3), '+-', round(f['se'], 3), [round(f['lo'], 3), round(f['hi'], 3)], f['n'])
rr = [x for x in rows if x['bits'] >= 18]
f = fit([math.log2(x['r']) for x in rr], [math.log2(x['total'] - x['setup']) for x in rr]); print('rho(total-setup)>=18', round(f['alpha'], 3), '+-', round(f['se'], 3), [round(f['lo'], 3), round(f['hi'], 3)])
f = fit([math.log2(x['r']) for x in rr], [math.log2(x['total']) for x in rr]); print('rho(total)>=18', round(f['alpha'], 3), '+-', round(f['se'], 3), [round(f['lo'], 3), round(f['hi'], 3)])
