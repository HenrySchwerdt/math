"""Seeded toy check for ECDLP-14 (RUN-e7c9feff).
(A) minimal pole order m* of f in L(m*O) (basis x^i, x^i y; pole orders 2i, 2i+3) with f(kP)=k mod p, k=1..r-1
    vs proven bound m >= (r-2)/2  (Theorem A, N=r-1: 2m >= N-1).
(B) minimal degree D of g in F_p[X] with g(x(kP)) = k^2 mod p, k=1..(r-1)/2, vs proven D >= (r-1)/8 (Theorem B).
Pure python, sys.path to ../lib/toyec.py. Deterministic: curves enumerated in fixed order, seed fixes subset order."""
import sys, random, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from toyec import Curve, is_prime
random.seed(20261103)

def rank_solve(rows, rhs, p):
    """Return True iff linear system rows*c = rhs solvable over F_p (rows: list of lists)."""
    n = len(rows); mcols = len(rows[0]) if rows else 0
    M = [rows[i][:] + [rhs[i] % p] for i in range(n)]
    r = 0
    for c in range(mcols):
        piv = next((i for i in range(r, n) if M[i][c] % p), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]
        inv = pow(M[r][c], -1, p)
        M[r] = [v * inv % p for v in M[r]]
        for i in range(n):
            if i != r and M[i][c] % p:
                f = M[i][c]; M[i] = [(a - f * b) % p for a, b in zip(M[i], M[r])]
        r += 1
    return all(any(v % p for v in row[:-1]) or row[-1] % p == 0 for row in M)

def basis(m):
    b = []  # (poleorder, i, j)
    for i in range(0, m // 2 + 1):
        if 2 * i <= m: b.append((2 * i, i, 0))
        if 2 * i + 3 <= m: b.append((2 * i + 3, i, 1))
    return b

def min_pole_order(E, P, r):
    p = E.p
    pts = []; Q = P
    for k in range(1, r):
        pts.append((k, Q)); Q = E.add(Q, P)
    for m in range(0, 2 * r + 4):
        B = basis(m)
        rows = [[pow(Q[0], i, p) * pow(Q[1], j, p) % p for (_, i, j) in B] for (k, Q) in pts]
        if rows and rank_solve(rows, [k for k, _ in pts], p):
            return m
    return None

def interp_degree(xs, ys, p):
    n = len(xs); c = ys[:]
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            c[i] = (c[i] - c[i - 1]) * pow(xs[i] - xs[i - j], -1, p) % p
    d = n - 1
    # Newton coefficients nonzero up to degree d
    while d > 0 and c[d] == 0: d -= 1
    return d

out = []
cases = []
for p in [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]:
    for a in range(p):
        for b in range(1, p):
            if (4 * a**3 + 27 * b * b) % p == 0: continue
            cases.append((p, a, b))
random.shuffle(cases)
seen = set(); done = 0
print("p a b | N=#E r | m*_A bound(r-2)/2 ok | D*_B bound(r-1)/8 ok")
for (p, a, b) in cases:
    E = Curve(a, b, p); pts = E.points(); N = len(pts)
    # find prime-order subgroup r>=7, r odd prime
    from math import isqrt
    rs = [q for q in range(7, N + 1) if is_prime(q) and N % q == 0]
    if not rs: continue
    r = max(rs)
    if (p, r) in seen: continue
    P = next((Q for Q in pts[1:] if E.mul(r, Q) is None), None)
    if P is None: continue
    seen.add((p, r))
    mA = min_pole_order(E, P, r)
    okA = mA is not None and 2 * mA >= r - 2
    xs, ys = [], []; Q = P
    for k in range(1, (r - 1) // 2 + 1):
        xs.append(Q[0]); ys.append(k * k % p); Q = E.add(Q, P)
    distinct = len(set(xs)) == len(xs)
    DB = interp_degree(xs, ys, p) if distinct else None
    okB = DB is not None and 8 * DB >= r - 1
    tag = " ANOMALOUS(r=p)" if r == p else (" r>p" if r > p else "")
    print(p, a, b, "|", N, r, "|", mA, (r - 2) / 2, okA, "|", DB, (r - 1) / 8, okB, tag)
    done += 1
    if done >= 40: break
