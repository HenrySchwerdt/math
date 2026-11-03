"""Usage: gb.py M D  -- sympy groebner (modulus p, grevlex) on the S_3-tower system for m=M summands over the coset base x^D = c, p ~ D^5.
M=2: {S3(x1,x2,xR)}; M=3: {S3(x1,x2,U), S3(U,x3,xR)}; M=4: {S3(x1,x2,U), S3(x3,x4,T), S3(U,T,xR)}; plus x_i^D = c. Planted target. One JSON line (run under external timeout)."""
import sys, json, time, random
from sympy import symbols, groebner, Poly, expand
from lib18 import *
M, D = int(sys.argv[1]), int(sys.argv[2])
rng = random.Random(1800 + 7 * D)
while True:
    p = (rng.randrange(D ** 5 // 2, D ** 5) // D) * D + 1
    if is_prime(p): break
a, b = rng.randrange(1, p), rng.randrange(1, p)
E = EC(a, b, p)
fac = [q for q in range(2, D + 1) if D % q == 0 and is_prime(q)]
while True:
    zeta = pow(rng.randrange(2, p), (p - 1) // D, p)
    if all(pow(zeta, D // q, p) != 1 for q in fac): break
g = rng.randrange(1, p); xs = [g * pow(zeta, i, p) % p for i in range(D)]
cls = [(x, sqrt_mod(x ** 3 + a * x + b, p)) for x in xs]; cls = [c for c in cls if c[1]]
while len(cls) < 2:
    g = rng.randrange(1, p); xs = [g * pow(zeta, i, p) % p for i in range(D)]
    cls = [(x, sqrt_mod(x ** 3 + a * x + b, p)) for x in xs]; cls = [c for c in cls if c[1]]
pts = [rng.choice(cls) for _ in range(M)]
R = None
for q in pts: R = E.add(R, q)
if R is None: print(json.dumps(dict(skip=True))); sys.exit()
cc = pow(xs[0], D, p)
X = symbols('x1:%d' % (M + 1)); U, T = symbols('U T')
def S3s(u, v, w):
    return expand((u - v) ** 2 * w ** 2 - 2 * ((u + v) * (u * v + a) + 2 * b) * w + (u * v - a) ** 2 - 4 * b * (u + v))
if M == 2: F = [S3s(X[0], X[1], R[0])]; V = list(X)
elif M == 3: F = [S3s(X[0], X[1], U), S3s(U, X[2], R[0])]; V = list(X) + [U]
else: F = [S3s(X[0], X[1], U), S3s(X[2], X[3], T), S3s(U, T, R[0])]; V = list(X) + [U, T]
F += [x ** D - cc for x in X]
t = time.time()
G = groebner(F, *V, modulus=p, order='grevlex')
tg = time.time() - t
print(json.dumps(dict(m=M, d=D, p=p, nclasses=len(cls), gb_time=tg, gb_len=len(G.exprs), gb_maxdeg=max(Poly(q, *V).total_degree() for q in G.exprs))), flush=True)
