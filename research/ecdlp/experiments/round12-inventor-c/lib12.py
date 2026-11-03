"""Round-12 inventor C: counted-operation collision algorithms on toy prime-order curves.
Group-operation counter: every point addition or doubling = 1 op (field inversions not separately counted;
each affine op = 1 inversion + ~3 mults, same for all algorithms). Scalar tag arithmetic is free.
"""
import random, sys, os
from math import isqrt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
from toyec import Curve, dlog_bsgs

R_PARTS = 31  # partition count (odd => independent of power-of-two DP mask)

def is_prime(n):
    if n < 2: return False
    for q in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % q == 0: return n == q
    d, s = n-1, 0
    while d % 2 == 0: d//=2; s+=1
    for a in (2,3,5,7,11,13,17,19,23,29,31,37):
        x = pow(a,d,n)
        if x in (1,n-1): continue
        for _ in range(s-1):
            x = x*x % n
            if x == n-1: break
        else: return False
    return True

class Ops:
    """Affine arithmetic with op counter."""
    def __init__(self, p, a):
        self.p, self.a, self.count = p, a, 0
    def add(self, P, Q):
        self.count += 1
        p = self.p
        if P is None: return Q
        if Q is None: return P
        x1,y1 = P; x2,y2 = Q
        if x1 == x2:
            if (y1+y2) % p == 0: return None
            lam = (3*x1*x1 + self.a) * pow(2*y1, -1, p) % p
        else:
            lam = (y2-y1) * pow(x2-x1, -1, p) % p
        x3 = (lam*lam - x1 - x2) % p
        return (x3, (lam*(x1-x3) - y1) % p)
    def mul(self, k, P):
        R = None
        while k:
            if k & 1: R = self.add(R, P)
            k >>= 1
            if k: P = self.add(P, P)
        return R

def _on(E, P):
    return E.on_curve(P)

def order_of_point(E, P, rng):
    """BSGS in the Hasse interval: returns M if M is the unique multiple of ord(P) in the interval and
    M prime (then #E = M and E(F_p) has prime order)."""
    p = E.p
    lo, hi = p+1-2*isqrt(p)-2, p+1+2*isqrt(p)+2
    m = isqrt(hi-lo)+1
    # baby steps jP, 0<=j<m ; giant: (lo + i*m)P ... find lo+i*m+j' with  (lo+i m)P = -j'P
    tab = {}
    R = None
    for j in range(m):
        tab.setdefault(R, []).append(j)
        R = E.add(R, P)
    G = E.mul(lo, P); step = E.mul(m, P)
    found = []
    for i in range(m+1):
        for j in tab.get(E.neg(G), []):
            M = lo + i*m + j
            if lo <= M <= hi: found.append(M)
        G = E.add(G, step)
    return found

def find_prime_order_curve(bits, seed):
    """Deterministic search: prime p with ~`bits` bits, random (a,b); require #E prime with #E = r > 4 sqrt p.
    Returns (Curve, P, r) with P a generator."""
    rng = random.Random(f'curve-{bits}-{seed}')
    while True:
        p = rng.randrange(1 << (bits-1), 1 << bits) | 1
        if not is_prime(p) or p < 7: continue
        a, b = rng.randrange(p), rng.randrange(p)
        try: E = Curve(a, b, p)
        except ValueError: continue
        # random point
        while True:
            x = rng.randrange(p); rhs = (x**3 + a*x + b) % p
            if rhs == 0: continue
            if pow(rhs, (p-1)//2, p) == 1:
                # p%4==3 shortcut else Tonelli (small): use brute sqrt via pow if p%4==3
                if p % 4 == 3: y = pow(rhs, (p+1)//4, p)
                else:
                    y = _sqrt(rhs, p)
                P = (x, y); break
        M = order_of_point(E, P, rng)
        if len(M) == 1 and is_prime(M[0]) and M[0] > 4*isqrt(p)+4 and E.mul(M[0], P) is None:
            return E, P, M[0]

def _sqrt(a, p):
    # Tonelli-Shanks
    q, s = p-1, 0
    while q % 2 == 0: q//=2; s+=1
    z = 2
    while pow(z, (p-1)//2, p) != p-1: z += 1
    c, t, r, m = pow(z,q,p), pow(a,q,p), pow(a,(q+1)//2,p), s
    while t != 1:
        i, t2 = 0, t
        while t2 != 1: t2 = t2*t2 % p; i += 1
        b = pow(c, 1 << (m-i-1), p)
        r, c = r*b % p, b*b % p
        t, m = t*c % p, i
    return r

def dp_mask_for(L):
    k = max(1, round(L).bit_length()-1)   # power of two <= L
    return (1 << k) - 1
