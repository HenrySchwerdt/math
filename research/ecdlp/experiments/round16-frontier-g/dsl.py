"""Round 16 / frontier G: tiny DLP instruction set (VM), toy curves, hand baselines.
stdlib only. Points are tracked internally as (a, b, v): the point equals aP + bQ and v = a + b*k mod r
is its hidden discrete log (used ONLY to look up the x-coordinate / verify candidates; programs never read a, b,
v except through SOLVE/LOOK, which are charged). Group-op cost: ADD, DBL cost 1; NEG, MOV, SETO cost 0.
"""
import os, sys, random, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from toyec import Curve, is_prime

# ---------- curves ----------
_CACHE = {}
def make_curve(tb, seed):
    """Prime-order curve with r near 2^tb (within ~+-6%), deterministic in (tb, seed).
    Returns dict(r, p, xt) where xt[i] = x-coordinate of i*P (xt[0] = -1 for infinity)."""
    key = (tb, seed)
    if key in _CACHE: return _CACHE[key]
    rng = random.Random(1000003 * tb + seed)
    lo, hi = int(2 ** tb * 0.94), int(2 ** tb * 1.06)
    while True:
        p = rng.randrange(lo, hi)
        if not is_prime(p) or p < 5: continue
        a, b = rng.randrange(p), rng.randrange(p)
        try: E = Curve(a, b, p)
        except ValueError: continue
        pts = E.points(); r = len(pts)
        if not is_prime(r) or r == p or r < 2 ** (tb - 0.2) or r >= min(2 ** (tb + 0.2), 65537): continue
        P = pts[1 + rng.randrange(r - 1)]
        xt = [-1] * r; R = None
        for i in range(r):
            xt[i] = -1 if R is None else R[0]
            R = E.add(R, P)
        assert R is None  # order r
        c = dict(r=r, p=p, a=E.a, b=E.b, xt=xt, tb=tb, seed=seed)
        _CACHE[key] = c
        return c

# ---------- instruction set ----------
# instr = (op, f1, f2, f3, f4)
OPS = ['SETC', 'ADD', 'DBL', 'NEG', 'MOV', 'SETO', 'SETRAND', 'STEP', 'INS', 'LOOK', 'SOLVE', 'INC', 'ZERO',
       'IFLT', 'IFGE', 'IFMOD', 'IFEQX', 'IFLTX', 'IFDP']
OPI = {n: i for i, n in enumerate(OPS)}
# field ranges (inclusive) per op for f1..f4
RANGES = {
    'SETC': [(0, 3), (0, 1), (0, 32), (1, 4)],     # dst, kind(0=P,1=Q), exponent e/32, multiplier
    'ADD': [(0, 3), (0, 3), (0, 3), (0, 0)], 'DBL': [(0, 3), (0, 3), (0, 0), (0, 0)],
    'NEG': [(0, 3), (0, 3), (0, 0), (0, 0)], 'MOV': [(0, 3), (0, 3), (0, 0), (0, 0)],
    'SETO': [(0, 3), (0, 0), (0, 0), (0, 0)], 'SETRAND': [(0, 3), (0, 0), (0, 0), (0, 0)],
    'STEP': [(0, 3), (0, 3), (1, 4), (0, 0)],       # dst, src, nbits of walk table
    'INS': [(0, 3), (0, 8), (1, 20), (0, 0)], 'LOOK': [(0, 3), (0, 8), (1, 20), (0, 0)],  # reg, shift, keybits
    'SOLVE': [(0, 3), (0, 3), (0, 0), (0, 0)],
    'INC': [(0, 0), (0, 0), (0, 0), (0, 0)], 'ZERO': [(0, 0), (0, 0), (0, 0), (0, 0)],
    'IFLT': [(0, 1), (0, 32), (1, 4), (0, 0)], 'IFGE': [(0, 1), (0, 32), (1, 4), (0, 0)],
    'IFMOD': [(0, 1), (0, 32), (1, 4), (0, 0)],
    'IFEQX': [(0, 3), (0, 3), (0, 0), (0, 0)], 'IFLTX': [(0, 3), (0, 3), (0, 0), (0, 0)],
    'IFDP': [(0, 3), (0, 8), (0, 0), (0, 0)],
}

def I(name, *f):
    f = list(f) + [0] * (4 - len(f))
    return (OPI[name], *f)

def _const(r, e, m):
    return max(1, math.ceil(r ** (e / 32.0) - 1e-9) * m)

def _mulcost(c):
    return max(0, c.bit_length() + bin(c).count('1') - 2)

