"""E3: sympy Groebner (grevlex then lex fallback not used) on the PKM-chain-free direct system {S_4(x1,x2,x3,xT)=0, x_i^d = c} over GF(p), m=3.
Usage: f3_groebner.py D SEED   (prints one json line; run under an external timeout)"""
import sys, json, random, time
from sympy import symbols, Poly, groebner, GF, resultant, expand
from f_lib import *
D, seed = int(sys.argv[1]), int(sys.argv[2])
rng = random.Random(1500 + 31 * D + seed)
while True:
    p = rng.randrange(max(D ** 3 // 2, 50), 2 * D ** 3 + 100) // D * D + 1
    if is_prime(p): break
a, b = rng.randrange(1, p), rng.randrange(1, p)
x1, x2, x3, X = symbols('x1 x2 x3 X')
def S3(u, v, w):
    return expand((u - v) ** 2 * w ** 2 - 2 * ((u + v) * (u * v + a) + 2 * b) * w + (u * v - a) ** 2 - 4 * b * (u + v))
A = Poly(S3(x1, x2, X), X); B = Poly(S3(x3, symbols('xT'), X), X)
a2, a1, a0 = [A.coeff_monomial(X ** k) for k in (2, 1, 0)]; b2, b1, b0 = [B.coeff_monomial(X ** k) for k in (2, 1, 0)]
S4 = expand((a2 * b0 - a0 * b2) ** 2 - (a2 * b1 - a1 * b2) * (a1 * b0 - a0 * b1))
rng2 = random.Random(seed)
V = base_coset(p, a, b, D, rng2); xs = sorted(V)
while len(xs) < 4:   # need >= 4 base points (3 summands, distinct choices)
    rng2 = random.Random(rng2.random()); V = base_coset(p, a, b, D, rng2); xs = sorted(V)
# pick target as an actual sum of three base points so that a solution exists
E = Curve(a, b, p); pts = [(x, V[x]) for x in xs]
u = rng2.sample(pts, 3); T = E.add(E.add(u[0], u[1]), u[2])
if T is None: print(json.dumps(dict(exp='gb', D=D, skip=True))); sys.exit()
xT = T[0]; c = [pow(rng2.choice(xs), D, p)] * 3  # all x^D equal on a coset
cc = pow(xs[0], D, p)
F = [S4.subs(symbols('xT'), xT)] + [x ** D - cc for x in (x1, x2, x3)]
t = time.time()
G = groebner(F, x3, x2, x1, modulus=p, order='grevlex')
tg = time.time() - t
# count solutions by brute force on the coset for comparison (ordered triples with S4 = 0)
fn = lambda *v: None
import numpy as np
from sympy import lambdify
fS = lambdify((x1, x2, x3), F[0], 'math')
brute = sum(1 for i in xs for j in xs for k in xs if int(fS(i, j, k)) % p == 0)
print(json.dumps(dict(exp='gb', D=D, p=p, s=len(xs), gb_time=tg, gb_len=len(G.exprs), gb_maxdeg=max(Poly(g, x1, x2, x3).total_degree() for g in G.exprs),
                      brute_ordered_solutions=brute, brute_cost=len(xs) ** 3)), flush=True)
