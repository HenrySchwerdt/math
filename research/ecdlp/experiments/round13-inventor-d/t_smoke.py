import sys; sys.path.insert(0,'.')
from d2lib import *
from toyec import dlog_bruteforce
# row-level correctness at small sizes: every relation holds with true logs
for bits in (12,14):
  for seed in (1,2,3):
    inst = gen_instance(bits, seed, 0); E = Curve(inst['a'],inst['b'],inst['p']); r=inst['r']
    rng = random.Random(5)
    V = build_V(inst, fb_coset(inst, rng)); F = Finder(inst, V)
    logs = [dlog_bruteforce(E, inst['P'], (x, V[x])) for x in F.keys]
    bad = tot = 0
    for _ in range(200):
        a_, b_ = rng.randrange(1, r), rng.randrange(1, r)
        T = E.add(E.mul(a_, inst['P']), E.mul(b_, inst['Q']))
        if T is None: continue
        for (c1,s1,c2,s2) in F.decompositions(T):
            lhs = (a_ + b_*inst['k']) % r
            rhs = (s1*logs[c1] + (s2*logs[c2] if c2 is not None else 0)) % r
            tot += 1; bad += (lhs != rhs)
    print(bits, seed, 'relations', tot, 'bad', bad)
    for kind in ('coset','smallx'):
        res = run_pipeline(inst, kind, 1); print(' ', kind, res['ok'], res['s'], res['targets'], res['relations'])
