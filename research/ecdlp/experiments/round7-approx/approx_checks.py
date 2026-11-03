"""ECDLP-21 / RUN-eb84ffa8: partial-agreement lower bounds, toy checks. stdlib only, seeded."""
import sys, os, random, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from toyec import Curve, is_prime

def prime_order_curves(rng, pmin, pmax, count, need_r_ge=7):
    out = []
    tries = 0
    while len(out) < count and tries < 20000:
        tries += 1
        p = rng.choice([q for q in range(pmin, pmax) if is_prime(q)])
        a, b = rng.randrange(p), rng.randrange(p)
        try: E = Curve(a, b, p)
        except ValueError: continue
        pts = E.points(); n = len(pts)
        if not is_prime(n) or n < need_r_ge: continue
        P = rng.choice([q for q in pts if q is not None])
        out.append((E, P, n))
    return out

def rank_solve(rows, rhs, p):
    """Gaussian elimination mod p; returns True iff A z = rhs consistent."""
    M = [r[:] + [c] for r, c in zip(rows, rhs)]
    ncol = len(rows[0]); piv = 0
    for c in range(ncol):
        s = next((i for i in range(piv, len(M)) if M[i][c] % p), None)
        if s is None: continue
        M[piv], M[s] = M[s], M[piv]
        inv = pow(M[piv][c], -1, p)
        M[piv] = [v * inv % p for v in M[piv]]
        for i in range(len(M)):
            if i != piv and M[i][c] % p:
                f = M[i][c]; M[i] = [(v - f * w) % p for v, w in zip(M[i], M[piv])]
        piv += 1
    return all(any(v % p for v in row[:-1]) or row[-1] % p == 0 for row in M)

def nullspace(rows, p, ncol):
    M = [r[:] for r in rows]; piv = 0; pivcols = []
    for c in range(ncol):
        s = next((i for i in range(piv, len(M)) if M[i][c] % p), None)
        if s is None: continue
        M[piv], M[s] = M[s], M[piv]
        inv = pow(M[piv][c], -1, p); M[piv] = [v * inv % p for v in M[piv]]
        for i in range(len(M)):
            if i != piv and M[i][c] % p:
                f = M[i][c]; M[i] = [(v - f * w) % p for v, w in zip(M[i], M[piv])]
        pivcols.append(c); piv += 1
    free = [c for c in range(ncol) if c not in pivcols]
    basis = []
    for fc in free:
        z = [0] * ncol; z[fc] = 1
        for i, pc in enumerate(pivcols): z[pc] = (-M[i][fc]) % p
        basis.append(z)
    return basis

