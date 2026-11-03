"""Candidate algorithms. All return (k, group_ops, info) and take counted-op `ops` (Ops).
Instance: curve (p,a), base P (order n prime), target Q = kP.
"""
import random
from lib12 import Ops, R_PARTS, dp_mask_for

def _steps(ops, P, Q, n, rng, withQ=True):
    S = []
    for _ in range(R_PARTS):
        a = rng.randrange(1, n); b = rng.randrange(1, n) if withQ else 0
        pt = ops.mul(a, P)
        if withQ: pt = ops.add(pt, ops.mul(b, Q))
        S.append((pt, a, b))
    return S

# ---------------------------------------------------------------- reference: Pollard rho (DP, r-adding)
def rho_ref(ops, P, Q, n, rng, L, maxfac=20):
    p = ops.p
    S = _steps(ops, P, Q, n, rng)
    mask, table, wid = dp_mask_for(L), {}, 0
    cap = maxfac * (mask+1)
    while True:
        wid += 1
        a0, b0 = rng.randrange(n), rng.randrange(n)
        R = ops.add(ops.mul(a0, P), ops.mul(b0, Q)); a, b = a0, b0
        for _ in range(cap):
            if R is None: break
            x = R[0]
            if (x & mask) == 0:
                prev = table.get(x)
                if prev is None: table[x] = (a, b, wid)
                elif prev[2] != wid and prev[1] != b:
                    return (prev[0]-a) * pow(b-prev[1], -1, n) % n, ops.count, len(table)
                break
            pt, da, db = S[x % R_PARTS]
            if pt[0] == x: R = None; break
            R = ops.add(R, pt); a = (a+da) % n; b = (b+db) % n

# ---------------------------------------------------------------- C1: negation-class rho with cycle escape
def rho_neg(ops, P, Q, n, rng, L, maxfac=20):
    p, half = ops.p, ops.p >> 1
    S = _steps(ops, P, Q, n, rng)
    mask, table, wid = dp_mask_for(L), {}, 0
    cap = maxfac * (mask+1)
    stats = {'cycle2': 0, 'cycle4': 0, 'capped': 0}
    def canon(R, a, b):
        if R[1] > half: return (R[0], p - R[1]), (-a) % n, (-b) % n
        return R, a, b
    while True:
        wid += 1
        a0, b0 = rng.randrange(n), rng.randrange(n)
        R = ops.add(ops.mul(a0, P), ops.mul(b0, Q))
        if R is None: continue
        R, a, b = canon(R, a0, b0)
        hist = []   # last points (R,a,b)
        for it in range(cap):
            x = R[0]
            if (x & mask) == 0:
                prev = table.get(x)
                if prev is None: table[x] = (a, b, wid)
                elif prev[2] != wid and prev[1] != b:
                    return (prev[0]-a) * pow(b-prev[1], -1, n) % n, ops.count, (len(table), stats)
                break
            pt, da, db = S[x % R_PARTS]
            if pt[0] == x: break
            hist.append((R, a, b))
            if len(hist) > 4: hist.pop(0)
            R = ops.add(R, pt); a = (a+da) % n; b = (b+db) % n
            R, a, b = canon(R, a, b)
            # fruitless-cycle detection (period 2 and 4 in classes)
            cyc = None
            if len(hist) >= 2 and hist[-2][0][0] == R[0]: cyc = [(R, a, b), hist[-1]]; stats['cycle2'] += 1
            elif len(hist) >= 4 and hist[-4][0][0] == R[0]: cyc = [(R, a, b)] + hist[-1:-4:-1]; stats['cycle4'] += 1
            if cyc is not None:
                (M, ma, mb) = min(cyc, key=lambda t: t[0][0])
                R = ops.add(M, M); a, b = (2*ma) % n, (2*mb) % n
                if R is None: break
                R, a, b = canon(R, a, b); hist = []
        else:
            stats['capped'] += 1

