"""Sympy Groebner cross-check of the PKM-style algebraic system on tiny p (correctness + time scaling). Not in the decision."""
import sys, os, time, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d2lib import *
from sympy import symbols, groebner, GF, Poly
x1, x2 = symbols('x1 x2')
rows = []
for p, n in [(257, 4), (1153, 5), (4289, 6), (17921, 7)]:
    rng = random.Random(p)
    # curve; coset of mu_{2^n}
    while True:
        a, b = rng.randrange(p), rng.randrange(p)
        if (4*a**3+27*b*b) % p: break
    inst = dict(p=p, a=a, b=b, n=n)
    xs = fb_coset(inst, rng); c = pow(xs[0], 1 << n, p)
    V = build_V(inst, xs); Vx = set(V)
    sols_true = None
    for trial in range(200):
        xT = rng.randrange(p)
        if pow((xT**3+a*xT+b) % p, (p-1)//2, p) != 1: continue
        # exhaustive: pairs (u,v) in coset (ALL x in coset, algebraic system ignores curve membership of x_i) with S3=0
        def S3(u, v, w): return ((u-v)**2*w*w - 2*((u+v)*(u*v+a)+2*b)*w + ((u*v-a)**2 - 4*b*(u+v))) % p
        brute = sorted((u, v) for u in xs for v in xs if S3(u, v, xT) == 0)
        if len(brute) >= 1: break
    S = (x1-x2)**2*xT**2 - 2*((x1+x2)*(x1*x2+a)+2*b)*xT + ((x1*x2-a)**2 - 4*b*(x1+x2))
    t0 = time.time()
    G = groebner([S, x1**(1 << n) - c, x2**(1 << n) - c], x2, x1, modulus=p, order='lex')
    t = time.time() - t0
    # solutions: roots of last element in x1 then x2
    gl = list(G.exprs); last = [g for g in gl if not g.has(x2)]
    pol = Poly(last[0], x1, modulus=p)
    roots1 = [u for u in xs if pol.eval(u) % p == 0]
    sols = []
    for u in roots1:
        for v in xs:
            if all(g.subs({x1: u, x2: v}) % p == 0 for g in gl): sols.append((u, v))
    row = dict(p=p, d=1 << n, groebner_seconds=t, n_basis=len(gl), deg_univariate=pol.degree(), brute=len(brute), gb_solutions=len(sols), equal=sorted(sols) == brute)
    print(json.dumps(row)); rows.append(row)
