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
def tjurina(G, vs):
    """dim_Q Q[vs]/(G,G_vs...) = total Tjurina number of affine singular points (inf if positive-dimensional)."""
    I = sp.groebner([G] + [sp.diff(G, w) for w in vs], *vs, order='grevlex', domain=sp.QQ)
    lms = [sp.Poly(g, *vs).monoms(order='grevlex')[0] for g in I.exprs]
    if lms == [(0, 0)]: return 0
    # count standard monomials (finite iff pure powers of both variables occur)
    mx = [None, None]
    for m in lms:
        if m[1] == 0: mx[0] = m[0] if mx[0] is None else min(mx[0], m[0])
        if m[0] == 0: mx[1] = m[1] if mx[1] is None else min(mx[1], m[1])
    if None in mx: return float('inf')
    return sum(1 for i in range(mx[0]) for j in range(mx[1]) if not any(i >= m[0] and j >= m[1] for m in lms))
def charts(F):
    out = []
    for s1 in (t1, 1/u):
        for s2 in (t2, 1/v):
            G = sp.numer(sp.together(F.subs({t1: s1, t2: s2}, simultaneous=True)))
            vs = [t1 if s1 == t1 else u, t2 if s2 == t2 else v]
            out.append(tjurina(G, vs))
    return out
print("(a) total Tjurina number (= sum of delta-type local invariants; 0 = smooth) per chart of P1xP1: [t1,t2], [t1,1/t2], [1/t1,t2], [1/t1,1/t2]")
print("    genus(normalization) = (2e-1)^2 - sum delta, delta = floor(e/2) at each of 2e cusp/node points (checked via Tjurina: nodes tau=1, cusp tau=2)")
a, b, x3v = 2, 3, 5
cases = [(1, 'phi=t', lambda t: t),
         (2, 'phi=t^2 (poly, pole order e at inf)', lambda t: t**2),
         (3, 'phi=t^3', lambda t: t**3),
         (2, 'phi=(t^2+1)/(t^2+2t+3) generic rational, inf unramified', None),
         (3, 'phi=(t^3+t+1)/(t^3+2t^2+5) generic rational', None)]
for e, name, phi in cases:
    t0 = time.time()
    if phi is None:
        N = {2: t1**2+1, 3: t1**3+t1+1}[e]; Dn = {2: t1**2+2*t1+3, 3: t1**3+2*t1**2+5}[e]
        ph = lambda t, N=N, Dn=Dn: N.subs(t1, t)/Dn.subs(t1, t)
    else: ph = phi
    F = S3(ph(t1), ph(t2), x3v, a, b)
    r = charts(F)
    print(f"e={e} {name:62s} arith.genus={(2*e-1)**2:3d} Tjurina per chart={r}  ({time.time()-t0:.1f}s)")
print()
print("(c) F_p point counts of Y (phi = t^e, p = 1 mod e); N = #{(t1,t2) in F_p^2 : F=0} affine;  Weil window half-width 2g sqrt p with g=g_mono(e) (even e: (3e-1)(e-1); odd e: 3e^2-3e+1; derived in report)")
def count_pairs(a_, b_, p, xr):
    X1 = np.arange(p, dtype=np.int64)[:, None]; X2 = np.arange(p, dtype=np.int64)[None, :]
    val = ((X1-X2)**2 % p * xr % p * xr - 2*(((X1+X2) * ((X1*X2 + a_) % p) + 2*b_) % p) * xr + (X1*X2 - a_)**2 % p - 4*b_*(X1+X2)) % p
    return (val == 0)
def is_prime(n):
    return n > 1 and all(n % q for q in range(2, int(n**.5)+1))
print(" p     e   g_mono(e)  2g*sqrt(p)  N_affine(Y)   N-p      |N-p|/sqrt(p)   |phi(F_p)|")
for p in (1009, 2017, 4001, 6007):
    for e in (1, 2, 3, 4, 5, 6):
        if (p-1) % e: continue
        a_, b_ = rng.randrange(1, p), rng.randrange(1, p)
        xr = rng.randrange(1, p)
        M = count_pairs(a_, b_, p, xr)     # M[x1,x2] bool on C_R
        n_phi = np.zeros(p, dtype=np.int64)
        for t in range(p): n_phi[pow(t, e, p)] += 1
        N = int((M * n_phi[:, None] * n_phi[None, :]).sum())
        g = 1 if e == 1 else ((3*e-1)*(e-1) if e % 2 == 0 else 3*e*e-3*e+1)
        print(f"{p:5d} {e:3d} {g:6d} {2*g*p**.5:10.0f} {N:10d} {N-p:8d}   {abs(N-p)/p**.5:8.2f}      {int((n_phi>0).sum())}")
