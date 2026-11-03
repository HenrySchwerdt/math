"""3+1 finder with a precomputed table of all triple sums (x-coordinates): T_test = 2c EC adds/target, precompute ~ 2*M*c adds.
Usage: run_mitm31.py BITS SEED NRAND NPLANT -> one JSON line."""
import sys, json, time, random
from lib18 import *
bits, seed, nr, npl = map(int, sys.argv[1:5])
I = gen_instance(bits, seed, 1.0); E = I['E']; cls = I['cls']; p = I['p']; rng = random.Random(31 + bits * 7 + seed)
D = pair_sums(E, cls); c = len(cls)
t0 = time.time(); TR = {}; adds_pre = 0
for xU, (U, i, j, sg) in D.items():
    for k in range(c):
        for sg2 in (1, -1):
            W = E.add(U, cls[k] if sg2 > 0 else E.neg(cls[k])); adds_pre += 1
            if W is not None and W[0] not in TR: TR[W[0]] = (W, xU, k)
t_pre = time.time() - t0
out = dict(bits=bits, seed=seed, p=p, s=2 * c, nclasses=c, ntriples=len(TR), adds_pre=adds_pre, t_pre=t_pre, rand=[], planted=[])
for kind, n in (('rand', nr), ('planted', npl)):
    for _ in range(n):
        if kind == 'rand': R = E.rand_point(rng)
        else:
            idx = rng.sample(range(c), 4); pts = [cls[i] if rng.random() < .5 else E.neg(cls[i]) for i in idx]
            R = E.add(E.add(pts[0], pts[1]), E.add(pts[2], pts[3]))
            if R is None: continue
        adds = 0; found = False; t0 = time.perf_counter()
        for q in cls:
            for T in (E.sub(R, q), E.add(R, q)):
                adds += 1
                if T is not None and T[0] in TR: found = True
        out[kind].append(dict(adds=adds, t=time.perf_counter() - t0, found=found))
print(json.dumps(out), flush=True)
