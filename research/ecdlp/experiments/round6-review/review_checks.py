"""Round 6 adversarial review experiments (RUN-4b283c25). Pure python, seeded.
E0: curves with p | r, r != p (hypothesis r != p of Theorem A).
EB: Theorem B: Lagrange degree of k^2 over x(kP), k<=(r-1)/2, vs (r-5)/6, odd (incl. composite) r.
EB2: extra zero of H at k=(r-1)/2 when p | r (identity check).
EA: Theorem A: minimal pole order m of (i) polynomial interpolants (L(mO)), (ii) rational u/v, u,v in L(mO),
    nondegenerate, compared with (N-1)/2; (iii) minimal total degree d of polynomial in X,Y vs (N-1)/6.
"""
import sys, random, time
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime
random.seed(20261103)
T0 = time.time()

def kernel(rows, ncols, p):
    """kernel basis of matrix rows (list of lists) mod p"""
    M = [r[:] for r in rows]; piv = []; r = 0
    for c in range(ncols):
        s = next((i for i in range(r, len(M)) if M[i][c] % p), None)
        if s is None: continue
        M[r], M[s] = M[s], M[r]
        inv = pow(M[r][c], -1, p); M[r] = [v * inv % p for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] % p:
                f = M[i][c]; M[i] = [(a - f * b) % p for a, b in zip(M[i], M[r])]
        piv.append(c); r += 1
        if r == len(M): break
    free = [c for c in range(ncols) if c not in piv]
    ker = []
    for f in free:
        v = [0] * ncols; v[f] = 1
        for i, c in enumerate(piv): v[c] = (-M[i][f]) % p
        ker.append(v)
    return ker

def has_sol(rows, rhs, ncols, p):
    aug = [r + [b] for r, b in zip(rows, rhs)]
    # consistent iff rank(rows)==rank(aug)
    def rank(M):
        M = [r[:] for r in M]; r = 0
        for c in range(len(M[0])):
            s = next((i for i in range(r, len(M)) if M[i][c] % p), None)
            if s is None: continue
            M[r], M[s] = M[s], M[r]; inv = pow(M[r][c], -1, p); M[r] = [v * inv % p for v in M[r]]
            for i in range(r + 1, len(M)):
                if M[i][c] % p:
                    f = M[i][c]; M[i] = [(a - f * b) % p for a, b in zip(M[i], M[r])]
            r += 1
            if r == len(M): break
        return r
    return rank(rows) == rank(aug)

def lagrange_degree(xs, ys, p):
    n = len(xs); c = ys[:]
    for j in range(1, n):  # Newton divided differences
        for i in range(n - 1, j - 1, -1):
            c[i] = (c[i] - c[i - 1]) * pow(xs[i] - xs[i - j], -1, p) % p
    d = max((i for i in range(n) if c[i] % p), default=0)
    return d

def curves(p, cnt):
    out = []
    while len(out) < cnt:
        a, b = random.randrange(p), random.randrange(p)
        if (4 * a**3 + 27 * b**2) % p: out.append(Curve(a, b, p))
    return out

# ---------- E0: p | r, r != p
print('E0: curves over F_p, p in {5,7,11,13} with point order r a multiple of p, r != p')
for p in (5, 7, 11, 13):
    found = 0
    for a in range(p):
        for b in range(p):
            if (4*a**3+27*b**2) % p == 0: continue
            E = Curve(a, b, p); n = E.order()
            for P in E.points()[1:]:
                r = E.point_order(P, n)
                if r % p == 0 and r != p:
                    found += 1; ex = (a, b, P, r, n); break
    print(' p=%d: curves with such a point: %d %s' % (p, found, '' if not found else 'e.g. (a,b,P,r,#E)=%s' % (ex,)))

# ---------- EB: Theorem B
print('EB: Theorem B, Lagrange degree D of g with g(x(kP))=k^2, k=1..(r-1)/2')
viol = 0; tight = []; tot = 0; stat = {}
for p in (7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61):
    for E in curves(p, 12):
        n = E.order(); seen = set()
        for P in E.points()[1:]:
            r = E.point_order(P, n)
            if r % 2 == 0 or r < 5 or (r, ) in seen: continue
            seen.add((r,))
            m = (r - 1) // 2
            xs = [E.mul(k, P)[0] for k in range(1, m + 1)]
            assert len(set(xs)) == m
            D = lagrange_degree(xs, [k * k % p for k in range(1, m + 1)], p)
            tot += 1
            key = (r % 2, is_prime(r), r == p, r % p == 0)
            stat.setdefault(key, [0, 0, 10**9]); stat[key][0] += 1
            stat[key][1] += (D == m - 1)
            stat[key][2] = min(stat[key][2], D - (r - 5) / 6)
            if D < (r - 5) / 6 - 1e-9: viol += 1; print(' VIOLATION', p, E.a, E.b, P, r, D)
            if D != m - 1: tight.append((p, E.a, E.b, r, D, m - 1))
print(' cases', tot, 'violations of D>=(r-5)/6:', viol)
for k, v in sorted(stat.items(), key=str): print('  (odd,r prime,r==p,p|r)=%s: n=%d, #D==(r-3)/2: %d, min(D-(r-5)/6)=%.2f' % (k, v[0], v[1], v[2]))
print(' cases with D < (r-3)/2 (lower than full Lagrange degree):', len(tight), tight[:8])