# ---------------------------------------------------------------- C2: preprocessed fixed-walk table (S,T tradeoff)
class PreTable:
    """Point-only walk f (no dependence on Q); table of DPs reached from m chains started at s_i P."""
    def __init__(self, ops, P, n, rng, m, L, maxfac=20):
        self.ops, self.P, self.n, self.L = ops, P, n, L
        self.S = _steps(ops, P, None, n, rng, withQ=False)
        self.mask = dp_mask_for(L); self.cap = maxfac*(self.mask+1)
        self.table, self.chains = {}, 0
        c0 = ops.count
        for _ in range(m):
            s = rng.randrange(1, n)
            R = ops.mul(s, P); a = s
            r = self.walk_to_dp(R, a)
            self.chains += 1
            if r is not None: self.table.setdefault(r[0][0], r[1])
        self.pre_ops = ops.count - c0
    def walk_to_dp(self, R, a):
        ops, n, mask, S = self.ops, self.n, self.mask, self.S
        for _ in range(self.cap):
            if R is None: return None
            x = R[0]
            if (x & mask) == 0: return R, a
            pt, da, _ = S[x % R_PARTS]
            if pt[0] == x: return None
            R = ops.add(R, pt); a = (a+da) % n
        return None
    def query(self, Q, rng, max_restarts=10**6):
        """returns (k, online_ops, restarts)."""
        ops, n, T = self.ops, self.n, self.table
        c0 = ops.count
        R0 = Q; t = 0
        R0 = ops.add(Q, self.P)  # start t=1: Q + 1*P
        while True:
            t += 1
            r = self.walk_to_dp(R0, t)
            if r is not None and r[0][0] in T:
                return (T[r[0][0]] - r[1]) % n, ops.count - c0, t
            R0 = ops.add(R0, self.P)   # next start Q + (t+1)P  (1 op)
            if t > max_restarts: return None, ops.count - c0, t

# ---------------------------------------------------------------- C3: multi-instance batch, shared DP, union-find with potentials
def batch_rho(ops, P, Qs, n, rng, L, maxfac=20):
    """Solve all Q_j = k_j P. Nodes 0..M ; node 0 is the base P (k_0=0). Walk from Q_j + cP (j may be 0 -> cP).
    Collision between nodes j!=j' : k_j + c = k_j' + c' => k_j' - k_j = c - c'. Union-find with offsets:
    off[v] = k_v - k_root(v) (mod n)."""
    M = len(Qs)
    pts = [None] + list(Qs)            # node 0 = identity => walk from cP
    S = _steps(ops, P, None, n, rng, withQ=False)
    mask, table, wid = dp_mask_for(L), {}, 0
    cap = maxfac*(mask+1)
    parent, off = list(range(M+1)), [0]*(M+1)
    def find(v):
        path = []
        while parent[v] != v: path.append(v); v = parent[v]
        root = v
        # compress with offsets
        acc = 0
        for u in reversed(path):
            acc = (acc + off[u]) % n
            parent[u] = root; off[u] = acc
        return root
    # off[u] = k_u - k_parent(u); after compression off[u]=k_u-k_root. Recompute properly:
    def find2(v):
        if parent[v] == v: return v, 0
        chain = []
        u = v
        while parent[u] != u: chain.append(u); u = parent[u]
        root = u
        # walk from the top of chain down accumulating
        acc = 0
        for w in reversed(chain):
            acc = (acc + off[w]) % n
            off[w] = acc; parent[w] = root
        return root, off[v] if v != root else 0
    comps = M + 1
    unresolved_target = lambda: find2(0)[0]
    def solved():
        r0 = find2(0)[0]
        return all(find2(j)[0] == r0 for j in range(1, M+1))
    def union(u, v, d):
        """k_v - k_u = d"""
        ru, ou = find2(u); rv, ov = find2(v)
        if ru == rv: return False
        # k_u = k_ru + ou ; k_v = k_rv + ov ; k_rv - k_ru = d + ou - ov
        parent[rv] = ru; off[rv] = (d + ou - ov) % n
        return True
    # choose instance for next walk: uniformly among nodes whose component != component of node 0 plus node 0
    rounds = 0
    check_every = 8
    while True:
        wid += 1
        r0 = find2(0)[0]
        cand = [j for j in range(M+1) if find2(j)[0] != r0] 
        j = rng.choice(cand + [0]) if cand else 0
        c0 = rng.randrange(n)
        base = pts[j]
        R = ops.mul(c0, P) if base is None else ops.add(base, ops.mul(c0, P))
        c = c0
        for _ in range(cap):
            if R is None: break
            x = R[0]
            if (x & mask) == 0:
                prev = table.get(x)
                if prev is None: table[x] = (j, c, wid)
                elif prev[2] != wid:
                    pj, pc, _ = prev
                    if pj != j:
                        # k_pj + pc = k_j + c  -> k_j - k_pj = pc - c
                        union(pj, j, (pc - c) % n)
                    # (pj==j: same instance; carries no information)
                break
            pt, da, _ = S[x % R_PARTS]
            if pt[0] == x: R = None; break
            R = ops.add(R, pt); c = (c+da) % n
        if wid % check_every == 0 and solved() :
            r0, _ = find2(0)
            ks = [(off[j] if j else 0) for j in range(M+1)]
            # off[j] = k_j - k_root; root may not be 0 -> normalise by k_0 = 0
            r = find2(0)
            res = []
            for j in range(1, M+1):
                rj, oj = find2(j)
                _, o0 = find2(0)
                res.append((oj - o0) % n)
            return res, ops.count, len(table)
