"""RUN-3386b45f toy checks (stdlib, seeded, < 2 min).
C1: pair (first-difference) norm polynomial M of Theorem P: cleared formula == direct product,
    deg M <= 4d, M != 0, M(x_k)=0 when k,k+j in A for an interpolating (f,h).
C2: computation trees with equality tests: nodes leaving the generic path lie in the root sets of
    the tested numerators; |Bad| <= 2^(L+1)-1; generic-leaf output = k on followers.
Usage: python3 dtree_check.py   (prints a summary; exit code 1 on any failed assertion)"""
import os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from toyec import Curve, is_prime

# ---------- poly arithmetic mod p, coefficient lists low->high ----------
def trim(a):
    while a and a[-1] == 0: a.pop()
    return a
def padd(a, b, p):
    n = max(len(a), len(b)); return trim([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p for i in range(n)])
def psub(a, b, p):
    n = max(len(a), len(b)); return trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p for i in range(n)])
def pmul(a, b, p):
    if not a or not b: return []
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b): r[i + j] = (r[i + j] + x * y) % p
    return trim(r)
def ppow(a, n, p):
    r = [1]
    for _ in range(n): r = pmul(r, a, p)
    return r
def pscal(a, c, p): return trim([x * c % p for x in a])
def peval(a, x, p):
    r = 0
    for c in reversed(a): r = (r * x + c) % p
    return r
def deg(a): return len(a) - 1 if a else -1

def setup(seed, p, Nmax):
    rng = random.Random(seed)
    while True:
        a, b = rng.randrange(p), rng.randrange(p)
        try: E = Curve(a, b, p)
        except ValueError: continue
        n = E.order()
        for r in range(n, 2 * Nmax + 2, -1):
            if n % r == 0 and is_prime(r):
                cof = n // r
                for _ in range(40):
                    pts = E.points(); Q = rng.choice(pts)
                    P = E.mul(cof, Q)
                    if P is not None and E.mul(r, P) is None: return E, P, r, rng
                break

def xk(E, P, k): return E.mul(k, P)[0]

def pair_M(E, x0, f, h, j, d):
    p, a, b = E.p, E.a, E.b
    # S(u)=2((x0 u + a)(u + x0) + 2b), T(u)=(x0 u - a)^2 - 4b(u+x0), D=(u-x0)^2
    S = pscal(padd(pmul([a, x0], [x0, 1], p), [2 * b % p], p), 2, p)
    T = psub(pmul([-a % p, x0], [-a % p, x0], p), pscal([x0, 1], 4 * b % p, p), p)
    D = pmul([-x0 % p, 1], [-x0 % p, 1], p)
    sig = {0: [2], 1: S}
    for m in range(1, d):
        sig[m + 1] = psub(pmul(S, sig[m], p), pmul(pmul(T, D, p), sig[m - 1], p), p)
    # phi(z,u) = sum_i c_i(u) z^i, c_i = f_i h - h_i f - j h_i h
    c = []
    for i in range(d + 1):
        fi = f[i] if i < len(f) else 0; hi = h[i] if i < len(h) else 0
        t = psub(pscal(h, fi, p), pscal(f, hi, p), p)
        c.append(psub(t, pscal(h, j * hi % p, p), p))
    M = []
    for i in range(d + 1):
        M = padd(M, pmul(pmul(c[i], c[i], p), pmul(ppow(D, d - i, p), ppow(T, i, p), p), p), p)
        for l in range(i + 1, d + 1):
            term = pmul(pmul(c[i], c[l], p), pmul(pmul(ppow(D, d - l, p), ppow(T, i, p), p), sig[l - i], p), p)
            M = padd(M, term, p)
    return M, D

def solve_nullspace(rows, ncols, p):
    rows = [r[:] for r in rows]; piv = []; r = 0
    for cidx in range(ncols):
        pr = next((i for i in range(r, len(rows)) if rows[i][cidx] % p), None)
        if pr is None: continue
        rows[r], rows[pr] = rows[pr], rows[r]
        inv = pow(rows[r][cidx], -1, p); rows[r] = [v * inv % p for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][cidx] % p:
                fct = rows[i][cidx]; rows[i] = [(v - fct * w) % p for v, w in zip(rows[i], rows[r])]
        piv.append(cidx); r += 1
    free = [c for c in range(ncols) if c not in piv]
    if not free: return None
    fc = free[0]; v = [0] * ncols; v[fc] = 1
    for i, pc in enumerate(piv): v[pc] = (-rows[i][fc]) % p
    return v

