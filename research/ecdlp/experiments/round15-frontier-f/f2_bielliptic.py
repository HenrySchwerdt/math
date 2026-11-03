"""F2 (candidates b/c, g=2, N=2): bielliptic genus-2 cover C: y^2 = w^6 + a w^2 + b -> E: y^2=x^3+ax+b (x=w^2)
and -> E'': y^2 = x^3 + a x^2 + b^2 (x'=b/w^2, y'=b y/w^3).  Albanese map phi(P) = (pi1(P), pi2(P)-pi2(inf+)) in E x E''.
Relation in J(C) among places  <=>  (up to the kernel, a 2-group) both components vanish.  Counts closed triples among a random
symmetric base S of affine degree-1 places: E-only (pushed-down relations) versus full product (true J-relations).
Usage: f2_bielliptic.py p_lo seed s_factor"""
import sys, os, random
from math import isqrt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from toyec import Curve, is_prime

def make_add(a2, a4, a6, p):  # y^2 = x^3 + a2 x^2 + a4 x + a6
    def add(P, Q):
        if P is None: return Q
        if Q is None: return P
        if P[0] == Q[0]:
            if (P[1] + Q[1]) % p == 0: return None
            lam = (3*P[0]*P[0] + 2*a2*P[0] + a4) * pow(2*P[1], -1, p) % p
        else:
            lam = (Q[1]-P[1]) * pow(Q[0]-P[0], -1, p) % p
        x3 = (lam*lam - a2 - P[0] - Q[0]) % p
        return (x3, (lam*(P[0]-x3) - P[1]) % p)
    neg = lambda P: None if P is None else (P[0], (-P[1]) % p)
    return add, neg

def count_pts(a2, a4, a6, p):
    sq = {}
    for y in range(p): sq[y*y % p] = sq.get(y*y % p, 0) + 1
    return 1 + sum(sq.get((x**3 + a2*x*x + a4*x + a6) % p, 0) for x in range(p))

def run(p, seed, sf):
    rng = random.Random(seed)
    while True:
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        if (4*a**3 + 27*b*b) % p == 0: continue
        n = Curve(a, b, p).order()
        if is_prime(n) and n != p and count_pts(0, a, b, p) == n: break
    n2 = count_pts(a, 0, b*b, p)
    addE, negE = make_add(0, a, b, p)
    addF, negF = make_add(a, 0, b*b, p)
    sq = {}
    for y in range(p): sq.setdefault(y*y % p, []).append(y)
    base2 = (0, b % p)   # pi2(inf+): X=0,Y=+1 -> (x',y')=(0,b); on E'': y^2=b^2 ok
    C = [(w, y) for w in range(p) for y in sq.get((pow(w, 6, p) + a*w*w + b) % p, [])]
    s = max(10, int(sf*isqrt(p)))
    S = rng.sample(C, s)
    S = list({(w, y) for (w, y) in S} | {(w, (-y) % p) for (w, y) in S})
    def phi(P):
        w, y = P
        p1 = (w*w % p, y)
        if w == 0: p2 = None
        else:
            iw = pow(w, -1, p)
            p2 = (b*iw*iw % p, b*y*pow(iw, -3, p) % p) if False else (b*iw*iw % p, b*y*pow(iw, 3, p) % p)
        assert (p1[1]**2 - (p1[0]**3 + a*p1[0] + b)) % p == 0
        if p2 is not None: assert (p2[1]**2 - (p2[0]**3 + a*p2[0]**2 + b*b)) % p == 0
        return p1, addF(p2, negF(base2))
    ph = [phi(P) for P in S]
    # E-only index and full index
    idxE, idxF = {}, {}
    for k, (u, v) in enumerate(ph):
        idxE.setdefault(u, []).append(k); idxF.setdefault((u, v), []).append(k)
    cE = cF = 0
    for i in range(len(S)):
        for j in range(i, len(S)):
            u = addE(ph[i][0], ph[j][0])
            nu = negE(u)
            cE += len(idxE.get(nu, ()))
            v = addF(ph[i][1], ph[j][1])
            cF += len(idxF.get((nu, negF(v)), ()))
    return dict(p=p, r=n, r2=n2, places=len(C), s=len(S), pushed_down_closed=cE, full_J_closed=cF,
                ratio=(cE/cF if cF else None), predicted_ratio_if_random=n2)

if __name__ == '__main__':
    p = int(sys.argv[1])
    while not is_prime(p): p += 1
    print(run(p, int(sys.argv[2]), float(sys.argv[3])))
