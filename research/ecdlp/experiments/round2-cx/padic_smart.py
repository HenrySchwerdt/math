"""Shared p-adic (Z/p^N) elliptic-curve arithmetic for H4: Bosma-Lenstra/Renes-Costello-Batina projective addition
(a,b general), Hensel point lifting, and psi(P~) = (-x/y)([#E]P~)/p mod p  (computed as -X/Y, no inversion of Z).
Addition law is valid (no exceptional pair) whenever the reduction mod p of both points lies in E(F_p) of ODD order
(no F_p-point of order 2); we assert/restrict accordingly, and self-test against affine toyec arithmetic."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
from toyec import Curve, is_prime

class PCurve:
    def __init__(self, a, b, p, N=3):
        self.a, self.b, self.p, self.N, self.m = a, b, p, N, p ** N
    def add(self, P, Q):
        a, b, m = self.a, self.b, self.m
        X1, Y1, Z1 = P; X2, Y2, Z2 = Q
        b3 = 3 * b
        A = (Y1 * Y2 - a * (X1 * Z2 + X2 * Z1) - b3 * Z1 * Z2)
        B = (Y1 * Y2 + a * (X1 * Z2 + X2 * Z1) + b3 * Z1 * Z2)
        C = (a * X1 * X2 + b3 * (X1 * Z2 + X2 * Z1) - a * a * Z1 * Z2)
        X3 = (X1 * Y2 + X2 * Y1) * A - (Y1 * Z2 + Y2 * Z1) * C
        Y3 = B * A + (3 * X1 * X2 + a * Z1 * Z2) * C
        Z3 = (Y1 * Z2 + Y2 * Z1) * B + (X1 * Y2 + X2 * Y1) * (3 * X1 * X2 + a * Z1 * Z2)
        return (X3 % m, Y3 % m, Z3 % m)
    INF = (0, 1, 0)
    def mul(self, k, P):
        R = self.INF
        while k:
            if k & 1: R = self.add(R, P)
            P = self.add(P, P); k >>= 1
        return R
    def neg(self, P): return (P[0], (-P[1]) % self.m, P[2])
    def lift(self, pt, u):
        """lift affine (x,y) mod p, y != 0, to x~ = x + p*u, y~ by Newton/Hensel"""
        p, m = self.p, self.m
        x, y = pt
        xt = (x + p * u) % m
        f = (xt ** 3 + self.a * xt + self.b) % m
        yt = y
        for _ in range(self.N + 1):
            yt = (yt - (yt * yt - f) * pow(2 * yt, -1, m)) % m
        assert (yt * yt - f) % m == 0 and yt % p == y % p
        return (xt, yt, 1)
    def teich_lift(self, pt):
        p, m = self.p, self.m
        x, y = pt
        xt = pow(x, p ** (self.N - 1), m)   # Teichmuller representative of x
        f = (xt ** 3 + self.a * xt + self.b) % m
        yt = y
        for _ in range(self.N + 1):
            yt = (yt - (yt * yt - f) * pow(2 * yt, -1, m)) % m
        return (xt, yt, 1)
    def psi(self, P, nE):
        X, Y, Z = self.mul(nE, P)
        p = self.p
        assert X % p == 0 and Z % p == 0 and Y % p != 0, 'reduction of [#E]P~ is not O'
        z = (-X * pow(Y, -1, self.m)) % (p * p)
        assert z % p == 0
        return (z // p) % p

def all_curves(p, odd_only=True, anomalous=None):
    """yield (a,b,Ecurve,#E) for all nonsingular (a,b)"""
    for a in range(p):
        for b in range(p):
            if (4 * a ** 3 + 27 * b * b) % p == 0: continue
            E = Curve(a, b, p); n = E.order()
            yield a, b, E, n

def prime_factors(n):
    f, d = [], 2
    while d * d <= n:
        if n % d == 0:
            f.append(d)
            while n % d == 0: n //= d
        d += 1
    if n > 1: f.append(n)
    return f

def selftest():
    rnd = random.Random(7)
    for p in (101, 103, 107):
        for _ in range(20):
            a, b = rnd.randrange(p), rnd.randrange(p)
            if (4 * a ** 3 + 27 * b * b) % p == 0: continue
            E = Curve(a, b, p); n = E.order()
            if n % 2 == 0: continue
            pts = [q for q in E.points() if q is not None and q[1] != 0]
            Ec = PCurve(a, b, p)
            for _ in range(15):
                P, Q = rnd.choice(pts), rnd.choice(pts)
                S = E.add(P, Q)
                lp, lq = Ec.lift(P, rnd.randrange(p * p)), Ec.lift(Q, rnd.randrange(p * p))
                R = Ec.add(lp, lq)
                if S is None:
                    assert R[0] % p == 0 and R[2] % p == 0
                else:
                    assert R[2] % p != 0 and R[0] * pow(R[2], -1, p) % p == S[0] and R[1] * pow(R[2], -1, p) % p == S[1]
            # associativity / homomorphism on E(Z/p^3)
            A_, B_, C_ = (Ec.lift(rnd.choice(pts), rnd.randrange(p * p)) for _ in range(3))
            def eq(U, V): return all((U[i] * V[j] - U[j] * V[i]) % Ec.m == 0 for i in range(3) for j in range(3))
            assert eq(Ec.add(Ec.add(A_, B_), C_), Ec.add(A_, Ec.add(B_, C_)))
    print('selftest OK (RCB addition agrees with affine toyec mod p, associative mod p^3, curves with odd #E)')

if __name__ == '__main__':
    selftest()

def sample_curves(p, pred, count, rnd, tries=200000):
    """random (a,b) with predicate pred(n) on #E; returns list of (a,b,E,n) (distinct)"""
    out, seen = [], set()
    for _ in range(tries):
        a, b = rnd.randrange(p), rnd.randrange(p)
        if (a, b) in seen or (4 * a ** 3 + 27 * b * b) % p == 0: continue
        seen.add((a, b))
        E = Curve(a, b, p); n = E.order()
        if pred(n): out.append((a, b, E, n))
        if len(out) >= count: break
    return out