def c1():
    p, Nmax = 1009, 60
    E, P, r, rng = setup(101, p, Nmax)
    X = {k: xk(E, P, k) for k in range(1, 2 * Nmax + 2)}
    stats = dict(identity=0, nonzero=0, vanish=0, degok=0, cases=0, skipped=0)
    for trial in range(60):
        d = rng.randrange(1, 6); j = rng.randrange(1, 20)
        x0 = X[j]
        f = [rng.randrange(p) for _ in range(d + 1)]; h = [rng.randrange(p) for _ in range(d + 1)]
        M, D = pair_M(E, x0, f, h, j, d)
        assert deg(M) <= 4 * d; stats['degok'] += 1
        assert M, 'M == 0 for random f,h'; stats['nonzero'] += 1
        for k in range(1, Nmax + 1):
            if k == j: continue
            u = X[k]; z1, z2 = X[k + j], X[abs(k - j)]
            phi = lambda z: (peval(f, z, p) * peval(h, u, p) - peval(f, u, p) * peval(h, z, p) - j * peval(h, z, p) * peval(h, u, p)) % p
            assert peval(M, u, p) == pow(peval(D, u, p), d, p) * phi(z1) * phi(z2) % p
            stats['identity'] += 1
    # interpolating (f,h) on a set A of size 2d+1 containing many pairs at difference j
    for trial in range(60):
        d = rng.randrange(1, 6); j = rng.randrange(1, 8)
        starts = rng.sample(range(j + 1, Nmax - j), d); A = sorted(set(starts) | {s + j for s in starts})
        A = A[:2 * d + 1]
        rows = [[pow(X[k], i, p) for i in range(d + 1)] + [(-k * pow(X[k], i, p)) % p for i in range(d + 1)] for k in A]
        v = solve_nullspace(rows, 2 * d + 2, p)
        if v is None: stats['skipped'] += 1; continue
        f, h = trim(v[:d + 1]), trim(v[d + 1:])
        if any(peval(h, X[k], p) == 0 for k in A): stats['skipped'] += 1; continue
        M, D = pair_M(E, X[j], f + [0] * (d + 1 - len(f)), h + [0] * (d + 1 - len(h)), j, d)
        assert M, 'M==0 for interpolant'
        assert deg(M) <= 4 * d
        pairs = [k for k in A if k + j in A and k != j]
        for k in pairs: assert peval(M, X[k], p) == 0; stats['vanish'] += 1
        assert len(pairs) <= 4 * d
        stats['cases'] += 1
    return stats

# ---------- C2: trees ----------
def gen_tree(rng, Lleft, cap, pool):
    """node: ('op',kind,i,j|const,child) | ('test',reg,zero,nz) | ('leaf',reg). reg index into register list;
    register 0 = u; op creates new register. Divisions are guarded by a test on the divisor (zero branch: leaf 0)."""
    def build(nregs, Lleft):
        cap[0] -= 1
        if Lleft == 0 or cap[0] <= 0:
            return ('leaf', rng.randrange(nregs))
        roll = rng.random()
        if roll < 0.3:
            reg = rng.randrange(nregs)
            return ('test', reg, build(nregs, Lleft), build(nregs, Lleft))
        kind = rng.choice('+-*/')
        i = rng.randrange(nregs); jj = rng.randrange(nregs) if rng.random() < 0.7 else ('c', rng.choice(pool))
        node = ('op', kind, i, jj, build(nregs + 1, Lleft - 1))
        if kind == '/':
            dv = jj
            if isinstance(dv, tuple): return node
            return ('test', dv, ('leaf', ('c', 0)), node)
        return node
    return build(1, Lleft)

def run_tree(tree, u, p):
    regs = [u]; node = tree
    while True:
        if node[0] == 'leaf':
            rg = node[1]; return (rg[1] % p if isinstance(rg, tuple) else regs[rg]), True
        if node[0] == 'test':
            node = node[2] if regs[node[1]] == 0 else node[3]; continue
        _, kind, i, jj, ch = node
        a = regs[i]; b = jj[1] % p if isinstance(jj, tuple) else regs[jj]
        if kind == '+': v = (a + b) % p
        elif kind == '-': v = (a - b) % p
        elif kind == '*': v = a * b % p
        else:
            if b == 0: return None, False
            v = a * pow(b, -1, p) % p
        regs.append(v); node = ch

