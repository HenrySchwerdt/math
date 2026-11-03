"""Round 13 inventor D: instance generation (BSGS point counting up to 28 bits), factor bases, algebraic m=2 finder, LA."""
import sys, os, random, math, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
sys.path.insert(0, os.path.join(HERE, '..', 'round12-inventor-a'))
from toyec import Curve
from math import isqrt

def is_prime(n):
    if n < 2: return False
    for q in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % q == 0: return n == q
    d, s = n-1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2,3,5,7,11,13,17,19,23,29,31,37):
        x = pow(a, d, n)
        if x in (1, n-1): continue
        for _ in range(s-1):
            x = x*x % n
            if x == n-1: break
        else: return False
    return True

def sqrt_mod(v, p):
    v %= p
    if v == 0: return 0
    if pow(v, (p-1)//2, p) != 1: return None
    if p % 4 == 3: return pow(v, (p+1)//4, p)
    q, e = p-1, 0
    while q % 2 == 0: q //= 2; e += 1
    z = 2
    while pow(z, (p-1)//2, p) != p-1: z += 1
    c, x, t, m = pow(z, q, p), pow(v, (q+1)//2, p), pow(v, q, p), e
    while t != 1:
        i, tt = 0, t
        while tt != 1: tt = tt*tt % p; i += 1
        b = pow(c, 1 << (m-i-1), p)
        x, c = x*b % p, b*b % p
        t, m = t*c % p, i
    return x

def order_bsgs(E, P, p):
    """Return all M in Hasse interval with M*P = O (BSGS over t, #E = p+1-t)."""
    w = 2*isqrt(p)+2
    m = isqrt(2*w)+1
    tab = {}
    R = None
    for j in range(0, m+1):
        tab.setdefault(R, []).append(j)
        if R is not None:
            tab.setdefault(E.neg(R), []).append(-j)
        R = E.add(R, P)
    U = E.mul(p+1, P)
    step = E.mul(2*m+1, P)
    out = []
    # need U - i*step = j*P with t = i(2m+1)+j  (since U = tP)
    i0 = -(w//(2*m+1)) - 2
    cur = E.add(U, E.mul(-i0, step)) if False else None
    G = E.add(U, E.neg(E.mul(i0, step) if i0 >= 0 else E.neg(E.mul(-i0, step))))
    for i in range(i0, -i0+1):
        for j in tab.get(G, []):
            t = i*(2*m+1)+j
            if abs(t) <= w: out.append(p+1-t)
        G = E.add(G, E.neg(step))
    return out

def gen_prime(rng, b, n):
    while True:
        c = rng.randrange(max(1, int(0.75*2**b) >> n), (2**b >> n) + 1)
        p = (c << n) + 1
        if 0.75*2**b < p < 2**b and is_prime(p): return p

def gen_instance(bits, seed, gidx):
    rng = random.Random(1000*bits + seed + 7*gidx)
    n = round(bits / (2.0 if gidx == 0 else 3.0))
    while True:
        p = gen_prime(rng, bits, n)
        for _ in range(400):
            a, c = rng.randrange(p), rng.randrange(p)
            if (4*a**3+27*c*c) % p == 0: continue
            E = Curve(a, c, p)
            while True:
                x = rng.randrange(p); y = sqrt_mod(x**3+a*x+c, p)
                if y: break
            P = (x, y)
            if E.mul(p+1-0, P) is None and False: pass
            Ms = [M for M in order_bsgs(E, P, p) if is_prime(M)]
            if len(Ms) == 1:
                r = Ms[0]
                assert E.mul(r, P) is None
                k = rng.randrange(1, r)
                return dict(bits=bits, seed=seed, gidx=gidx, p=p, a=a, b=c, r=r, n=n, d=1 << n, P=P, k=k, Q=E.mul(k, P))

# ---------- factor bases ----------
def fb_coset(inst, rng):
    p, a, b, n = inst['p'], inst['a'], inst['b'], inst['n']
    d = 1 << n
    while True:
        z = rng.randrange(2, p)
        zeta = pow(z, (p-1) >> n, p)
        if pow(zeta, d >> 1, p) != 1: break
    g = rng.randrange(1, p)
    xs, x = [], g
    for _ in range(d):
        xs.append(x); x = x*zeta % p
    return xs

def fb_smallx(inst, size):
    p, a, b = inst['p'], inst['a'], inst['b']
    xs, x = [], 0
    while len(xs) < size:
        if pow((x**3+a*x+b) % p, (p-1)//2, p) == 1: xs.append(x)
        x += 1
    return xs

def build_V(inst, xs):
    """Keep x with a point; choose one y each. Returns dict x->y (stored sign) ; mults charged ~ 2 log2 p each."""
    p, a, b = inst['p'], inst['a'], inst['b']
    V = {}
    for x in xs:
        v = (x**3+a*x+b) % p
        if v == 0: continue
        y = sqrt_mod(v, p)
        if y: V[x] = y
    return V

# ---------- vectorised arithmetic ----------
def vinv(x, p):
    r = np.ones_like(x); b = x.copy(); e = p-2
    while e:
        if e & 1: r = r*b % p
        b = b*b % p; e >>= 1
    return r

class Finder:
    def __init__(self, inst, V):
        self.p = inst['p']; self.E = Curve(inst['a'], inst['b'], inst['p'])
        self.keys = sorted(V); self.idx = {x: i for i, x in enumerate(self.keys)}
        self.vy = {x: V[x] for x in self.keys}
        xs = np.array(self.keys, dtype=np.int64); ys = np.array([V[x] for x in self.keys], dtype=np.int64)
        self.sorted_x = xs
        self.X = np.concatenate([xs, xs]); self.Y = np.concatenate([ys, (-ys) % self.p])
        self.sign = np.concatenate([np.ones(len(xs), dtype=np.int64), -np.ones(len(xs), dtype=np.int64)])
        self.col = np.concatenate([np.arange(len(xs)), np.arange(len(xs))])
        self.adds = 0
    def decompositions(self, T):
        """All (col1,s1,col2,s2) with T = s1*u_col1 + s2*u_col2 (u_col stored-sign point), found by additions T+v, v in signed V.
        T = W - v  where W = T+v... we test W=T+v in V:  T = W + (-v). Cost: |V_signed| additions (counted)."""
        p = self.p; tx, ty = T
        n = len(self.X); self.adds += n
        out = []
        same = self.X == tx
        dx = (self.X - tx) % p
        dx[same] = 1
        lam = (self.Y - ty) % p * vinv(dx, p) % p
        x3 = (lam*lam - self.X - tx) % p
        y3 = (lam*((self.X - x3) % p) - self.Y) % p     # W = T + v
        pos = np.searchsorted(self.sorted_x, x3)
        pos[pos >= len(self.sorted_x)] = 0
        hit = (self.sorted_x[pos] == x3) & (~same)
        for i in np.nonzero(hit)[0]:
            c = int(pos[i]); x = int(x3[i])
            sW = 1 if int(y3[i]) == self.vy[x] else -1     # W = sW*u_c
            # T = W - v = sW*u_c - sign_i*u_{col_i}
            out.append((c, sW, int(self.col[i]), -int(self.sign[i])))
        for i in np.nonzero(same)[0]:                      # T = +-v : one-term relation
            sT = 1 if int(self.Y[i]) == ty else -1
            out.append((int(self.col[i]), int(self.sign[i]) * sT, None, 0))
        return out

# ---------- linear algebra: incremental sparse-aware elimination mod r ----------
class LA:
    def __init__(self, ncols, r):
        self.s, self.r = ncols, r          # columns 0..s-1 = logs, column s = k, column s+1 = rhs
        self.piv = {}; self.mults = 0; self.k = None
    def add(self, row):
        r, s = self.r, self.s
        while True:
            nz = np.nonzero(row[:s+1])[0]
            if len(nz) == 0: return
            c = int(nz[0])
            if c in self.piv:
                pr = self.piv[c]; f = int(row[c])
                row = (row - f*pr) % r; self.mults += int(np.count_nonzero(pr))
            else:
                inv = pow(int(row[c]), -1, r); row = row*inv % r; self.mults += int(np.count_nonzero(row))
                self.piv[c] = row
                if c == s: self.k = int(row[s+1])
                return

def run_pipeline(inst, kind, seed, max_targets=None):
    rng = random.Random(seed*99991 + inst['bits'])
    p, r, a, b = inst['p'], inst['r'], inst['a'], inst['b']
    t0 = time.time()
    xs = fb_coset(inst, rng)
    V = build_V(inst, xs)
    if kind != 'coset': xs = fb_smallx(inst, len(V)); V = build_V(inst, xs)
    s = len(V)
    fb_mults = len(xs) * 2 * int(math.log2(p) + 1)
    F = Finder(inst, V)
    E = F.E
    # target walk: T_{i+1} = T_i + W_j, W_j = a_j P + b_j Q (32 entries), coefficients tracked
    adds_tg = 0
    W = []
    for _ in range(32):
        aj, bj = rng.randrange(1, r), rng.randrange(1, r)
        W.append((E.add(E.mul(aj, inst['P']), E.mul(bj, inst['Q'])), aj, bj)); adds_tg += 2*inst['r'].bit_length()*3//2
    ta, tb = rng.randrange(1, r), rng.randrange(1, r)
    T = E.add(E.mul(ta, inst['P']), E.mul(tb, inst['Q'])); adds_tg += 2*int(inst['r'].bit_length()*1.5)
    la = LA(s, r)
    targets = relations = hits_targets = 0
    ok = False; kout = None
    cap = max_targets or 10**9
    while targets < cap:
        targets += 1
        if T is not None:
            decs = F.decompositions(T)
            if decs: hits_targets += 1
            for (c1, s1, c2, s2) in decs:
                row = np.zeros(s+2, dtype=np.int64)
                row[c1] = (row[c1] + s1) % r
                if c2 is not None: row[c2] = (row[c2] + s2) % r
                row[s] = (-tb) % r       # s1 l1 + s2 l2 - tb k = ta
                row[s+1] = ta % r
                relations += 1
                la.add(row)
            if la.k is not None:
                kout = la.k; ok = (E.mul(kout, inst['P']) == inst['Q']); break
        j = rng.randrange(32); T = E.add(T, W[j][0]); ta = (ta + W[j][1]) % r; tb = (tb + W[j][2]) % r; adds_tg += 1
    return dict(bits=inst['bits'], seed=inst['seed'], kind=kind, p=p, r=r, d=inst['d'], s=s, targets=targets, hit_targets=hits_targets,
                relations=relations, ok=bool(ok), adds_finder=F.adds, adds_target=adds_tg, fb_mults=fb_mults, la_mults=la.mults,
                pi_hat=hits_targets/max(1, targets), wall=time.time()-t0)

def per_relation(inst, kind, seed, ntarget):
    """Finder cost only (no LA): sample ntarget random targets."""
    rng = random.Random(seed*7919 + inst['bits'])
    p, r = inst['p'], inst['r']
    xs = fb_coset(inst, rng)
    V = build_V(inst, xs)
    if kind != 'coset': xs = fb_smallx(inst, len(V)); V = build_V(inst, xs)
    F = Finder(inst, V); E = F.E
    rel = hit = 0; t0 = time.time()
    for _ in range(ntarget):
        T = E.mul(rng.randrange(1, r), inst['P'])
        dec = F.decompositions(T)
        hit += bool(dec); rel += len(dec)
        for (c1, s1, c2, s2) in dec[:3]:   # correctness spot-check
            def pt(c, sg):
                x = F.keys[c]; y = F.vy[x]; return (x, y if sg == 1 else (-y) % p)
            Sx = E.add(pt(c1, 1) if s1 == 1 else E.neg(pt(c1, 1)), (None if c2 is None else (pt(c2, 1) if s2 == 1 else E.neg(pt(c2, 1)))))
            assert Sx == T, 'decomposition check failed'
    return dict(bits=inst['bits'], seed=inst['seed'], kind=kind, p=p, r=r, d=inst['d'], s=len(V), targets=ntarget, hit_targets=hit, relations=rel,
                adds_finder=F.adds, wall=time.time()-t0)
