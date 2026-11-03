"""E2: pullback Y_phi: S_3(phi(t1),phi(t2),x3)=0 for phi of degree e.  (a) exact smoothness in P1xP1 over Q (Groebner, 4 charts)
=> genus = arithmetic genus (2e-1)^2;  (b) Riemann-Hurwitz prediction; (c) F_p point counts vs Weil window p+1 +- 2g sqrt p."""
import sympy as sp, random, numpy as np, sys, time
x1, x2, t1, t2, u, v = sp.symbols('x1 x2 t1 t2 u v')
def S3(X1, X2, X3, a, b):
    return sp.expand((X1-X2)**2*X3**2 - 2*((X1+X2)*(X1*X2+a)+2*b)*X3 + ((X1*X2-a)**2 - 4*b*(X1+X2)))
def smooth_chart(F, e):
    # chart handling: substitute t -> 1/u and clear denominators (bidegree (2e,2e))
    res = []
    for sub1, s1 in ((t1, t1), (t1, 1/u)):
        for sub2, s2 in ((t2, t2), (t2, 1/v)):
            G = sp.together(F.subs({t1: s1, t2: s2}, simultaneous=True))
            G = sp.numer(G)
            vars_ = [w for w, s in ((t1, s1), (t2, s2)) if True]
            vs = [t1 if s1 == t1 else u, t2 if s2 == t2 else v]
            Gp = sp.Poly(G, *vs)
            I = sp.groebner([G, sp.diff(G, vs[0]), sp.diff(G, vs[1])], *vs, order='grevlex', domain=sp.QQ)
            res.append(list(I.exprs) == [1])
    return res
rng = random.Random(5)
print("(a) smoothness over Q of F(phi(t1),phi(t2)) in the four charts of P1xP1 (True = smooth => genus (2e-1)^2)")
for e, kind in ((1, 'identity'), (2, 't^2'), (2, 'generic quadratic'), (3, 't^3'), (3, 'generic cubic')):
    a, b, x3v = 2, 3, 5     # fixed rational curve y^2=x^3+2x+3, x(R)=5 (rational; genericity checked by result)
    if kind.startswith('generic'):
        phi = lambda t: t**e + 3*t**(e-1) + 7*t + 1 if e == 3 else t**2 + 5*t
    elif kind == 'identity': phi = lambda t: t
    else: phi = lambda t: t**e
    F = S3(phi(t1), phi(t2), x3v, a, b)
    t0 = time.time(); r = smooth_chart(F, e)
    print(f"e={e} {kind:18s} bidegree=({sp.degree(F,t1)},{sp.degree(F,t2)}) arithmetic genus (2e-1)^2={(2*e-1)**2}; charts smooth={r}; {time.time()-t0:.1f}s")
print()
print("(c) F_p point counts of Y (phi = t^e, p = 1 mod e); N = #{(t1,t2) in F_p^2 : F=0} affine;  Weil window half-width 2g sqrt p with g=(2e-1)^2")
def count_pairs(a_, b_, p, xr):
    X1 = np.arange(p, dtype=np.int64)[:, None]; X2 = np.arange(p, dtype=np.int64)[None, :]
    val = ((X1-X2)**2 % p * xr % p * xr - 2*(((X1+X2) * ((X1*X2 + a_) % p) + 2*b_) % p) * xr + (X1*X2 - a_)**2 % p - 4*b_*(X1+X2)) % p
    return (val == 0)
def is_prime(n):
    return n > 1 and all(n % q for q in range(2, int(n**.5)+1))
print(" p     e   g=(2e-1)^2  2g*sqrt(p)  N_affine(Y)   N-p      |N-p|/sqrt(p)   |phi(F_p)|")
for p in (1009, 2017, 4001, 6007):
    for e in (1, 2, 3, 4, 5, 6):
        if (p-1) % e: continue
        a_, b_ = rng.randrange(1, p), rng.randrange(1, p)
        xr = rng.randrange(1, p)
        M = count_pairs(a_, b_, p, xr)     # M[x1,x2] bool on C_R
        n_phi = np.zeros(p, dtype=np.int64)
        for t in range(p): n_phi[pow(t, e, p)] += 1
        N = int((M * n_phi[:, None] * n_phi[None, :]).sum())
        g = (2*e-1)**2
        print(f"{p:5d} {e:3d} {g:6d} {2*g*p**.5:10.0f} {N:10d} {N-p:8d}   {abs(N-p)/p**.5:8.2f}      {int((n_phi>0).sum())}")
