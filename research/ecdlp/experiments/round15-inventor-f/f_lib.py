"""Round 15 inventor F: m=3 (S_4) relation machinery. Reuses round13 d2lib (imported, not edited) for primes, sqrt, BSGS order, LA."""
import sys, os, random, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'round13-inventor-d'))
from d2lib import is_prime, sqrt_mod, order_bsgs, vinv, LA
from toyec import Curve

# ---------------- instance generation (prime order r, d | p-1 with d ~ c p^{1/3}) ----------------
def gen_instance(bits, seed, cfac=1.6):
    rng = random.Random(15000 * bits + seed)
    d = 2 * round(cfac * 2 ** (bits / 3.0) / 2)
    while True:
        c = rng.randrange(max(1, int(0.75 * 2 ** bits) // d), (2 ** bits) // d + 1)
        p = c * d + 1
        if not (0.75 * 2 ** bits < p < 2 ** bits and is_prime(p)): continue
        for _ in range(300):
            a, b = rng.randrange(p), rng.randrange(p)
            if (4 * a ** 3 + 27 * b * b) % p == 0: continue
            E = Curve(a, b, p)
            while True:
                x = rng.randrange(p); y = sqrt_mod(x ** 3 + a * x + b, p)
                if y: break
            Ms = [M for M in order_bsgs(E, (x, y), p) if is_prime(M)]
            if len(Ms) == 1:
                r = Ms[0]; P = (x, y); assert E.mul(r, P) is None
                k = rng.randrange(1, r)
                return dict(bits=bits, seed=seed, p=p, a=a, b=b, r=r, d=d, P=P, k=k, Q=E.mul(k, P))

# ---------------- factor bases (x-sets; y chosen by sqrt) ----------------
def with_points(p, a, b, xs):
    V = {}
    for x in xs:
        x = int(x) % p; v = (x ** 3 + a * x + b) % p
        if v == 0 or x in V: continue
        y = sqrt_mod(v, p)
        if y: V[x] = y
    return V

def base_coset(p, a, b, d, rng):
    # g * mu_d, zeta of exact order d (d | p-1, any d)
    fac = [q for q in range(2, d + 1) if d % q == 0 and is_prime(q)]
    while True:
        zeta = pow(rng.randrange(2, p), (p - 1) // d, p)
        if all(pow(zeta, d // q, p) != 1 for q in fac): break
    g = rng.randrange(1, p); xs = []; x = g
    for _ in range(d): xs.append(x); x = x * zeta % p
    return with_points(p, a, b, xs)

def base_random(p, a, b, s, rng):
    V = {}
    while len(V) < s:
        x = rng.randrange(p); v = (x ** 3 + a * x + b) % p
        if v and x not in V:
            y = sqrt_mod(v, p)
            if y: V[x] = y
    return V

def base_smallx(p, a, b, s):
    V = {}; x = 0
    while len(V) < s:
        v = (x ** 3 + a * x + b) % p
        if v and pow(v, (p - 1) // 2, p) == 1: V[x] = sqrt_mod(v, p)
        x += 1
    return V

def base_phi(p, a, b, s, deg, rng):
    """x = phi(t), t = 0,1,2,... (interval), phi random monic degree-deg polynomial: image of a low-degree map on a short interval."""
    co = [rng.randrange(p) for _ in range(deg)]
    def phi(t):
        v = pow(t, deg, p)
        for i, c in enumerate(co): v += c * pow(t, i, p)
        return v % p
    V = {}; t = 0
    while len(V) < s and t < 20 * s + 100:
        for x in [phi(t)]:
            v = (x ** 3 + a * x + b) % p
            if v and x not in V:
                y = sqrt_mod(v, p)
                if y: V[x] = y
        t += 1
    return V

def base_phi_power(p, a, b, s, e, rng):
    """x = g*t^e for t = 1..: image of the monomial map on a short interval (not a subgroup)."""
    g = rng.randrange(1, p); V = {}; t = 1
    while len(V) < s and t < 20 * s + 100:
        x = g * pow(t, e, p) % p; v = (x ** 3 + a * x + b) % p
        if v and x not in V:
            y = sqrt_mod(v, p)
            if y: V[x] = y
        t += 1
    return V

# ---------------- vectorised x-only / affine arithmetic ----------------
def arrays(V):
    xs = np.array(sorted(V), dtype=np.int64); ys = np.array([V[int(x)] for x in xs], dtype=np.int64)
    return xs, ys

def pair_table(p, a, xs, ys):
    """x(Pi + s*Pj) for all i<=j, s in {+1,-1} (i==j: only the doubling, s=+1). Returns (z, I, J, S). Paired additions charged 1 each."""
    s = len(xs); I, J = np.triu_indices(s, 1)
    dx = (xs[J] - xs[I]) % p; inv = vinv(dx, p)
    zs, Is, Js, Ss = [], [], [], []
    for sg in (1, -1):
        lam = ((sg * ys[J] - ys[I]) % p) * inv % p
        zs.append((lam * lam - xs[I] - xs[J]) % p); Is.append(I); Js.append(J); Ss.append(np.full(len(I), sg, dtype=np.int8))
    lam = (3 * xs * xs + a) % p * vinv(2 * ys % p, p) % p
    zs.append((lam * lam - 2 * xs) % p); Is.append(np.arange(s)); Js.append(np.arange(s)); Ss.append(np.ones(s, dtype=np.int8))
    adds = len(I) + s
    return np.concatenate(zs), np.concatenate(Is), np.concatenate(Js), np.concatenate(Ss), adds

def closed_quadruples(p, a, xs, ys):
    """Count unordered closed quadruples sum eps_i u_i = 0 with 4 DISTINCT base points, via collisions of disjoint pair-sums.
    Each relation (sign pattern up to global sign) gives exactly 3 disjoint collisions (one per split of {1,2,3,4}) -> N4 = coll/3."""
    z, I, J, S, adds = pair_table(p, a, xs, ys)
    keep = I != J  # drop doublings (relations with repeated points are lower order)
    z, I, J = z[keep], I[keep], J[keep]
    o = np.argsort(z, kind='stable'); z, I, J = z[o], I[o], J[o]
    eq = np.nonzero(z[1:] == z[:-1])[0]
    coll = 0
    if len(eq):
        # group runs
        starts = np.unique(np.concatenate([eq]))
        i = 0; n = len(eq)
        runs = []; cur = [eq[0]]
        for e in eq[1:]:
            if e == cur[-1] + 1: cur.append(e)
            else: runs.append(cur); cur = [e]
        runs.append(cur)
        for run in runs:
            idx = list(range(run[0], run[-1] + 2))
            for u in range(len(idx)):
                for v in range(u + 1, len(idx)):
                    a1, b1, a2, b2 = I[idx[u]], J[idx[u]], I[idx[v]], J[idx[v]]
                    if len({a1, b1, a2, b2}) == 4: coll += 1
    return coll, adds

# ---------------- m=3 target finder (2+1 split, hashing) ----------------
class Finder3:
    def __init__(self, inst, V):
        self.p, self.a = inst['p'], inst['a']; self.E = Curve(inst['a'], inst['b'], inst['p'])
        self.xs, self.ys = arrays(V); self.s = len(self.xs); p = self.p
        z, I, J, S, self.build_adds = pair_table(p, self.a, self.xs, self.ys)
        o = np.argsort(z, kind='stable'); self.z, self.I, self.J, self.S = z[o], I[o], J[o], S[o]
        self.adds = 0; self.targets = 0
    def decompose(self, T):
        """All (c, e1, i, e2, j, e3) ... returned as list of coefficient dicts {col: coeff} with T = sum coeff*u_col. Cost: s paired additions."""
        p = self.p; tx, ty = T; xs, ys = self.xs, self.ys; self.adds += self.s; self.targets += 1
        same = xs == tx
        dx = (xs - tx) % p; dx[same] = 1; inv = vinv(dx, p)
        out = []
        for sg in (1, -1):                           # W = T - sg*u_i
            lam = ((-sg * ys - ty) % p) * inv % p
            x3 = (lam * lam - xs - tx) % p
            y3 = (lam * ((tx - x3) % p) - ty) % p
            lo = np.searchsorted(self.z, x3, 'left'); hi = np.searchsorted(self.z, x3, 'right')
            for i in np.nonzero((hi > lo) & ~same)[0]:
                for t in range(lo[i], hi[i]):
                    ci, cj, sj = int(self.I[t]), int(self.J[t]), int(self.S[t])
                    # pair point Z = u_ci + sj*u_cj (as affine point), W = +-Z
                    Z = self.E.add((int(xs[ci]), int(ys[ci])), (int(xs[cj]), int(sj * ys[cj] % p)) if True else None)
                    Wp = (int(x3[i]), int(y3[i]))
                    eps = 1 if Z == Wp else (-1 if Z == self.E.neg(Wp) else 0)
                    if eps == 0: continue
                    # T = W + sg*u_i = eps*(u_ci + sj u_cj) + sg u_i
                    co = {}
                    for col, c in ((ci, eps), (cj, eps * sj), (int(i), sg)):
                        co[col] = co.get(col, 0) + c
                    out.append(co)
        return out

def solve_k(inst, V, seed, max_targets=10 ** 6):
    """Full m=3 index-calculus: hash finder + incremental elimination mod r. Returns dict of counts."""
    rng = random.Random(seed * 7919 + inst['bits'])
    p, r, a = inst['p'], inst['r'], inst['a']; E = Curve(a, inst['b'], p)
    F = Finder3(inst, V); s = F.s; la = LA(s, r)
    P, Q = inst['P'], inst['Q']
    # target generation by a branching walk (1 addition per new target), as in round 13
    steps = [(rng.randrange(1, r), rng.randrange(1, r)) for _ in range(32)]
    stpts = [E.add(E.mul(u, P), E.mul(v, Q)) for u, v in steps]
    aa, bb = rng.randrange(1, r), rng.randrange(1, r); T = E.add(E.mul(aa, P), E.mul(bb, Q))
    nrel = 0; gen_adds = 0; tries = 0; seen = set()
    while la.k is None and tries < max_targets:
        tries += 1
        if T is None: aa, bb = rng.randrange(1, r), rng.randrange(1, r); T = E.add(E.mul(aa, P), E.mul(bb, Q)); continue
        for co in F.decompose(T):
            key = frozenset(co.items())
            if key in seen: continue
            seen.add(key)
            row = np.zeros(s + 2, dtype=np.int64)
            for col, c in co.items(): row[col] = c % r      # sum c_i l_i - b k = a
            row[s] = (-bb) % r; row[s + 1] = aa % r
            nrel += 1; la.add(row)
            if la.k is not None: break
        j = int(T[0]) % 32 if T is not None else 0
        T = E.add(T, stpts[j]); aa = (aa + steps[j][0]) % r; bb = (bb + steps[j][1]) % r; gen_adds += 1
    k = la.k
    return dict(k=k, ok=(k is not None and E.mul(k, P) == Q), s=s, targets=F.targets, relations=nrel,
                build_adds=F.build_adds, finder_adds=F.adds, gen_adds=gen_adds, la_mults=la.mults)
