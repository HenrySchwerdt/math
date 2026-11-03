"""F1 (candidate a): relations among base points {P in E(F_{p^2}) : x(P) in S}, S subset F_p.
Claim: V = E(F_p)-type U twist-type; closed triples are only EEE and TTT (direct product).
Seeded, deterministic. Usage: f1_fp2_split.py p_lo seed s_factor"""
import sys, random
from math import isqrt
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from toyec import Curve, is_prime

def run(p, seed, sf):
    rng = random.Random(seed)
    while True:
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        if (4*a**3 + 27*b*b) % p == 0: continue
        E = Curve(a, b, p)
        n = E.order()
        if is_prime(n) and n != p: break
    nr = next(z for z in range(2, p) if pow(z, (p-1)//2, p) == p-1)
    # F_{p^2} element = (u,v) = u + v*i, i^2 = nr
    def mul(A, B): return ((A[0]*B[0] + nr*A[1]*B[1]) % p, (A[0]*B[1] + A[1]*B[0]) % p)
    def sub(A, B): return ((A[0]-B[0]) % p, (A[1]-B[1]) % p)
    def inv(A):
        d = pow((A[0]*A[0] - nr*A[1]*A[1]) % p, -1, p)
        return (A[0]*d % p, (-A[1])*d % p)
    def add(P, Q):
        if P is None: return Q
        if Q is None: return P
        if P[0] == Q[0]:
            if ((P[1][0]+Q[1][0]) % p, (P[1][1]+Q[1][1]) % p) == (0, 0): return None
            num = ((3*mul(P[0], P[0])[0] + a) % p, 3*mul(P[0], P[0])[1] % p)
            lam = mul(num, inv(((2*P[1][0]) % p, (2*P[1][1]) % p)))
        else:
            lam = mul(sub(Q[1], P[1]), inv(sub(Q[0], P[0])))
        l2 = mul(lam, lam)
        x3 = sub(sub(l2, P[0]), Q[0])
        y3 = sub(mul(lam, sub(P[0], x3)), P[1])
        return (x3, y3)
    sqrt1 = {}
    for y in range(p): sqrt1.setdefault(y*y % p, y)
    s = max(8, int(sf*isqrt(p)))
    S = rng.sample(range(p), s)
    Sset = set(S)
    V, typ = [], []
    for x in S:
        fx = (x**3 + a*x + b) % p
        if fx == 0: continue
        if fx in sqrt1:
            y = sqrt1[fx]; t = 'E'; Y = (y, 0)
        else:
            # y = t*i, t^2*nr = fx
            t2 = fx * pow(nr, -1, p) % p
            t = sqrt1[t2]; Y = (0, t); typ_ = 'T'; t = 'T'
        for sg in (1, -1):
            V.append(((x, 0), ((sg*Y[0]) % p, (sg*Y[1]) % p))); typ.append(t)
    idx = {v: k for k, v in enumerate(V)}
    cnt = {}
    for i, P in enumerate(V):
        for j in range(i, len(V)):
            Q = V[j]
            R = add(P, Q)
            if R is None: continue
            nR = (R[0], ((-R[1][0]) % p, (-R[1][1]) % p))
            if nR in idx:   # P+Q = -(third) with third in V
                k = idx[nR]
                key = ''.join(sorted(typ[i] + typ[j] + typ[k]))
                cnt[key] = cnt.get(key, 0) + 1
    nE, nT = typ.count('E')//2, typ.count('T')//2
    tw = p + 1 + (p + 1 - n)  # #E^tw = 2(p+1) - #E
    return dict(p=p, order=n, twist_order=2*(p+1)-n, order_Fp2=n*(2*(p+1)-n), s=s,
                nE_x=nE, nT_x=nT, closed=cnt)

if __name__ == '__main__':
    p0, seed, sf = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    p = p0
    while not is_prime(p): p += 1
    print(run(p, seed, sf))