# ---------- EB2: H value at k=(r-1)/2
print('EB2: H((r-1)/2 P) = -r mod p (zero iff p | r)')
for r in (5, 7, 9, 11, 13):
    a = (r - 1) // 2
    print('  r=%d: ((a+... )) second difference value = %d' % (r, ((a-1)**2 + a**2 - 2*a**2 - 2)))

# ---------- EA
def monos_L(m):  # basis x^i y^j (j in {0,1}) with pole order 2i+3j <= m
    return [(i, j) for i in range(m // 2 + 1) for j in (0, 1) if 2*i + 3*j <= m]

def evalbasis(E, B, pts):
    p = E.p
    return [[pow(P[0], i, p) * pow(P[1], j, p) % p for (i, j) in B] for P in pts]

def min_poly_pole(E, P, N, mmax):
    p = E.p; pts = [E.mul(k, P) for k in range(1, N + 1)]
    for m in range(2, mmax + 1):
        B = monos_L(m); ev = evalbasis(E, B, pts)
        if has_sol(ev, [k % p for k in range(1, N + 1)], len(B), p): return m
    return None

def min_rational_pole(E, P, N, mmax):
    p = E.p; pts = [E.mul(k, P) for k in range(1, N + 1)]
    for m in range(1, mmax + 1):
        B = monos_L(m) if m != 1 else [(0, 0)]
        ev = evalbasis(E, B, pts); nb = len(B)
        rows = [ev[t] + [(-(t + 1) * c) % p for c in ev[t]] for t in range(N)]
        ker = kernel(rows, 2 * nb, p)
        if not ker: continue
        for _ in range(20):
            z = [0] * (2 * nb)
            for v in ker:
                c = random.randrange(p); z = [(a + c * b) % p for a, b in zip(z, v)]
            vv = [sum(c * e for c, e in zip(z[nb:], ev[t])) % p for t in range(N)]
            if all(vv):  # v(kP) != 0 for all k: u/v is regular at kP with value k
                return m
    return None

def min_total_degree(E, P, N, dmax):
    p = E.p; pts = [E.mul(k, P) for k in range(1, N + 1)]
    for d in range(1, dmax + 1):
        B = [(i, j) for i in range(d + 1) for j in range(d + 1 - i)]
        ev = evalbasis(E, B, pts)
        if has_sol(ev, [k % p for k in range(1, N + 1)], len(B), p): return d
    return None

print('EA: Theorem A on toy curves; rows: p,a,b,r,N, minPolyPole, minRationalPole(u/v), (N-1)/2, minTotalDeg, (N-1)/6')
viol = 0; rows = 0; ratio = []
cfgs = [(11, 3), (13, 3), (17, 3), (19, 3), (23, 2), (29, 2), (31, 2)]
for p, cnt in cfgs:
    for E in curves(p, cnt):
        n = E.order(); best = None
        for P in E.points()[1:]:
            r = E.point_order(P, n)
            if best is None or r > best[1]: best = (P, r)
        P, r = best
        if r < 6: continue
        for N in sorted({2, 3, 4, 5, r // 3, r // 2, r - 3, r - 2, r - 1}):
            if not 2 <= N <= r - 1: continue
            mp = min_poly_pole(E, P, N, N + 3)
            mr = min_rational_pole(E, P, N, N + 3)
            md = min_total_degree(E, P, N, N + 2)
            rows += 1
            if rows <= 45: print(' ', p, E.a, E.b, r, N, mp, mr, (N-1)/2, md, round((N-1)/6, 2))
            for val, bnd, nm in ((mp, (N-1)/2, 'poly pole'), (mr, (N-1)/2, 'rat pole'), (md, (N-1)/6, 'total deg')):
                if val is not None and val < bnd - 1e-9:
                    viol += 1; print('  VIOLATION', nm, p, E.a, E.b, r, N, val, bnd)
            if mr is not None and N >= 8: ratio.append(mr / ((N - 1) / 2))
print(' rows', rows, 'violations', viol, 'rational min-pole / ((N-1)/2): min %.2f max %.2f' % (min(ratio), max(ratio)))

print('EA-p|r: targeted: curve p=5 y^2=x^3+3x (P=(2,2), r=10, p|r, r!=p) and anomalous (r==p) curves')
def targeted(E, P, r, tag):
    for N in (r // 2, r - 2, r - 1):
        mp = min_poly_pole(E, P, N, N + 3); mr = min_rational_pole(E, P, N, N + 3); md = min_total_degree(E, P, N, N + 2)
        print('  %s r=%d N=%d minPolyPole=%s minRatPole<=%s (N-1)/2=%.1f minTotalDeg=%s (N-1)/6=%.2f' % (tag, r, N, mp, mr, (N-1)/2, md, (N-1)/6))
E5 = Curve(3, 0, 5); targeted(E5, (2, 2), 10, 'p=5')
cnt = 0
for p in (7, 11, 13, 17, 19, 23, 29):
    for a in range(p):
        for b in range(p):
            if (4*a**3+27*b**2) % p == 0: continue
            E = Curve(a, b, p)
            if E.order() == p and cnt < 4:
                P = E.points()[1]; targeted(E, P, p, 'anomalous p=%d a=%d b=%d' % (p, a, b)); cnt += 1
print('elapsed %.1fs' % (time.time() - T0))
