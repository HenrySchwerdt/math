"""Round 17 / frontier H: DLP instruction set v2 = frontier-G generic ops + F_p field arithmetic, S_3, lifting, linear algebra.
Points: [a, b, v, e]  = aP + bQ + sum_g e[g]*G_g ; v = hidden true discrete log (VM-internal, used only to look up x
and to fix relation signs, which a real implementation reads off the y-coordinate); e = coefficients on lifted
'factor-base generators' G_g (created by LIFT, true log unknown to programs).
Cost unit = one elliptic group op (affine add/dbl = 1 inversion+2M ~ 12 field mults, so 1 field mult = 1/12).
"""
import os, sys, random, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from curves import make_curve, sqrt_mod

OPS = ['SETC', 'ADD', 'DBL', 'NEG', 'MOV', 'SETO', 'SETRAND', 'STEP', 'INS', 'LOOK', 'SOLVE', 'INC', 'ZERO',
       'IFLT', 'IFGE', 'IFMOD', 'IFEQX', 'IFLTX', 'IFDP',
       # new in round 17
       'FCTR', 'FCONST', 'FADD', 'FMUL', 'FINV', 'FSQRT', 'FRHS', 'FLEG', 'FRAND', 'FX', 'FS3', 'FS3EV', 'LIFT',
       'IFOK', 'IFSMALL', 'RELATE', 'MSOLVE']
OPI = {n: i for i, n in enumerate(OPS)}
NEWOPS = OPS[19:]
R4 = (0, 3)
RANGES = {
    'SETC': [R4, (0, 1), (0, 32), (1, 4)], 'ADD': [R4, R4, R4, (0, 0)], 'DBL': [R4, R4, (0, 0), (0, 0)],
    'NEG': [R4, R4, (0, 0), (0, 0)], 'MOV': [R4, R4, (0, 0), (0, 0)], 'SETO': [R4, (0, 0), (0, 0), (0, 0)],
    'SETRAND': [R4, (0, 0), (0, 0), (0, 0)], 'STEP': [R4, R4, (1, 4), (0, 0)],
    'INS': [R4, (0, 8), (1, 20), (0, 0)], 'LOOK': [R4, (0, 8), (1, 20), (0, 0)], 'SOLVE': [R4, R4, (0, 0), (0, 0)],
    'INC': [(0, 0)] * 4, 'ZERO': [(0, 0)] * 4,
    'IFLT': [(0, 1), (0, 32), (1, 4), (0, 0)], 'IFGE': [(0, 1), (0, 32), (1, 4), (0, 0)],
    'IFMOD': [(0, 1), (0, 32), (1, 4), (0, 0)], 'IFEQX': [R4, R4, (0, 0), (0, 0)], 'IFLTX': [R4, R4, (0, 0), (0, 0)],
    'IFDP': [R4, (0, 8), (0, 0), (0, 0)],
    'FCTR': [R4, (0, 1), (0, 32), (0, 0)],       # F[d] = (counter mod const(p,e,1)) + 1
    'FCONST': [R4, (0, 32), (1, 4), (0, 0)],     # F[d] = const(p,e,m)
    'FADD': [R4, R4, R4, (0, 0)], 'FMUL': [R4, R4, R4, (0, 0)], 'FINV': [R4, R4, (0, 0), (0, 0)],
    'FSQRT': [R4, R4, (0, 0), (0, 0)], 'FRHS': [R4, R4, (0, 0), (0, 0)], 'FLEG': [R4, (0, 0), (0, 0), (0, 0)],
    'FRAND': [R4, (0, 0), (0, 0), (0, 0)], 'FX': [R4, R4, (0, 0), (0, 0)],   # F[d] = x(point reg)
    'FS3': [R4, R4, R4, (0, 1)],                 # F[d] = a root of S_3(F[a], F[b], .)  (flag=ok); f4 selects the root
    'FS3EV': [R4, R4, R4, R4],                   # F[d] = S_3(F[a],F[b],F[c])
    'LIFT': [R4, R4, (0, 1), (0, 0)],            # point reg d <- (F[a], +-y) as new generator (flag=ok)
    'IFOK': [(0, 0)] * 4, 'IFSMALL': [R4, (0, 32), (1, 4), (0, 0)],
    'RELATE': [R4, R4, R4, (0, 0)],              # record  A (+-) B (+-) C = 0  if S_3 relation holds (flag=ok)
    'MSOLVE': [(0, 0)] * 4,                      # Gaussian elimination mod r on recorded relations
}
for n in OPS: assert n in RANGES, n
CONDS = ('IFLT', 'IFGE', 'IFMOD', 'IFEQX', 'IFLTX', 'IFDP', 'IFOK', 'IFSMALL')

