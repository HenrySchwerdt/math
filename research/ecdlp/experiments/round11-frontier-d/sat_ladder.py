"""T1 (round 11): x-only Montgomery-ladder CNF/XOR encoding of [k]P=Q; solvers Glucose4 / CaDiCaL / CryptoMiniSat.
Usage: python3 sat_ladder.py gen N_MIN N_MAX REPS SEED > instances.jsonl
       python3 sat_ladder.py run instances.jsonl SOLVER[glucose4|cadical195|cms] TLIMIT OUT.jsonl [--xor]
"""
import sys, json, random, time, math, multiprocessing as mp
sys.path.insert(0, '../round10-frontier-b'); sys.path.insert(0, '../lib')
from sat_ecdlp import CNF, modmul, modadd, modsub
from toyec import is_prime

# ---------- number theory ----------
def ladder(k, x1, A, p):
    a24 = (A + 2) * pow(4, -1, p) % p
    X0, Z0, X1, Z1 = 1, 0, x1 % p, 1
    for i in reversed(range(max(k.bit_length(), 1))):
        U = (X0 - Z0) * (X1 + Z1) % p; V = (X0 + Z0) * (X1 - Z1) % p
        Xa = (U + V) ** 2 % p; Za = x1 * (U - V) ** 2 % p
        if (k >> i) & 1: X0, Z0 = X1, Z1; sel = (X0, Z0)
        # recompute generically below
        # (written simply: use cswap form)
        pass
    return None

def ladder(k, x1, A, p):  # standard cswap ladder, returns (X:Z) of [k]P
    a24 = (A + 2) * pow(4, -1, p) % p
    R0 = (1, 0); R1 = (x1 % p, 1)
    def add(R0, R1):
        U = (R0[0] - R0[1]) * (R1[0] + R1[1]) % p; V = (R0[0] + R0[1]) * (R1[0] - R1[1]) % p
        return ((U + V) ** 2 % p, x1 * (U - V) ** 2 % p)
    def dbl(R):
        a = (R[0] + R[1]) ** 2 % p; b = (R[0] - R[1]) ** 2 % p; e = (a - b) % p
        return (a * b % p, e * (b + a24 * e) % p)
    for i in reversed(range(k.bit_length())):
        if (k >> i) & 1: R0, R1 = add(R0, R1), dbl(R1)
        else: R0, R1 = dbl(R0), add(R0, R1)
    return R0