def generic_path(tree, p):
    """returns (list of (test_reg_pair, generic_branch_is_zero), output pair, L_used); formal pairs (num,den)."""
    regs = [([0, 1], [1])]; node = tree; tests = []; L = 0
    while True:
        if node[0] == 'leaf':
            rg = node[1]
            out = ([rg[1] % p] if isinstance(rg, tuple) and rg[1] % p else [], [1]) if isinstance(rg, tuple) else regs[rg]
            return tests, out, L
        if node[0] == 'test':
            num, den = regs[node[1]]
            is_zero = not num
            tests.append((num, is_zero, node))
            node = node[2] if is_zero else node[3]; continue
        _, kind, i, jj, ch = node
        a = regs[i]; b = ([jj[1] % p] if jj[1] % p else [], [1]) if isinstance(jj, tuple) else regs[jj]
        if kind == '+': v = (padd(pmul(a[0], b[1], p), pmul(b[0], a[1], p), p), pmul(a[1], b[1], p))
        elif kind == '-': v = (psub(pmul(a[0], b[1], p), pmul(b[0], a[1], p), p), pmul(a[1], b[1], p))
        elif kind == '*': v = (pmul(a[0], b[0], p), pmul(a[1], b[1], p))
        else: v = (pmul(a[0], b[1], p), pmul(a[1], b[0], p))
        assert max(deg(v[0]), deg(v[1])) <= 2 ** (L + 1)
        regs.append(v); L += 1; node = ch

def c2():
    p, Nmax = 1009, 60
    E, P, r, rng = setup(202, p, Nmax)
    X = [None] + [xk(E, P, k) for k in range(1, Nmax + 1)]
    worst = 0; byL = {}; trees = 0; nontriv = 0; followers_checked = 0
    for t in range(1500):
        Lb = rng.randrange(1, 6)
        tree = gen_tree(rng, Lb, [120], X[1:])
        tests, (on, od), L = generic_path(tree, p)
        # reachability along generic path = nodes that take every generic branch
        def follows(u):
            node = tree; regs = [u]
            while True:
                if node[0] == 'leaf': return True
                if node[0] == 'test':
                    z = regs[node[1]] == 0
                    gz = any(nd is node and zz for (_, zz, nd) in tests)
                    if z != gz: return False
                    node = node[2] if z else node[3]; continue
                _, kind, i, jj, ch = node
                a = regs[i]; b = jj[1] % p if isinstance(jj, tuple) else regs[jj]
                if kind == '/' and b == 0: return False
                regs.append({'+': (a + b) % p, '-': (a - b) % p, '*': a * b % p}.get(kind, a * pow(b, -1, p) % p if b else 0))
                node = ch
        bad = [k for k in range(1, Nmax + 1) if not follows(X[k])]
        roots = set()
        for num, is_zero, nd in tests:
            if num: roots |= {k for k in range(1, Nmax + 1) if peval(num, X[k], p) == 0}
        assert set(bad) <= roots, (bad, roots)
        # distinct tested registers on the generic path: Sum deg <= 2^(L+1)-1
        seen = {}
        for num, is_zero, nd in tests:
            if num: seen[tuple(num)] = deg(num)
        assert sum(seen.values()) <= 2 ** (L + 1) - 1
        assert len(bad) <= 2 ** (L + 1) - 1
        for k in range(1, Nmax + 1):
            if k in bad: continue
            val, ok = run_tree(tree, X[k], p)
            assert ok and peval(od, X[k], p) != 0
            assert val == peval(on, X[k], p) * pow(peval(od, X[k], p), -1, p) % p
            followers_checked += 1
        worst = max(worst, len(bad)); byL[L] = max(byL.get(L, 0), len(bad)); nontriv += bool(bad); trees += 1
    return dict(trees=trees, trees_with_bad=nontriv, max_bad=worst, max_bad_by_L=dict(sorted(byL.items())), followers_checked=followers_checked)

if __name__ == '__main__':
    print('C1', c1()); print('C2', c2())
