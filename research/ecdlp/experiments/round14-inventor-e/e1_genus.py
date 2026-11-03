"""E1: exact genus / structure of the decomposition curve C_R: S_3(x1,x2,x3)=0, x3 fixed; and of its pullbacks
under x = phi(t) (monomial and generic degree e).  sympy exact + brute force over F_p (p <= 2^16)."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from toyec import Curve
import sympy as sp
x1, x2, x3, a, b, t1, t2 = sp.symbols('x1 x2 x3 a b t1 t2')
S3 = sp.expand((x1-x2)**2*x3**2 - 2*((x1+x2)*(x1*x2+a)+2*b)*x3 + ((x1*x2-a)**2 - 4*b*(x1+x2)))
print("S3 bidegree in (x1,x2):", sp.degree(S3, x1), sp.degree(S3, x2), "total deg", sp.Poly(S3, x1, x2).total_degree())
f = lambda z: z**3 + a*z + b
D = sp.factor(sp.discriminant(S3, x2))
print("disc_x2(S3) =", D)
# quartic invariants => j-invariant of the genus-1 curve w^2 = disc(x1)
q = sp.Poly(sp.cancel(D / (16*f(x3))), x1) if sp.simplify(D/(16*f(x3))).is_polynomial(x1) else sp.Poly(D, x1)
print("quartic in x1 (after removing f(x3) factor):", sp.factor(q.as_expr()), " degree", q.degree())
c4, c3, c2, c1, c0 = [q.coeff_monomial(x1**i) for i in (4, 3, 2, 1, 0)]
I = 12*c4*c0 - 3*c3*c1 + c2**2
J = 72*c4*c2*c0 + 9*c3*c2*c1 - 27*c4*c1**2 - 27*c0*c3**2 - 2*c2**3
jq = sp.simplify(1728*4*I**3/(4*I**3 - J**2))
jE = 1728*4*a**3/(4*a**3 + 27*b**2)
print("j(quartic) - j(E) simplifies to:", sp.simplify(jq - jE))

# F_p brute-force: #C_R(F_p) affine pairs vs #E(F_p)
def affine_count(E, R, p):
    a_, b_ = E.a, E.b
    xr = R[0]
    cnt = 0
    for X1 in range(p):
        # quadratic in x2: A x2^2 + B x2 + C
        # S3 = (x1-x2)^2 x3^2 - 2((x1+x2)(x1x2+a)+2b) x3 + (x1x2-a)^2 - 4b(x1+x2)
        A = (x3v := xr)**2 - 2*X1*xr + X1*X1 if False else None
        break
    return None
import numpy as np
def count_pairs(a_, b_, p, xr):
    X1 = np.arange(p, dtype=np.int64)[:, None]; X2 = np.arange(p, dtype=np.int64)[None, :]
    val = ((X1-X2)**2 % p * xr % p * xr - 2*(((X1+X2) * ((X1*X2 + a_) % p) + 2*b_) % p) * xr + (X1*X2 - a_)**2 % p - 4*b_*(X1+X2)) % p
    return int((val == 0).sum())
def order_naive(a_, b_, p):
    sq = np.zeros(p, dtype=np.int64); y = np.arange(p, dtype=np.int64); np.add.at(sq, y*y % p, 1)
    xs = np.arange(p, dtype=np.int64)
    return 1 + int(sq[(xs**3 + a_*xs + b_) % p].sum())
rng = random.Random(14)
print("p, #E, r-type, xR, #C_R affine (x1,x2) in F_p^2, #E-2, #E(F_p)-pairs-by-group-law")
rows = []
for p in (101, 257, 509, 1021, 2053):
    for _ in range(3):
        while True:
            a_, b_ = rng.randrange(p), rng.randrange(p)
            if (4*a_**3 + 27*b_*b_) % p: break
        E = Curve(a_, b_, p); N = order_naive(a_, b_, p)
        # pick a point R of E with 2R != O, R != O
        while True:
            xr = rng.randrange(p); v = (xr**3 + a_*xr + b_) % p
            ys = [y for y in range(p) if y*y % p == v]
            if ys and ys[0] != 0: R = (xr, ys[0]); break
        cnt = count_pairs(a_, b_, p, xr)
        # group-law image {(x(P), x(R-P))}: P != O, R, -R handled by set
        S = set()
        for X in range(p):
            v = (X**3 + a_*X + b_) % p
            for y in [y for y in range(p) if y*y % p == v][:1]:
                P = (X, y); Qp = E.add(R, E.neg(P))
                if Qp is not None: S.add((X, Qp[0]))
        # also include P with R-P=-... covered by sign symmetry: add (x(P), x(R+P))
        for X in range(p):
            v = (X**3 + a_*X + b_) % p
            for y in [y for y in range(p) if y*y % p == v][:1]:
                P = (X, y); Qp = E.add(R, P)
                if Qp is not None: S.add((X, Qp[0]))
        print(p, N, '', xr, cnt, N-2, len(S), "MATCH" if cnt == len(S) else "DIFF")
        rows.append((p, N, cnt, len(S)))