def I(name, *f):
    f = list(f) + [0] * (4 - len(f)); return (OPI[name], *f)

def _const(n, e, m): return max(1, math.ceil(n ** (e / 32.0) - 1e-9) * m)
def _mulcost(c): return max(0, c.bit_length() + bin(c).count('1') - 2)
FM = 1.0 / 12.0
MAXROWS, MAXGENS = 400, 255

def run(prog, curve, k, seed, cap_factor=12.0):
    init, body = prog
    r, p, xt, xinv, Ac, Bc = curve['r'], curve['p'], curve['xt'], curve['xinv'], curve['a'], curve['b']
    cap = cap_factor * math.sqrt(r); sr = math.isqrt(r) + 1; M = 2 * sr
    rng = random.Random(seed); lb = r.bit_length(); lp = p.bit_length()
    verify_cost = math.ceil(1.5 * lb)
    R = [[0, 0, 0, None] for _ in range(4)]; F = [0, 0, 0, 0]
    ctr = [0, 0]; table = {}; W = {}
    st = dict(cost=0.0, steps=0, hits=0, ok=False)
    gens = {}; rows = []
    maxsteps = int(10 * cap) + 100

    def pt(a, b): return [a % r, b % r, (a + b * k) % r, None]
    def comb(A, B, sb):             # A + sb*B
        e = None
        if A[3] is not None or B[3] is not None:
            e = dict(A[3] or {})
            for g, c in (B[3] or {}).items():
                c = (e.get(g, 0) + sb * c) % r
                if c: e[g] = c
                else: e.pop(g, None)
        return [(A[0] + sb * B[0]) % r, (A[1] + sb * B[1]) % r, (A[2] + sb * B[2]) % r, e]
    def X(P): return xt[P[2]]

    def add_relation(terms):
        """terms = [(point, sign)] with true sum 0. Direct solve if no generators remain, else store a matrix row."""
        row = {}
        for P, s in terms:
            for col, c in ((0, P[0]), (1, P[1])):
                if c: row[col] = (row.get(col, 0) + s * c) % r
            for g, c in (P[3] or {}).items(): row[g + 2] = (row.get(g + 2, 0) + s * c) % r
        row = {c: v for c, v in row.items() if v}
        if not row: return None
        st['hits'] += 1
        if all(c < 2 for c in row):
            b = row.get(1, 0)
            if b == 0: return None
            cand = (-row.get(0, 0) * pow(b, -1, r)) % r
            st['cost'] += verify_cost
            return cand if cand == k % r else None
        if len(rows) < MAXROWS: rows.append(row)
        return None

    def relate_equal(A, B):
        if X(A) != X(B): return None
        s = -1 if A[2] == B[2] else 1      # A - B = 0 if same point, A + B = 0 if opposite
        return add_relation([(A, 1), (B, s)])

    def msolve():
        nr = len(rows)
        cols = sorted({c for rw in rows for c in rw if c >= 2}); nc = len(cols)
        if nr < nc + 1: st['cost'] += 0.5; return None
        st['cost'] += nr * max(nc, 1) * max(1, min(nr, nc)) * FM
        if st['cost'] > cap: return None
        ci = {c: i + 2 for i, c in enumerate(cols)}
        A = np.zeros((nr, nc + 2), dtype=np.int64)
        for i, rw in enumerate(rows):
            for c, v in rw.items(): A[i, ci.get(c, c)] = v
        used = 0
        for j in range(2, nc + 2):
            piv = None
            for i in range(used, nr):
                if A[i, j] % r: piv = i; break
            if piv is None: continue
            A[[used, piv]] = A[[piv, used]]
            A[used] = (A[used] * pow(int(A[used, j]), -1, r)) % r
            f = A[:, j].copy(); f[used] = 0
            A -= (f[:, None] * A[used][None, :]) % r; A %= r
            used += 1
        for i in range(used, nr):
            b = int(A[i, 1])
            if b:
                cand = (-int(A[i, 0]) * pow(b, -1, r)) % r
                st['cost'] += verify_cost
                if cand == k % r: return cand
        return None

    def s3coef(x1, x2):
        A2 = (x1 - x2) ** 2 % p
        B1 = (-2 * ((x1 + x2) * (x1 * x2 + Ac) + 2 * Bc)) % p
        C0 = ((x1 * x2 - Ac) ** 2 - 4 * Bc * (x1 + x2)) % p
        return A2, B1, C0

    def execute(code):
        n = len(code); i = 0
        while i < n:
            st['steps'] += 1
            if st['steps'] > maxsteps or st['cost'] > cap: return 'stop'
            op, f1, f2, f3, f4 = code[i]; name = OPS[op]; i += 1
            if name in CONDS:
                if name in ('IFLT', 'IFGE', 'IFMOD'):
                    T = _const(r, f2, f3); c = ctr[f1]
                    ok = (c < T) if name == 'IFLT' else (c >= T) if name == 'IFGE' else (c % T == T - 1)
                elif name == 'IFEQX': ok = X(R[f1]) == X(R[f2])
                elif name == 'IFLTX': ok = X(R[f1]) < X(R[f2])
                elif name == 'IFDP': ok = (X(R[f1]) & ((1 << f2) - 1)) == 0
                elif name == 'IFOK': ok = st['ok']
                else: ok = F[f1] < _const(p, f2, f3)
                if not ok: i += 1
                continue
            if name == 'SETC':
                c = _const(r, f3, f4); st['cost'] += _mulcost(c); R[f1] = pt(c, 0) if f2 == 0 else pt(0, c)
            elif name == 'ADD': R[f1] = comb(R[f2], R[f3], 1); st['cost'] += 1
            elif name == 'DBL': R[f1] = comb(R[f2], R[f2], 1); st['cost'] += 1
            elif name == 'NEG': R[f1] = comb([0, 0, 0, None], R[f2], -1)
            elif name == 'MOV': R[f1] = list(R[f2])
            elif name == 'SETO': R[f1] = [0, 0, 0, None]
            elif name == 'SETRAND': st['cost'] += 3 * lb; R[f1] = pt(rng.randrange(r), rng.randrange(r))
            elif name == 'STEP':
                nb = f3
                if nb not in W:
                    st['cost'] += 6 * lb + (1 << nb)
                    L = [pt(rng.randrange(r), rng.randrange(r)), pt(rng.randrange(r), rng.randrange(r))]
                    for j in range(2, 1 << nb): L.append(comb(L[-1], L[rng.randrange(j - 1)], 1))
                    W[nb] = L
                A = R[f2]; R[f1] = comb(A, W[nb][X(A) & ((1 << nb) - 1)], 1); st['cost'] += 1
            elif name == 'INS':
                kk = (X(R[f1]) >> f2) & ((1 << f3) - 1)
                if kk not in table and len(table) < M: table[kk] = R[f1]
            elif name == 'LOOK':
                kk = (X(R[f1]) >> f2) & ((1 << f3) - 1)
                if kk in table:
                    res = relate_equal(R[f1], table[kk])
                    if res is not None: return ('found', res)
            elif name == 'SOLVE':
                res = relate_equal(R[f1], R[f2])
                if res is not None: return ('found', res)
            elif name == 'INC': ctr[1] += 1
            elif name == 'ZERO': ctr[1] = 0
            # ---- field ops ----
            elif name == 'FCTR': F[f1] = (ctr[f2] % _const(p, f3, 1)) + 1
            elif name == 'FCONST': F[f1] = _const(p, f2, f3) % p
            elif name == 'FADD': F[f1] = (F[f2] + F[f3]) % p
            elif name == 'FMUL': F[f1] = F[f2] * F[f3] % p; st['cost'] += FM
            elif name == 'FINV':
                st['cost'] += 1.0; st['ok'] = F[f2] % p != 0
                F[f1] = pow(F[f2], -1, p) if st['ok'] else 0
            elif name == 'FSQRT':
                st['cost'] += 0.125 * lp; s = sqrt_mod(F[f2], p); st['ok'] = s is not None; F[f1] = s or 0
            elif name == 'FRHS': st['cost'] += 2 * FM; x = F[f2]; F[f1] = (x * x % p * x + Ac * x + Bc) % p
            elif name == 'FLEG': st['cost'] += 0.125 * lp; st['ok'] = pow(F[f1], (p - 1) // 2, p) == 1 if F[f1] % p else False
            elif name == 'FRAND': st['cost'] += 0.1; F[f1] = rng.randrange(p)
            elif name == 'FX':
                F[f1] = X(R[f2]) % p if R[f2][2] else 0; st['ok'] = R[f2][2] != 0
            elif name == 'FS3':
                st['cost'] += 0.125 * lp + 0.6
                A2, B1, C0 = s3coef(F[f2], F[f3])
                if A2 == 0:
                    st['ok'] = B1 != 0; F[f1] = (-C0 * pow(B1, -1, p)) % p if st['ok'] else 0
                else:
                    s = sqrt_mod(B1 * B1 - 4 * A2 * C0, p); st['ok'] = s is not None
                    F[f1] = ((-B1 + (s if f4 == 0 else -s)) * pow(2 * A2, -1, p)) % p if st['ok'] else 0
            elif name == 'FS3EV':
                st['cost'] += 0.5; A2, B1, C0 = s3coef(F[f2], F[f3]); x3 = F[f4]
                F[f1] = (A2 * x3 * x3 + B1 * x3 + C0) % p
            elif name == 'LIFT':
                st['cost'] += 0.125 * lp + 0.25; x = F[f2] % p
                v0 = xinv[x] if (x < len(xinv) and (x * x % p * x + Ac * x + Bc) % p != 0) else -1
                if v0 <= 0 or (x not in gens and len(gens) >= MAXGENS): st['ok'] = False; R[f1] = [0, 0, 0, None]
                else:
                    if x not in gens: gens[x] = len(gens)
                    s = 1 if f3 == 0 else -1
                    R[f1] = [0, 0, (s * v0) % r, {gens[x]: s % r}]; st['ok'] = True
            elif name == 'RELATE':
                st['cost'] += 0.5; A, B, C = R[f1], R[f2], R[f3]; st['ok'] = False
                if A[2] and B[2] and C[2] and X(A) % p == X(A):
                    for sb in (1, -1):
                        for sc in (1, -1):
                            if (A[2] + sb * B[2] + sc * C[2]) % r == 0:
                                st['ok'] = True
                                res = add_relation([(A, 1), (B, sb), (C, sc)])
                                if res is not None: return ('found', res)
                                break
                        if st['ok']: break
            elif name == 'MSOLVE':
                res = msolve()
                if res is not None: return ('found', res)
        return None

    res = execute(init); it = 0
    while res is None and body:
        ctr[0] = it; res = execute(body); it += 1
        if st['cost'] > cap or st['steps'] > maxsteps: break
    run.last_hits = st['hits']
    if isinstance(res, tuple) and res[0] == 'found' and st['cost'] <= cap: return res[1], st['cost'], st['steps']
    return None, min(st['cost'], cap) if res is None else cap, st['steps']

# ---------- hand programs in the same DSL ----------
def prog_bsgs():
    init = [I('SETC', 0, 0, 0, 1), I('SETC', 3, 0, 16, 1), I('NEG', 3, 3), I('SETC', 2, 1, 0, 1)]
    body = [I('IFLT', 0, 16, 1), I('INS', 1, 0, 20), I('IFLT', 0, 16, 1), I('ADD', 1, 1, 0),
            I('IFGE', 0, 16, 1), I('LOOK', 2, 0, 20), I('IFGE', 0, 16, 1), I('ADD', 2, 2, 3)]
    return (init, body)
def prog_rho_dp(nb=4, dpbits=2, restart_e=20):
    init = [I('SETRAND', 0)]
    body = [I('STEP', 0, 0, nb), I('IFDP', 0, dpbits), I('LOOK', 0, 0, 20), I('IFDP', 0, dpbits), I('INS', 0, 0, 20),
            I('IFMOD', 0, restart_e, 1), I('SETRAND', 0)]
    return (init, body)
def prog_rho_floyd_restart(nb=4, restart_e=20):
    init = [I('SETRAND', 0), I('MOV', 1, 0)]
    body = [I('STEP', 0, 0, nb), I('STEP', 1, 1, nb), I('STEP', 1, 1, nb), I('IFEQX', 0, 1), I('SOLVE', 0, 1),
            I('IFMOD', 0, restart_e, 4), I('SETRAND', 0), I('IFMOD', 0, restart_e, 4), I('MOV', 1, 0)]
    return (init, body)
def prog_ic(fb_e=14, msolve_e=14):
    """Index-calculus-like (2-decomposition via S_3): R=aP+bQ random walk point; for x1 cycling in a factor base
    {1..p^(fb_e/32)} solve S_3(x1,x2,xR)=0 for x2, keep if x2 < bound; record relation R = +-f1 +-f2; MSOLVE when
    enough rows (every iteration where counter hits a multiple; rows < cols+1 makes it a cheap no-op)."""
    init = [I('SETRAND', 0)]
    body = [I('STEP', 0, 0, 4), I('FX', 1, 0), I('FCTR', 0, 0, fb_e), I('LIFT', 1, 0, 0),
            I('IFOK'), I('FS3', 2, 0, 1, 0), I('IFSMALL', 2, fb_e, 1), I('LIFT', 2, 2, 0),
            I('IFOK'), I('RELATE', 0, 1, 2)]
    return (init, body)
def prog_ic_ms(fb_e=14):
    p, b = prog_ic(fb_e); return (p, b + [I('IFMOD', 0, 13, 1), I('MSOLVE')])

BASELINES = {'bsgs': prog_bsgs, 'rho_floyd': prog_rho_floyd_restart, 'rho_dp': prog_rho_dp}

def instances(curve, n, seed):
    rng = random.Random(seed * 7919 + curve['r'])
    return [(rng.randrange(1, curve['r']), rng.randrange(1 << 30)) for _ in range(n)]

if __name__ == '__main__':
    import time
    for tb in (10, 12, 14):
        c = make_curve(tb, 5); print('curve', tb, 'r', c['r'], 'sqrt', round(c['r'] ** .5))
        for nm, f in list(BASELINES.items()) + [('ic', prog_ic), ('ic_ms', prog_ic_ms)]:
            t = time.time(); ok = 0; tot = 0.0
            for k, s in instances(c, 20, 1):
                res, cost, _ = run(f(), c, k, s, 12.0 if not nm.startswith('ic') else 400.0); ok += res == k; tot += cost
            print(' ', nm, ok / 20, round(tot / 20 / c['r'] ** .5, 2), 'sqrt-units', round(time.time() - t, 1), 's')
