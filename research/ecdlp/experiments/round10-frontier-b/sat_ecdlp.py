"""F-B1: CNF encoding of [k]P = Q (bits of k unknown, arithmetic circuits mod p), solver scaling vs rho.
Usage: python3 sat_ecdlp.py [--selftest]  (seeded; solver: pysat Glucose4, conflict budget)."""
import sys, time, random, json, math
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime
from pysat.solvers import Glucose4

class CNF:
    def __init__(s):
        s.n = 1; s.cl = []; s.T = s.new(); s.cl.append([s.T])
    def new(s): s.n += 1; return s.n
    def vec(s, m): return [s.new() for _ in range(m)]
    def const(s, v, m): return [s.T if (v >> i) & 1 else -s.T for i in range(m)]
    def isT(s, l): return l == s.T
    def isF(s, l): return l == -s.T
    def AND(s, a, b):
        if s.isF(a) or s.isF(b): return -s.T
        if s.isT(a): return b
        if s.isT(b): return a
        c = s.new(); s.cl += [[-c, a], [-c, b], [c, -a, -b]]; return c
    def XOR(s, a, b):
        if s.isF(a): return b
        if s.isF(b): return a
        if s.isT(a): return -b
        if s.isT(b): return -a
        c = s.new(); s.cl += [[-c, a, b], [-c, -a, -b], [c, -a, b], [c, a, -b]]; return c
    def OR(s, a, b): return -s.AND(-a, -b)
    def MUX(s, k, a, b):  # k ? a : b
        return s.OR(s.AND(k, a), s.AND(-k, b))
    def fa(s, a, b, c):
        t = s.XOR(a, b); return s.XOR(t, c), s.OR(s.AND(a, b), s.AND(t, c))
    def add(s, A, B, width):  # unsigned add, result width bits (truncating carry out unless width > len)
        A = A + [-s.T] * (width - len(A)); B = B + [-s.T] * (width - len(B))
        out = []; c = -s.T
        for i in range(width):
            o, c = s.fa(A[i], B[i], c); out.append(o)
        return out
    def eq(s, A, B):
        w = max(len(A), len(B)); A = A + [-s.T] * (w - len(A)); B = B + [-s.T] * (w - len(B))
        for a, b in zip(A, B): s.cl += [[-a, b], [a, -b]]
    def lt_const(s, A, c):  # assert A < c (A bit list LSB first)
        m = len(A)
        # A<c : exists i with c_i=1, A_i=0, higher bits equal
        # encode by forbidding A >= c: for each i where c_i=0 : not(A_i and all higher bits equal c) ... use prefix scan
        eqh = s.T  # all higher bits equal so far
        terms = []
        for i in reversed(range(m)):
            ci = (c >> i) & 1
            if ci:
                terms.append(s.AND(eqh, -A[i])); eqh = s.AND(eqh, A[i])
            else:
                eqh = s.AND(eqh, -A[i])
        r = -s.T
        for t in terms: r = s.OR(r, t)
        s.cl.append([r])
    def mulv(s, A, B):  # unsigned product, len(A)+len(B) bits
        w = len(A) + len(B); acc = [-s.T] * w
        for j, b in enumerate(B):
            row = [-s.T] * j + [s.AND(a, b) for a in A]
            acc = s.add(acc, row, w)
        return acc
    def mulc(s, A, c):
        w = len(A) + c.bit_length() + 1; acc = [-s.T] * w
        for j in range(c.bit_length()):
            if (c >> j) & 1: acc = s.add(acc, [-s.T] * j + A, w)
        return acc

def modmul(C, A, B, p, m):
    q = C.vec(m); r = C.vec(m); C.lt_const(r, p); C.lt_const(q, p)
    C.eq(C.mulv(A, B), C.add(C.mulc(q, p), r, 2 * m + 1))
    return r
def modadd(C, A, B, p, m):  # (A+B) mod p
    s_ = C.new(); r = C.vec(m); C.lt_const(r, p)
    C.eq(C.add(A, B, m + 1), C.add(r, C.mulc([s_], p), m + 1)); return r
