#!/usr/bin/env python3
"""EXP2: Smart's p-adic lift attack on a small anomalous curve (#E(F_p)=p), plus the
negative control: the same 'lift and multiply by #E' map vanishes on non-anomalous curves.
Seeds fixed. Run: python3 exp2.py"""
import random

def is_prime(n):
    if n < 2: return False
    i = 2
    while i*i <= n:
        if n % i == 0: return False
        i += 1
    return True

def count_points(a, b, p):
    sq = [0]*p
    for y in range(p): sq[y*y % p] += 1
    return 1 + sum(sq[(x**3 + a*x + b) % p] for x in range(p))

def aff_add(P, Q, a, m):
    """affine addition mod m (m = p^2); caller guarantees denominators are units."""
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % m == 0: return None
    if P == Q: l = (3*x1*x1 + a) * pow(2*y1, -1, m) % m
    else: l = (y2 - y1) * pow(x2 - x1, -1, m) % m
    x3 = (l*l - x1 - x2) % m
    return (x3, (l*(x1 - x3) - y1) % m)

def lift_point(P, a, b, p):
    """Hensel-lift (x,y) in E(F_p) to E~(Z/p^2) with y != 0 mod p, x kept."""
    x, y = P
    m = p*p
    f = (x**3 + a*x + b) % m
    # y~ = y + p t, (y+pt)^2 = f mod p^2  =>  2 y t = (f - y^2)/p mod p
    t = ((f - y*y) // p) * pow(2*y, -1, p) % p
    return (x, (y + p*t) % m)

def smart_psi(Pt, a, p):
    """psi(Pt) = (-x/y of (p)Pt)/p mod p, for Pt lifted point whose reduction has order p."""
    m = p*p
    R = None
    for _ in range(p-1):   # (p-1)Pt, all denominators units since multiples 1..p-1 are nonzero mod p
        R = aff_add(R, Pt, a, m)
    x1, y1 = R; x2, y2 = Pt
    N = (y2 - y1) % m; D = (x2 - x1) % m   # D = p*d
    assert D % p == 0 and N % p != 0
    d = D // p
    A = (N*N - (x1 + x2)*D*D) % m
    B = (N*(x1*D*D - A) - y1*D**3) % m
    assert B % p != 0
    return (-A * d * pow(B, -1, p)) % p

def hom_zero_control(a, b, p, n, rng, trials=20):
    """non-anomalous: map P -> psi-like value of [n]P~ ; should be 0 for all P (hom from order-n group to Z/p)."""
    m = p*p; vals = []
    for _ in range(trials):
        while True:
            x = rng.randrange(p); r = (x**3 + a*x + b) % p
            ys = [y for y in range(p) if y*y % p == r] if r else []
            if ys: break
        Pt = lift_point((x, ys[0]), a, b, p)
        R = None
        for _ in range(n-1): R = aff_add(R, Pt, a, m)
        x1, y1 = R; x2, y2 = Pt
        if x1 % p == x2 % p and (y1 + y2) % p == 0:
            N = (y2-y1) % m; D = (x2-x1) % m
            d = D // p
            A = (N*N - (x1+x2)*D*D) % m
            B = (N*(x1*D*D - A) - y1*D**3) % m
            vals.append((-A*d*pow(B, -1, p)) % p)
    return vals

if __name__ == "__main__":
    rng = random.Random(20261103)
    # anomalous search
    found = None
    while not found:
        p = rng.choice([q for q in range(500, 3000) if is_prime(q)])
        a, b = rng.randrange(p), rng.randrange(p)
        if (4*a**3 + 27*b*b) % p == 0: continue
        if count_points(a, b, p) == p: found = (p, a, b)
    p, a, b = found; m = p*p
    print("anomalous curve y^2=x^3+%dx+%d over F_%d, #E=p" % (a, b, p))
    def rpt():
        while True:
            x = rng.randrange(p); r = (x**3 + a*x + b) % p
            ys = [y for y in range(1, p) if y*y % p == r] if r else []
            if ys: return (x, ys[0])
    P = rpt(); ok = 0; T = 20
    for _ in range(T):
        k = rng.randrange(1, p)
        # Q = kP in F_p (affine)
        R = None
        for _ in range(k): R = aff_add(R, P, a, p)
        Pt, Qt = lift_point(P, a, b, p), lift_point(R, a, b, p)
        psiP, psiQ = smart_psi(Pt, a, p), smart_psi(Qt, a, p)
        k_rec = psiQ * pow(psiP, -1, p) % p
        ok += (k_rec == k)
    print("Smart recovery: %d/%d correct (k recovered in O(p) field ops here; polynomial in log p with double-and-add)" % (ok, T))
    # negative control
    rng2 = random.Random(7)
    while True:
        q = rng2.choice([r for r in range(100, 400) if is_prime(r)])
        a2, b2 = rng2.randrange(q), rng2.randrange(q)
        if (4*a2**3 + 27*b2*b2) % q == 0: continue
        n = count_points(a2, b2, q)
        if n != q and is_prime(n): break
    vals = hom_zero_control(a2, b2, q, n, rng2)
    print("control non-anomalous p=%d #E=%d: values of psi([#E]P~)/p over %d random P:" % (q, n, len(vals)), set(vals))
