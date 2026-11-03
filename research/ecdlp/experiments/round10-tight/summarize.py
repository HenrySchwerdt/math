"""Summarize raw outputs: deficit D(N)=N-1-mindeg(N) = length of the run of zero Newton coefficients c_{N-1},c_{N-2},...
Compare with the heuristic model that each c_j (j>=2) vanishes independently with prob 1/p."""
import json, sys, collections
files = sys.argv[1:]
recs = [r for f in files for r in json.load(open(f))]
def run(sel, label):
    for name in ('zk', 'zk2'):
        D = collections.Counter(); e1 = e2 = e3 = 0.0; maxD = (0, None); n = 0
        for r in sel:
            Nm = (r['r']-1)//2; zs = set(j for j in r[name] if j >= 2); p = r['p']
            for N in range(4, Nm+1):
                d = 0
                while (N-1-d) in zs: d += 1
                D[d] += 1; n += 1; e1 += 1/p; e2 += 1/p**2; e3 += 1/p**3
                if d > maxD[0]: maxD = (d, (p, r['a'], r['b'], r['r'], N))
        print('%-22s %-3s cases=%6d (case,N)=%8d  D>=1: obs %5d exp %7.1f | D>=2: obs %3d exp %6.1f | D>=3: obs %2d exp %5.2f | maxD %s'
              % (label, name, len(sel), n, sum(v for d, v in D.items() if d >= 1), e1, sum(v for d, v in D.items() if d >= 2), e2, sum(v for d, v in D.items() if d >= 3), e3, maxD))
gen = [r for r in recs if not r['anom']]
run(recs, 'all')
run(gen, 'non-anomalous')
run([r for r in recs if r['anom'] and not r['j0']], 'anomalous, j!=0')
run([r for r in recs if r['anom'] and r['j0']], 'anomalous, j=0')
run([r for r in recs if r['j0'] and not r['anom']], 'j=0 non-anomalous')
run([r for r in recs if r['j1728']], 'j=1728')
# top level N=(r-1)/2 only
for name in ('zk', 'zk2'):
    for lab, sel in (('non-anomalous', gen), ('anomalous j!=0', [r for r in recs if r['anom'] and not r['j0']]), ('anomalous j=0', [r for r in recs if r['anom'] and r['j0']])):
        obs = sum(((r['r']-1)//2 - 1) in r[name] for r in sel); exp = sum(1/r['p'] for r in sel)
        print('N=(r-1)/2 only', name, lab, 'cases', len(sel), 'deficit>=1 obs', obs, 'exp %.1f' % exp)
print('total curve/point cases', len(recs), 'distinct primes', len(set(r['p'] for r in recs)), 'p range', min(r['p'] for r in recs), max(r['p'] for r in recs))