def modsub(C, A, B, p, m):  # A-B mod p : r+B = A mod p
    r = C.vec(m); C.lt_const(r, p)
    s_ = C.new()
    C.eq(C.add(r, B, m + 1), C.add(A, C.mulc([s_], p), m + 1)); return r

def encode(E, P, Q, S, n):
    p = E.p; m = p.bit_length(); C = CNF()
    kb = C.vec(n)
    x = C.const(S[0], m); y = C.const(S[1], m)
    Ci = P
    for i in range(n):
        cx, cy = Ci
        cxv, cyv = C.const(cx, m), C.const(cy, m)
        dx = modsub(C, x, cxv, p, m); dy = modsub(C, y, cyv, p, m)
        C.cl.append([d for d in dx])  # dx != 0
        lam = C.vec(m); C.lt_const(lam, p)
        C.eq(modmul(C, lam, dx, p, m), dy)
        l2 = modmul(C, lam, lam, p, m)
        x3 = modsub(C, modsub(C, l2, x, p, m), cxv, p, m)
        t = modmul(C, lam, modsub(C, x, x3, p, m), p, m)
        y3 = modsub(C, t, y, p, m)
        x = [C.MUX(kb[i], a, b) for a, b in zip(x3, x)]
        y = [C.MUX(kb[i], a, b) for a, b in zip(y3, y)]
        Ci = E.add(Ci, Ci)
    T = E.add(Q, S)
    C.eq(x, C.const(T[0], m)); C.eq(y, C.const(T[1], m))
    return C, kb

def find_instance(rng, m):
    while True:
        p = rng.randrange(1 << (m - 1), 1 << m)
        if not is_prime(p) or p < 7: continue
        a, b = rng.randrange(p), rng.randrange(p)
        try: E = Curve(a, b, p)
        except ValueError: continue
        N = E.order()
        if not is_prime(N) or N == p: continue
        pts = E.points(); P = rng.choice(pts[1:])
        S = rng.choice(pts[1:])
        return E, P, N, S

def solve(C, kb, budget, tlimit):
    s = Glucose4(bootstrap_with=C.cl, use_timer=True)
    s.conf_budget(budget)
    t0 = time.time()
    res = s.solve_limited()
    dt = time.time() - t0; st = s.accum_stats()
    model = s.get_model() if res else None
    s.delete()
    return res, dt, st['conflicts'], model

def run(ms, reps, seed, budget):
    rng = random.Random(seed); out = []
    for m in ms:
        for rep in range(reps):
            E, P, N, S = find_instance(rng, m)
            for tries in range(50):
                k = rng.randrange(1, N)
                Q = E.mul(k, P)
                # skip instances with exceptional (R_i = +-C_i) steps along true path
                R = S; ok = True; Ci = P
                for i in range(N.bit_length()):
                    if R is None or R[0] == Ci[0]: ok = False; break
                    if (k >> i) & 1:
                        R = E.add(R, Ci)
                    Ci = E.add(Ci, Ci)
                if ok: break
            n = N.bit_length()
            C, kb = encode(E, P, Q, S, n)
            res, dt, conf, model = solve(C, kb, budget, None)
            correct = None
            if res:
                kk = sum((1 if model[abs(v) - 1] > 0 else 0) << i for i, v in enumerate(kb))
                correct = (E.mul(kk, P) == Q)
            out.append(dict(m=m, p=E.p, r=N, n=n, vars=C.n, clauses=len(C.cl), res=res, secs=round(dt, 3),
                            conflicts=conf, correct=correct, rho_ops=round(math.sqrt(math.pi * N / 2), 1)))
            print(json.dumps(out[-1]), flush=True)
    return out

if __name__ == '__main__':
    if '--selftest' in sys.argv:
        run([6, 7, 8], 2, 1, 10**6)
    else:
        ms = [int(a) for a in sys.argv[1].split(',')]
        run(ms, int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
