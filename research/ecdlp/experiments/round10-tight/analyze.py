import json, sys, collections
recs = json.load(open(sys.argv[1]))
for name in ('zk', 'zk2'):
    tot = 0; lev = 0; cases_def = 0; ex = []; byN = collections.Counter()
    expected = 0.0
    for r in recs:
        Nmax = (r['r'] - 1) // 2
        zs = [j for j in r[name] if j >= 2]  # level j<->deficit at N=j+1 (indep. of c0,c1 which are nonzero/trivial for k; for k2 see below)
        lev += Nmax - 2; expected += (Nmax - 2) / r['p']
        tot += len(zs)
        if zs: cases_def += 1; ex.append((r['p'], r['a'], r['b'], r['r'], Nmax, zs[:6], r['anom'], r['j0'], r['j1728']))
    print(name, 'cases', len(recs), 'levels', lev, 'zero coeffs', tot, 'expected(1/p each) %.1f' % expected, 'cases with a deficit', cases_def)
    print('  frac of zeros at N: first examples'); 
    for e in ex[:8]: print('  ', e)
    nz = collections.Counter()
    for r in recs:
        Nmax = (r['r'] - 1) // 2
        for j in r[name]:
            if j >= 2: nz[round(j / Nmax, 1)] += 1
    print('  zero position j/Nmax histogram', sorted(nz.items()))
