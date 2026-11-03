import json, glob, math
from collections import defaultdict
agg = defaultdict(lambda: [0, 0, 0, 0.0, 0.0])
for f in sorted(glob.glob('out_lambda_*.jsonl')):
    o = json.loads(open(f).read()); k = (o['bits'], o['kappa'])
    n = len(o['rand']); h = sum(r['found_mitm'] for r in o['rand'])
    c = o['nclasses']; p = o['p']
    lam = 1 - math.exp(-16 * math.comb(c, 4) / p)
    a = agg[k]; a[0] += n; a[1] += h; a[3] += n * lam; a[4] += n * (o['s'] ** 4 / (24 * p)); a[2] += 1
print('bits kappa  N  hits  rate  [Wilson95]  model(16C(c,4)/p)  s^4/(24p)  (|B| avg)')
for k in sorted(agg):
    n, h, _, lm, l2 = agg[k]; ph = h / n
    z = 1.96; den = 1 + z * z / n; ctr = (ph + z * z / (2 * n)) / den; hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    print(k[0], k[1], n, h, f'{ph:.4f} [{ctr-hw:.4f},{ctr+hw:.4f}] model {lm/n:.4f} s4/24p {l2/n:.4f}')
