import json, sys, collections
recs = json.load(open(sys.argv[1]))
def stats(sel, label):
    for name in ('zk', 'zk2'):
        D = collections.Counter(); lv = 0; z = 0; exp = 0.0; top = 0; topz = 0; topexp = 0.0; maxD = (0, None)
        for r in sel:
            Nm = (r['r'] - 1) // 2; zs = set(j for j in r[name] if j >= 2)
            for N in range(3, Nm + 1):          # deficit at N = # trailing zero coefficients c_{N-1}, c_{N-2},...
                d = 0
                while (N - 1 - d) in zs: d += 1
                D[d] += 1; lv += 1
                if d > maxD[0]: maxD = (d, (r['p'], r['a'], r['b'], r['r'], N))
            z += len(zs); exp += (Nm - 2) / r['p']
            top += 1; topexp += 1 / r['p']; topz += ((Nm - 1) in zs)
        print('%-9s %-3s cases=%d (case,N)=%d zeros=%d exp=%.1f | N=Nmax: zero %d exp %.1f | deficit hist %s maxD %s' % (label, name, len(sel), lv, z, exp, topz, topexp, dict(sorted(D.items())), maxD))
stats(recs, 'all')
stats([r for r in recs if r['anom']], 'anomalous')
stats([r for r in recs if r['j0']], 'j=0')
stats([r for r in recs if r['j1728']], 'j=1728')
stats([r for r in recs if r['r'] == (r['n'])], 'prime-order-group')
