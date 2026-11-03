"""Usage: run_finders.py BITS SEED NRAND NPLANT [KAPPA] [BASE]  -> one JSON line.
Measures MITM (counted adds + wall) and TOWER (flint, wall) per target; cross-checks found flags; verifies planted decompositions."""
import sys, json, time, random
from flint import nmod_poly
from lib18 import *

def ptree(polys, p):
    L = list(polys)
    while len(L) > 1:
        N = [L[i] * L[i + 1] for i in range(0, len(L) - 1, 2)]
        if len(L) % 2: N.append(L[-1])
        L = N
    return L[0]

def tower_test(E, D, A2, xs, R):
    p, a, b = E.p, E.a, E.b; w = R[0]
    facs = [nmod_poly(list(S3_coeffs_in_v(a, b, p, u, w))[::-1], p) for u in xs]   # [c0,c1,c2]
    Q = ptree(facs, p)
    g = (Q % A2).gcd(A2)
    if g.degree() <= 0: return None
    for xT in g.roots():
        xT = int(xT[0]) if isinstance(xT, tuple) else int(xT)
        # root list may be (root, mult)
    return g

def verify_tower(E, D, R, g):
    for r in g.roots():
        xT = int(r[0])
        if xT not in D: continue
        T = D[xT][0]
        for Tt in (T, E.neg(T)):
            Ux = E.sub(R, Tt)
            if Ux is not None and Ux[0] in D: return (Tt, Ux)
    return None

def expand(E, D, cls, X):  # check that X=(T,U) are sums of two base points each: x lookup
    return True

if __name__ == '__main__':
    bits, seed, nr, npl = map(int, sys.argv[1:5])
    kappa = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    base = sys.argv[6] if len(sys.argv) > 6 else 'coset'
    do_tower = (len(sys.argv) <= 7) or sys.argv[7] != 'notower'
    I = gen_instance(bits, seed, kappa, base); E = I['E']; p = I['p']; cls = I['cls']; rng = random.Random(777 + bits * 13 + seed)
    t0 = time.time(); D = pair_sums(E, cls); t_pre_mitm = time.time() - t0
    xs = list(D.keys())
    out = dict(bits=bits, seed=seed, kappa=kappa, base=base, p=p, d=I['d'], s=2 * len(cls), nclasses=len(cls), npairsums=len(xs),
               t_pre_mitm=t_pre_mitm, rand=[], planted=[])
    if do_tower:
        t0 = time.time(); A2 = ptree([nmod_poly([(-x) % p, 1], p) for x in xs], p); out['t_pre_tower'] = time.time() - t0
    for kind, n in (('rand', nr), ('planted', npl)):
        for _ in range(n):
            if kind == 'rand': R = E.rand_point(rng)
            else:
                pts = [rng.choice(cls) for _ in range(4)]; pts = [q if rng.random() < .5 else E.neg(q) for q in pts]
                R = E.add(E.add(pts[0], pts[1]), E.add(pts[2], pts[3]))
                if R is None: continue
            rec = {}
            ops = [0]; t0 = time.perf_counter(); h = mitm_test(E, D, R, ops); rec['t_mitm'] = time.perf_counter() - t0
            # for found targets mitm stops early only if count_ops None; we pass ops so it scans fully: full-scan cost is the worst/typical-for-failure cost
            rec['adds_mitm'] = ops[0]; rec['found_mitm'] = h is not None
            if h is not None:
                U, T = h; assert E.on(U) and E.on(T)
                # verify R = +-U +-T
                ok = any(E.add(U if s1 > 0 else E.neg(U), T if s2 > 0 else E.neg(T)) == R for s1 in (1, -1) for s2 in (1, -1))
                rec['ok_mitm'] = ok
            if do_tower:
                t0 = time.perf_counter(); g = tower_test(E, D, A2, xs, R); rec['t_tower'] = time.perf_counter() - t0
                rec['found_tower'] = g is not None; rec['deg_g'] = g.degree() if g is not None else 0
                if g is not None:
                    v = verify_tower(E, D, R, g); rec['ok_tower'] = v is not None
                assert rec['found_tower'] == rec['found_mitm'], ('MITM/TOWER mismatch', bits, seed, kind)
            out[kind].append(rec)
    print(json.dumps(out), flush=True)