def monos(D):  # basis of L(D*O): x^a y^b, b in {0,1}, 2a+3b <= D
    return [(a, b) for b in (0, 1) for a in range(D // 2 + 1) if 2 * a + 3 * b <= D]

def evalrow(E, Q, ms):
    x, y = Q; p = E.p
    return [pow(x, a, p) * pow(y, b, p) % p for a, b in ms]

def min_poly_D(E, pts, vals):
    """smallest D with f in L(D*O) (polynomial in x,y) and f(Q)=val on all given points."""
    for D in range(0, 4 * len(pts) + 10):
        ms = monos(D)
        if rank_solve([evalrow(E, Q, ms) for Q in pts], vals, E.p): return D
    return None

def min_rat_D(E, pts, vals, rng):
    """smallest D with u,v in L(D*O), u(Q)=val*v(Q), v(Q)!=0 on pts (then deg(u/v)<=D)."""
    p = E.p
    for D in range(1, 4 * len(pts) + 10):
        ms = monos(D); n = len(ms)
        rows = []
        for Q, val in zip(pts, vals):
            r = evalrow(E, Q, ms)
            rows.append(r + [(-val * c) % p for c in r])
        ns = nullspace(rows, p, 2 * n)
        for _ in range(30):
            if not ns: break
            z = [0] * (2 * n)
            for b in ns:
                c = rng.randrange(p); z = [(s + c * t) % p for s, t in zip(z, b)]
            v = z[n:]
            if any(v) and all(sum(c * w for c, w in zip(evalrow(E, Q, ms), v)) % p for Q in pts):
                return D
    return None

def T(A, j):
    S = set(A); return sum(1 for k in A if k + j in S)

def maxT(A, N, J):
    return max(T(A, j) for j in range(1, J + 1))

def S3(A, j):
    S = set(A); return sum(1 for k in A if k - j in S and k + j in S)

def lagrange_degree(xs, ys, p):
    # Newton divided differences mod p; return degree of interpolant
    n = len(xs); c = ys[:]
    for lvl in range(1, n):
        for i in range(n - 1, lvl - 1, -1):
            c[i] = (c[i] - c[i - 1]) * pow(xs[i] - xs[i - lvl], -1, p) % p
    d = n - 1
    while d > 0 and c[d] == 0: d -= 1
    return d

def exp1(rng):
    print('== E1: f(kP)=k on random delta-subset A of [1,N]; polynomial & two-section rational minima vs bounds')
    print('p r N delta m maxT_j  bound_avg=m(m-1)/(4(N-1)) bound_maxT/2  minD_poly minD_rat  viol')
    viol = 0
    for E, P, r in prime_order_curves(rng, 23, 60, 6):
        p = E.p
        pts = [E.mul(k, P) for k in range(1, r)]
        N = min(r - 1, p - 1)
        for delta in (0.3, 0.5, 0.8, 1.0):
            m = max(3, round(delta * N)); A = sorted(rng.sample(range(1, N + 1), m))
            Q = [pts[k - 1] for k in A]
            Dp = min_poly_D(E, Q, [k % p for k in A]); Dr = min_rat_D(E, Q, [k % p for k in A], rng)
            mt = maxT(A, N, N - 1)
            b1 = m * (m - 1) / (4 * (N - 1)); b2 = mt / 2
            v = (Dp < b2 - 1e-9) or (Dr < b2 - 1e-9) or (Dp < b1 - 1e-9)
            viol += v
            print(p, r, N, delta, m, mt, round(b1, 2), b2, Dp, Dr, 'VIOLATION' if v else 'ok')
    print('violations:', viol)

def exp2(rng):
    print('== E2: x-only g(x(kP))=k^2 on random delta-subset A of [1,N], N=(r-1)/2; deg g vs max_j S3_j/3')
    print('p r N delta m max_j S_j  bound  deg_g viol')
    viol = 0
    for E, P, r in prime_order_curves(rng, 23, 90, 6):
        p = E.p; N = (r - 1) // 2
        if N * N >= p * p: continue
        for delta in (0.4, 0.7, 0.9, 1.0):
            m = max(3, round(delta * N)); A = sorted(rng.sample(range(1, N + 1), m))
            xs = [E.mul(k, P)[0] for k in A]; ys = [k * k % p for k in A]
            d = lagrange_degree(xs, ys, p)
            ms = max(S3(A, j) for j in range(1, N))
            b = ms / 3; v = d < b - 1e-9; viol += v
            print(p, r, N, delta, m, ms, round(b, 2), d, 'VIOLATION' if v else 'ok')
    print('violations:', viol)

def exp3(rng):
    print('== E3: structured A: interval [1,m] and AP {s,2s..}: tightness of T_j/2 bound (polynomial, rational minima)')
    for E, P, r in prime_order_curves(rng, 41, 70, 3):
        p = E.p; N = min(r - 1, p - 1)
        for name, A in (('interval m=N/2', list(range(1, N // 2 + 1))),
                        ('AP step3', list(range(3, N + 1, 3))),
                        ('AP step5', list(range(5, N + 1, 5)))):
            Q = [E.mul(k, P) for k in A]; vals = [k % p for k in A]
            print(p, r, N, name, 'm', len(A), 'maxT/2', maxT(A, N, N - 1) / 2,
                  'minD_poly', min_poly_D(E, Q, vals), 'minD_rat', min_rat_D(E, Q, vals, rng))

def exp4(rng):
    print('== E4: N>=p example: constant f=a agrees with k mod p on k=a (mod p); h_j for j=p is identically 0 (j=0 mod p excluded)')
    for p in range(5, 60):
        if not is_prime(p): continue
        for a in range(0, p):
            for b in range(1, p):
                try: E = Curve(a, b, p)
                except ValueError: continue
                n = E.order()
                if is_prime(n) and n > p + 1:
                    P = next(q for q in E.points() if q is not None)
                    N = n - 1; c = 1
                    A = [k for k in range(1, N + 1) if k % p == c]
                    print('p', p, 'r', n, 'N', N, 'f=const', c, 'agreement size', len(A), 'delta', round(len(A) / N, 3),
                          'T_j (1<=j<p) =', max(T(A, j) for j in range(1, p)), ' T_p =', T(A, p), ' deg f = 0')
                    return
    print('no example found')

if __name__ == '__main__':
    rng = random.Random(20261103)
    for e in (exp1, exp2, exp3, exp4): e(rng)
