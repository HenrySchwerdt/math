"""E4: CM / endomorphism-orbit factor base on j=0 curves y^2=x^3+b over F_p (p=1 mod 3, prime order r).
 (a) exact factorisation of S_3 restricted to the omega-orbit line (x, zeta x, z).
 (b) on E(F_p)=<P0>, omega acts as scalar mu (mu^2+mu+1=0 mod r): the base V_B={x(alpha P0): alpha=a+b*omega, |a|,|b|<=B}
     has KNOWN discrete logs (a+b mu mod r).  Count S_3-relations inside V_B: 'trivial' (identity in Z[omega]) vs lattice-induced
     vs a random set of the same size in Z_r/{+-1}.  lattice L={(a,b): a+b mu = 0 mod r}, shortest vector lambda_1 ~ sqrt(r)."""
import sympy as sp, random, numpy as np, math, sys
x, z, w = sp.symbols('x z w')
A, Bb = 0, sp.Symbol('b')
S3 = lambda X1, X2, X3: sp.expand((X1-X2)**2*X3**2 - 2*((X1+X2)*(X1*X2+0)+2*Bb)*X3 + ((X1*X2-0)**2 - 4*Bb*(X1+X2)))
zeta = sp.Rational(-1, 2) + sp.sqrt(-3)/2
F = sp.expand(S3(x, zeta*x, z))
print("(a) S_3(x, zeta x, z) over Q(zeta), a=0 (j=0), as a quadratic in z:")
Pz = sp.Poly(F, z); Aq, Bq, Cq = Pz.all_coeffs()
print("    z^2-coefficient A =", sp.factor(sp.simplify(Aq)))
root1 = zeta**2*x
print("    S_3(x,zeta x, zeta^2 x) =", sp.simplify(sp.expand(F.subs(z, root1))), "   (identity 1+w+w^2=0: P + wP = -w^2 P)")
root2 = sp.simplify(sp.radsimp(sp.simplify(Cq/Aq)/root1))
print("    other root z2 = x((1-w)P) = C/(A*z1) =", sp.factor(root2))
print("    degree of z2 as rational function of x:", sp.degree(sp.numer(sp.together(root2)), x), sp.degree(sp.denom(sp.together(root2)), x))
# (b)
def is_prime(n): return n > 1 and all(n % q for q in range(2, int(n**.5)+1))
def order(b, p):
    sq = np.zeros(p, dtype=np.int64); y = np.arange(p, dtype=np.int64); np.add.at(sq, y*y % p, 1)
    xs = np.arange(p, dtype=np.int64); return 1 + int(sq[(xs**3 + b) % p].sum())
rng = random.Random(14)
def find(pmin, pmax):
    while True:
        p = rng.randrange(pmin, pmax) | 1
        if p % 3 == 1 and is_prime(p):
            for b in range(1, 60):
                r = order(b, p)
                if is_prime(r) and r != p: return p, b, r
def gauss_lambda1(r, mu):
    u, v = (r, 0), (mu, -1)    # lattice {(a,b): a + b mu = 0}: spanned by (r,0),(-mu,1)
    u, v = (r, 0), (-mu % r, 1)
    dot = lambda s, t: s[0]*t[0] + s[1]*t[1]
    while True:
        if dot(u, u) > dot(v, v): u, v = v, u
        m = round(dot(u, v)/dot(u, u))
        if m == 0: break
        v = (v[0]-m*u[0], v[1]-m*u[1])
    return math.sqrt(dot(u, u))
def classes(vals, r): return {min(c % r, (-c) % r) for c in vals}
def count_rel(cls, r):
    cl = sorted(cls); inset = np.zeros(r//2 + 1, dtype=bool); inset[cl] = True
    arr = np.array(cl, dtype=np.int64); n = 0
    for i, c1 in enumerate(cl):
        c2 = arr[i+1:]
        for s3 in (c1 + c2, c1 - c2):
            t = s3 % r; t = np.minimum(t, r - t)
            n += int(inset[t].sum())
    return n    # each unordered triple {c1,c2,c3} of distinct classes is counted a few times; same convention both columns
print("\n(b) p, b, r, mu, lambda1(L)/sqrt(r) ; per B: |V|, relations_obs, relations_trivial(Z[w]-identities), obs-triv, random-set expectation (same |V|)")
for (pmin, pmax) in ((2**12, 2**13), (2**14, 2**15)):
    p, b, r = find(pmin, pmax)
    mu = next(m for m in range(2, r) if (m*m + m + 1) % r == 0)
    lam = gauss_lambda1(r, mu)
    print(f"p={p} b={b} r={r} mu={mu} lambda1={lam:.1f} sqrt(r)={r**.5:.1f}")
    print("   NOTE rel_obs/rel_random count every unordered triple ~3x (once per pair); rel_triv counts distinct triples. Compare rel_obs/3 with rel_triv.")
    print("   B   |V|   rel_obs  rel_triv  rel_obs/3-rel_triv  random_same_size(mean of 5)")
    for B in (2, 4, 8, 16, 32, 48, 64):
        els = [(a, bb) for a in range(-B, B+1) for bb in range(-B, B+1) if (a, bb) != (0, 0)]
        vals = [a + bb*mu for a, bb in els]; cls = classes(vals, r)
        if len(cls) < 3: continue
        obs = count_rel(cls, r)
        # trivial: pairs of box elements (as classes) whose +-sum/difference in Z^2 (not mod r) is again in the box -> identity in Z[omega]
        elset = set(els); triv = set()
        do_triv = len(els) <= 1200
        cl_of = lambda ab: min((ab[0] + ab[1]*mu) % r, (-(ab[0] + ab[1]*mu)) % r)
        for (a1, b1) in (els if do_triv else []):
            for (a2, b2) in els:
                for s in (1, -1):
                    t = (a1 + s*a2, b1 + s*b2)
                    if t in elset:
                        c = tuple(sorted({cl_of((a1, b1)), cl_of((a2, b2)), cl_of(t)}))
                        if len(c) == 3: triv.add(c)
        rs = [count_rel(classes([rng.randrange(1, r) for _ in range(len(cls))], r), r) for _ in range(5)]
        print(f"  {B:3d} {len(cls):5d} {obs:9d} {(len(triv)) if do_triv else 'n/a':>9} {(round(obs/3-len(triv),1)) if do_triv else 'n/a':>9}        {sum(rs)/5:9.1f}")
