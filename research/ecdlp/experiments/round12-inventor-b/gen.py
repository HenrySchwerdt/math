import random
from math import isqrt
from ecinv import *

def two_squares(p, c):   # p = x^2 + c y^2
    for y in range(1, isqrt(p//c) + 1):
        x2 = p - c*y*y; x = isqrt(x2)
        if x*x == x2: return x, y
    return None

def cm_curve(kind, bits, rng, maxcof=16):
    """j=0 / j=1728 curve over a prime p ~ 2^bits with a point of prime order r (cofactor <= maxcof)."""
    while True:
        p = rng.randrange(1 << (bits-1), 1 << bits) | 1
        if not is_prime(p): continue
        if kind == 'j0':
            if p % 3 != 1: continue
            xy = two_squares(p, 3)
            if not xy: continue
            x, y = xy; traces = [2*x, -2*x, x+3*y, -(x+3*y), x-3*y, -(x-3*y)]
        else:
            if p % 4 != 1: continue
            xy = two_squares(p, 1)
            if not xy: continue
            x, y = xy; traces = [2*x, -2*x, 2*y, -2*y]
        rng.shuffle(traces)
        for t in traces:
            n = p + 1 - t
            for cof in range(1, maxcof+1):
                if n % cof == 0 and is_prime(n//cof) and n//cof > (1 << (bits-5)):
                    r = n//cof
                    for _ in range(400):
                        b = rng.randrange(1, p)
                        E = Curve(0, b, p) if kind == 'j0' else Curve(b, 0, p)
                        # random point
                        while True:
                            X = rng.randrange(p); rhs = (X**3 + E.a*X + E.b) % p
                            if pow(rhs, (p-1)//2, p) == 1:
                                # sqrt via Tonelli-lite for p%4==3 else Cipolla; use simple Tonelli
                                Y = sqrt_mod(rhs, p); break
                        C = Counter()
                        T = emul(n, (X, Y), E.a, p, C)
                        if T is not None: continue   # wrong twist
                        P = emul(cof, (X, Y), E.a, p, C)
                        if P is None: continue
                        if emul(r, P, E.a, p, C) is not None: continue
                        return E, P, r, dict(p=p, n=n, cof=cof, t=t)
                    break

def sqrt_mod(a, p):
    if p % 4 == 3: return pow(a, (p+1)//4, p)
    q, s = p-1, 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while pow(z, (p-1)//2, p) != p-1: z += 1
    m, c, t, rr = s, pow(z, q, p), pow(a, q, p), pow(a, (q+1)//2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1: t2 = t2*t2 % p; i += 1
        b = pow(c, 1 << (m-i-1), p); m = i; c = b*b % p; t = t*c % p; rr = rr*b % p
    return rr