def run(prog, curve, k, seed, cap_factor=12.0):
    """prog = (init, body). Returns (solved_k or None, cost, steps). Fresh VM per instance."""
    init, body = prog
    r, xt = curve['r'], curve['xt']
    sr = math.isqrt(r) + 1
    cap = cap_factor * math.sqrt(r)
    M = 2 * sr                                   # hash table capacity (entries)
    rng = random.Random(seed)
    lb = r.bit_length()
    verify_cost = math.ceil(1.5 * lb)
    R = [[0, 0, 0] for _ in range(4)]            # (a, b, v)
    ctr = [0, 0]
    table = {}
    W = {}
    st = {'cost': 0.0}
    maxsteps = int(10 * cap) + 100

    def pt(a, b): return [a % r, b % r, (a + b * k) % r]

    def solve(A, B):
        # relation  A = +-B  =>  a1 + b1 k = +-(a2 + b2 k)
        a1, b1, _ = A; a2, b2, _ = B
        if (a1, b1) == (a2, b2): return None
        cands = []
        d = (b1 - b2) % r
        if d: cands.append(((a2 - a1) * pow(d, -1, r)) % r)
        s = (b1 + b2) % r
        if s: cands.append(((-a2 - a1) * pow(s, -1, r)) % r)
        st['hits'] += 1
        for c in cands:
            st['cost'] += verify_cost
            if c % r == k % r: return c
            if st['cost'] > cap: return None
        return None

    def key_of(P, ks, kb): return (xt[P[2]] >> ks) & ((1 << kb) - 1)

    def execute(code, ci):
        """run list of instrs; return (found_k or None). Handles IF-skip. ctr[0] already set."""
        n = len(code); i = 0
        while i < n:
            st['steps'] += 1
            if st['steps'] > maxsteps or st['cost'] > cap: return 'stop'
            op, f1, f2, f3, f4 = code[i]; name = OPS[op]; i += 1
            if name in ('IFLT', 'IFGE', 'IFMOD', 'IFEQX', 'IFLTX', 'IFDP'):
                if name in ('IFLT', 'IFGE', 'IFMOD'):
                    T = _const(r, f2, f3); c = ctr[f1]
                    ok = (c < T) if name == 'IFLT' else (c >= T) if name == 'IFGE' else (c % T == T - 1)
                elif name == 'IFEQX': ok = xt[R[f1][2]] == xt[R[f2][2]]
                elif name == 'IFLTX': ok = xt[R[f1][2]] < xt[R[f2][2]]
                else: ok = (xt[R[f1][2]] & ((1 << f2) - 1)) == 0
                if not ok: i += 1
                continue
            if name == 'SETC':
                c = _const(r, f3, f4); st['cost'] += _mulcost(c)
                R[f1] = pt(c, 0) if f2 == 0 else pt(0, c)
            elif name == 'ADD':
                A, B = R[f2], R[f3]; R[f1] = [(A[0] + B[0]) % r, (A[1] + B[1]) % r, (A[2] + B[2]) % r]; st['cost'] += 1
            elif name == 'DBL':
                A = R[f2]; R[f1] = [(2 * A[0]) % r, (2 * A[1]) % r, (2 * A[2]) % r]; st['cost'] += 1
            elif name == 'NEG':
                A = R[f2]; R[f1] = [(-A[0]) % r, (-A[1]) % r, (-A[2]) % r]
            elif name == 'MOV': R[f1] = list(R[f2])
            elif name == 'SETO': R[f1] = [0, 0, 0]
            elif name == 'SETRAND':
                st['cost'] += 3 * lb; R[f1] = pt(rng.randrange(r), rng.randrange(r))
            elif name == 'STEP':
                nb = f3
                if nb not in W:
                    st['cost'] += 6 * lb + (1 << nb)   # two independent random combos (3*lb each) + 2^nb sums
                    L = [pt(rng.randrange(r), rng.randrange(r)), pt(rng.randrange(r), rng.randrange(r))]
                    for j in range(2, 1 << nb):
                        B = L[rng.randrange(j - 1)]; A = L[-1]
                        L.append([(A[0] + B[0]) % r, (A[1] + B[1]) % r, (A[2] + B[2]) % r])
                    W[nb] = L
                A = R[f2]; B = W[nb][xt[A[2]] & ((1 << nb) - 1)]
                R[f1] = [(A[0] + B[0]) % r, (A[1] + B[1]) % r, (A[2] + B[2]) % r]; st['cost'] += 1
            elif name == 'INS':
                kk = key_of(R[f1], f2, f3)
                if kk not in table and len(table) < M: table[kk] = (R[f1][0], R[f1][1])
            elif name == 'LOOK':
                kk = key_of(R[f1], f2, f3)
                if kk in table:
                    a2, b2 = table[kk]; res = solve(R[f1], [a2, b2, 0])
                    if res is not None: return ('found', res)
            elif name == 'SOLVE':
                if xt[R[f1][2]] == xt[R[f2][2]]:   # SOLVE only acts on an x-collision (programmer-free check)
                    res = solve(R[f1], R[f2])
                    if res is not None: return ('found', res)
            elif name == 'INC': ctr[1] += 1
            elif name == 'ZERO': ctr[1] = 0
        return None

    st['steps'] = 0; st['hits'] = 0
    # registers start at O; P and Q constants are produced by SETC (cost 0 for c=1)
    res = execute(init, 0)
    it = 0
    while res is None and body:
        ctr[0] = it
        res = execute(body, 1)
        it += 1
        if st['cost'] > cap or st['steps'] > maxsteps: break
    if isinstance(res, tuple) and res[0] == 'found' and st['cost'] <= cap:
        run.last_hits = st['hits']
        return res[1], st['cost'], st['steps']
    run.last_hits = st['hits']
    return None, min(st['cost'], cap) if res is None else cap, st['steps']

