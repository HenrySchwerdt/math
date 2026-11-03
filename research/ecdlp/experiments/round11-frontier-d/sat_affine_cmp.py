"""Comparator: round-10 affine Weierstrass encoding (imported unchanged) in the round-11 harness, same solvers/limits.
Usage: python3 sat_affine_cmp.py gen LO HI REPS SEED > aff_instances.jsonl ; python3 sat_affine_cmp.py run aff_instances.jsonl SOLVER TLIMIT OUT [--xor]"""
import sys, json, random, time, math, multiprocessing as mp
sys.path.insert(0, '../round10-frontier-b'); sys.path.insert(0, '../lib')
import sat_ecdlp as S10
from sat_ladder import XCNF
from toyec import Curve

def gen(lo, hi, reps, seed):
    rng = random.Random(seed)
    for n in range(lo, hi + 1):
        for _ in range(reps):
            while True:   # round-10 generator with m chosen so that bitlen(r)=n (m = n or n+1)
                m = n + rng.choice([0, 1])
                E, P, N, Sp = S10.find_instance(rng, m)
                if N.bit_length() != n: continue
                for tries in range(50):
                    k = rng.randrange(1, N); Q = E.mul(k, P); R = Sp; ok = True; Ci = P
                    for i in range(N.bit_length()):
                        if R is None or R[0] == Ci[0]: ok = False; break
                        if (k >> i) & 1: R = E.add(R, Ci)
                        Ci = E.add(Ci, Ci)
                    if ok: break
                if ok: break
            print(json.dumps(dict(n=n, p=E.p, a=E.a, b=E.b, r=N, P=P, S=Sp, k=k, Q=Q)))

def one(inst, solver, tlimit, xor, q):
    E = Curve(inst['a'], inst['b'], inst['p']); P = tuple(inst['P']); Sp = tuple(inst['S']); Q = tuple(inst['Q'])
    S10.CNF = (lambda: XCNF(True)) if xor else (lambda: XCNF(False))
    C, kb = S10.encode(E, P, Q, Sp, inst['n'])
    res = dict(n=inst['n'], p=inst['p'], r=inst['r'], solver=solver, xor=xor, vars=C.n, clauses=len(C.cl), xors=len(C.xors), rho_ops=round(math.sqrt(math.pi * inst['r'] / 2), 1))
    t0 = time.time()
    if solver == 'cms':
        import pycryptosat
        Sv = pycryptosat.Solver(threads=1)
        for c in C.cl: Sv.add_clause(c)
        for lits, rhs in C.xors:
            par = rhs
            for l in lits:
                if l < 0: par = not par
            Sv.add_xor_clause([abs(l) for l in lits], par)
        sat, model = Sv.solve(); conf = None; model = list(model)[1:] if sat else None
    else:
        from pysat.solvers import Solver
        import threading
        Sv = Solver(name=solver, bootstrap_with=C.cl)
        if solver == 'glucose4':
            Sv.conf_budget(4_000_000); tm = threading.Timer(tlimit, lambda: Sv.interrupt()); tm.start()
            sat = Sv.solve_limited(expect_interrupt=True); tm.cancel(); conf = Sv.accum_stats()['conflicts']
        else:
            sat = Sv.solve(); conf = Sv.accum_stats().get('conflicts')
        model = Sv.get_model() if sat else None
    dt = time.time() - t0; ok = None
    if sat:
        kk = sum((1 if model[abs(v) - 1] > 0 else 0) << i for i, v in enumerate(kb)); ok = (E.mul(kk, P) == Q)
    res.update(sat=sat, secs=round(dt, 2), conflicts=conf, key_ok=ok); q.put(res)

if __name__ == '__main__':
    if sys.argv[1] == 'gen': gen(*map(int, sys.argv[2:6]))
    else:
        import sat_ladder as L
        L.solve_one = lambda inst, solver, tl, xor, q: one(inst, solver, tl, xor, q)
        insts = [json.loads(l) for l in open(sys.argv[2])]
        L.run_all(insts, sys.argv[3], float(sys.argv[4]), sys.argv[5], '--xor' in sys.argv)
