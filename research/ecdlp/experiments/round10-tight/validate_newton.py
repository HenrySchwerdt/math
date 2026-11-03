"""Independent check of Newton-coefficient method: Gaussian elimination for the minimal d s.t. a degree<=d poly g exists with g(x_k)=f(k), k<=N.
Seed 12345, p in [17,150], 400 random curve/point cases, random N."""
import random, sys
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime
from tight import factor, newton_coeffs

def solvable(xs, vals, d, p):
    n = len(xs); M = [[pow(x, i, p) for i in range(d+1)] + [v] for x, v in zip(xs, vals)]
    row = 0
    for col in range(d+1):
        piv = next((i for i in range(row, n) if M[i][col]), None)
        if piv is None: continue
        M[row], M[piv] = M[piv], M[row]; iv = pow(M[row][col], -1, p)
        M[row] = [a*iv % p for a in M[row]]
        for i in range(n):
            if i != row and M[i][col]:
                f = M[i][col]; M[i] = [(a-f*b) % p for a, b in zip(M[i], M[row])]
        row += 1
    return all(M[i][d+1] == 0 for i in range(row, n))

rnd = random.Random(12345); done = bad = 0; defs = 0
primes = [q for q in range(17, 151) if is_prime(q)]
while done < 400:
    p = rnd.choice(primes); E = Curve(rnd.randrange(p), rnd.randrange(p), p) if False else None
    try: E = Curve(rnd.randrange(p), rnd.randrange(p), p)
    except ValueError: continue
    pts = E.points(); n = len(pts); rs = [q for q in factor(n) if q >= 7]
    if not rs: continue
    r = rnd.choice(rs); P = None
    for _ in range(20):
        P = E.mul(n//r, rnd.choice(pts))
        if P: break
    if not P: continue
    Nmax = (r-1)//2; xs = []; Q = None
    for k in range(1, Nmax+1): Q = E.add(Q, P); xs.append(Q[0])
    for name, f in (('k', lambda k: k % p), ('k2', lambda k: k*k % p)):
        N = rnd.randint(3, Nmax); vals = [f(k) for k in range(1, N+1)]
        c = newton_coeffs(xs[:N], vals, p); dN = max(j for j, v in enumerate(c) if v)
        # minimal d by elimination
        dm = next(d for d in range(N) if solvable(xs[:N], vals, d, p))
        done += 1; bad += (dm != dN); defs += (dN < N-1)
print('cases', done, 'mismatches', bad, 'with deficit', defs)