# ---------- hand baselines expressed in the DSL ----------
def prog_bsgs():
    init = [I('SETC', 0, 0, 0, 1), I('SETC', 3, 0, 16, 1), I('NEG', 3, 3), I('SETC', 2, 1, 0, 1)]
    body = [I('IFLT', 0, 16, 1), I('INS', 1, 0, 20), I('IFLT', 0, 16, 1), I('ADD', 1, 1, 0),
            I('IFGE', 0, 16, 1), I('LOOK', 2, 0, 20), I('IFGE', 0, 16, 1), I('ADD', 2, 2, 3)]
    return (init, body)

def prog_rho_floyd(nb=3, restart_e=20):
    init = [I('SETRAND', 0), I('MOV', 1, 0)]
    body = [I('STEP', 0, 0, nb), I('STEP', 1, 1, nb), I('STEP', 1, 1, nb), I('IFEQX', 0, 1), I('SOLVE', 0, 1)]
    return (init, body)

def prog_rho_floyd_restart(nb=4, restart_e=20):
    init = [I('SETRAND', 0), I('MOV', 1, 0)]
    body = [I('STEP', 0, 0, nb), I('STEP', 1, 1, nb), I('STEP', 1, 1, nb), I('IFEQX', 0, 1), I('SOLVE', 0, 1),
            I('IFMOD', 0, restart_e, 4), I('SETRAND', 0), I('IFMOD', 0, restart_e, 4), I('MOV', 1, 0)]
    return (init, body)

def prog_rho_dp(nb=4, dpbits=2, restart_e=20):
    init = [I('SETRAND', 0)]
    body = [I('STEP', 0, 0, nb), I('IFDP', 0, dpbits), I('LOOK', 0, 0, 20), I('IFDP', 0, dpbits), I('INS', 0, 0, 20),
            I('IFMOD', 0, restart_e, 1), I('SETRAND', 0)]
    return (init, body)

def prog_brute():
    init = [I('SETC', 0, 0, 0, 1), I('SETC', 2, 1, 0, 1)]
    body = [I('ADD', 1, 1, 0), I('IFEQX', 1, 2), I('SOLVE', 1, 2)]
    return (init, body)

BASELINES = {'bsgs': prog_bsgs, 'rho_floyd': prog_rho_floyd_restart, 'rho_dp': prog_rho_dp, 'brute': prog_brute}

def instances(curve, n, seed):
    rng = random.Random(seed * 7919 + curve['r'])
    return [(rng.randrange(1, curve['r']), rng.randrange(1 << 30)) for _ in range(n)]

def mean_cost(prog, curve, n, seed):
    ok = 0; tot = 0.0
    for k, s in instances(curve, n, seed):
        res, cost, _ = run(prog, curve, k, s)
        ok += res == k; tot += cost
    return ok / n, tot / n

if __name__ == '__main__':
    for tb in (10, 12):
        c = make_curve(tb, 100)
        print('curve', tb, 'r', c['r'], 'p', c['p'], 'sqrt', c['r'] ** .5)
        for nm, f in BASELINES.items():
            print(' ', nm, mean_cost(f(), c, 30, 1))