def legendre(a, p): return 0 if a % p == 0 else (1 if pow(a, (p - 1) // 2, p) == 1 else -1)

def gen_instance(rng, n):
    while True:
        p = rng.randrange(1 << (n + 1), 1 << (n + 2))
        if not is_prime(p) or p < 11: continue
        A = rng.randrange(3, p - 2)
        N = p + 1 + sum(legendre(x ** 3 + A * x * x + x, p) for x in range(p))
        if N % 4 or not is_prime(N // 4) or (N // 4).bit_length() != n: continue
        r = N // 4
        for _ in range(100):
            x = rng.randrange(2, p)
            if legendre(x ** 3 + A * x * x + x, p) != 1: continue
            X, Z = ladder(4, x, A, p)
            if Z == 0: continue
            x1 = X * pow(Z, -1, p) % p
            if ladder(r, x1, A, p)[1] != 0: continue
            k = rng.randrange(1, r)
            X, Z = ladder(k, x1, A, p)
            return dict(n=n, p=p, A=A, r=r, x1=x1, k=k, xQ=X * pow(Z, -1, p) % p)

# ---------- encoding ----------
class XCNF(CNF):
    """CNF with optional native XOR gates (list self.xors of (lits, rhs): xor of lits == rhs)."""
    def __init__(s, native_xor=False):
        super().__init__(); s.native = native_xor; s.xors = []
    def XOR(s, a, b):
        if s.isF(a): return b
        if s.isF(b): return a
        if s.isT(a): return -b
        if s.isT(b): return -a
        c = s.new()
        if s.native: s.xors.append(([a, b, c], False))   # a^b^c = 0
        else: s.cl += [[-c, a, b], [-c, -a, -b], [c, -a, b], [c, a, -b]]
        return c

def modmulc(C, A, c, p, m):
    q = C.vec(c.bit_length()); r = C.vec(m); C.lt_const(r, p)
    lhs = C.mulc(A, c); rhs = C.add(C.mulc(q, p), r, max(len(lhs), len(q) + p.bit_length() + 1) + 1)
    C.eq(lhs, rhs); return r

def encode_ladder(inst, native_xor=False):
    p, A, r, x1, xQ, n = inst['p'], inst['A'], inst['r'], inst['x1'], inst['xQ'], inst['n']
    m = p.bit_length(); a24 = (A + 2) * pow(4, -1, p) % p
    C = XCNF(native_xor); kb = C.vec(n)
    C.lt_const(kb, r); C.cl.append(list(kb))            # 1 <= k < r
    cst = lambda v: C.const(v % p, m)
    R0 = (cst(1), cst(0)); R1 = (cst(x1), cst(1))
    mux = lambda b, U, V: [C.MUX(b, u, v) for u, v in zip(U, V)]
    for i in reversed(range(n)):
        b = kb[i]
        X0, Z0 = R0; X1, Z1 = R1
        # add(R0,R1)
        B0 = modsub(C, X0, Z0, p, m); A0 = modadd(C, X0, Z0, p, m)
        A1 = modadd(C, X1, Z1, p, m); B1 = modsub(C, X1, Z1, p, m)
        U = modmul(C, B0, A1, p, m); V = modmul(C, A0, B1, p, m)
        s = modadd(C, U, V, p, m); d = modsub(C, U, V, p, m)
        Xa = modmul(C, s, s, p, m); Za = modmulc(C, modmul(C, d, d, p, m), x1, p, m)
        # dbl(sel), sel = b ? R1 : R0
        Xs, Zs = mux(b, X1, X0), mux(b, Z1, Z0)
        As = modadd(C, Xs, Zs, p, m); Bs = modsub(C, Xs, Zs, p, m)
        AA = modmul(C, As, As, p, m); BB = modmul(C, Bs, Bs, p, m)
        E = modsub(C, AA, BB, p, m); Xd = modmul(C, AA, BB, p, m)
        Zd = modmul(C, E, modadd(C, BB, modmulc(C, E, a24, p, m), p, m), p, m)
        R0 = (mux(b, Xa, Xd), mux(b, Za, Zd)); R1 = (mux(b, Xd, Xa), mux(b, Zd, Za))
    X0, Z0 = R0
    C.cl.append(list(Z0))                                  # Z != 0
    C.eq(X0, modmulc(C, Z0, xQ, p, m) if xQ > 0 else C.const(0, m))
    return C, kb

def check(inst, kk): return kk != 0 and (lambda XZ: XZ[1] != 0 and XZ[0] * pow(XZ[1], -1, inst['p']) % inst['p'] == inst['xQ'])(ladder(kk, inst['x1'], inst['A'], inst['p']))

# ---------- solving ----------
def solve_one(inst, solver, tlimit, native_xor, q):
    t0 = time.time(); C, kb = encode_ladder(inst, native_xor); enc = time.time() - t0
    nv, ncl, nx = C.n, len(C.cl), len(C.xors)
    res = dict(n=inst['n'], p=inst['p'], r=inst['r'], solver=solver, xor=native_xor, vars=nv, clauses=ncl, xors=nx,
               enc_s=round(enc, 2), rho_ops=round(math.sqrt(math.pi * inst['r'] / 2), 1))
    t0 = time.time()
    if solver == 'cms':
        import pycryptosat
        S = pycryptosat.Solver(threads=1)
        for c in C.cl: S.add_clause(c)
        for lits, rhs in C.xors:
            par = rhs
            for l in lits:
                if l < 0: par = not par
            S.add_xor_clause([abs(l) for l in lits], par)
        ok, model = S.solve(); dt = time.time() - t0; conf = None
        model = list(model)[1:] if ok else None; sat = ok
    else:
        from pysat.solvers import Solver
        import threading
        assert not C.xors
        S = Solver(name=solver, bootstrap_with=C.cl, use_timer=(solver == 'glucose4'))
        if solver == 'glucose4':
            S.conf_budget(4_000_000)
            tm = threading.Timer(tlimit, lambda: S.interrupt()); tm.start()
            sat = S.solve_limited(expect_interrupt=True); tm.cancel()
            conf = S.accum_stats()['conflicts']
        else:
            sat = S.solve(); conf = S.accum_stats().get('conflicts')
        dt = time.time() - t0
        model = S.get_model() if sat else None
    ok_key = None
    if sat:
        kk = sum((1 if model[abs(v) - 1] > 0 else 0) << i for i, v in enumerate(kb))
        ok_key = check(inst, kk)
    res.update(sat=sat, secs=round(dt, 2), conflicts=conf, key_ok=ok_key); q.put(res)

def run_all(insts, solver, tlimit, out, native_xor, par=4):
    done = []; active = []; skip_n = set()
    pend = list(insts)
    with open(out, 'a') as f:
        while pend or active:
            while pend and len(active) < par:
                inst = pend.pop(0)
                if inst['n'] in skip_n: continue
                q = mp.Queue(); pr = mp.Process(target=solve_one, args=(inst, solver, tlimit, native_xor, q))
                pr.start(); active.append((pr, q, inst, time.time()))
            time.sleep(0.2)
            for a in list(active):
                pr, q, inst, t0 = a
                if not q.empty():
                    res = q.get(); pr.join(); active.remove(a)
                elif time.time() - t0 > tlimit + 10 or not pr.is_alive():
                    pr.kill(); pr.join(); active.remove(a); res = None
                    if not q.empty(): res = q.get()
                    else: res = dict(n=inst['n'], p=inst['p'], r=inst['r'], solver=solver, xor=native_xor, sat=None, secs=round(time.time() - t0, 2), conflicts=None, key_ok=None, rho_ops=round(math.sqrt(math.pi * inst['r'] / 2), 1), censored=True)
                else: continue
                if res.get('sat') is None: res['censored'] = True
                f.write(json.dumps(res) + '\n'); f.flush(); print(json.dumps(res), flush=True); done.append(res)
                # skip rule: all instances of one n censored -> larger n not run
                same = [d for d in done if d['n'] == inst['n']]
                if len(same) >= 3 and all(d.get('censored') for d in same):
                    skip_n.update(range(inst['n'] + 1, 100))

if __name__ == '__main__':
    if sys.argv[1] == 'gen':
        lo, hi, reps, seed = map(int, sys.argv[2:6]); rng = random.Random(seed)
        for n in range(lo, hi + 1):
            for _ in range(reps): print(json.dumps(gen_instance(rng, n)))
    else:
        insts = [json.loads(l) for l in open(sys.argv[2])]
        run_all(insts, sys.argv[3], float(sys.argv[4]), sys.argv[5], '--xor' in sys.argv)
