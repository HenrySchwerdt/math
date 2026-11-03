"""Readable reference arithmetic for toy short-Weierstrass curves y^2 = x^3 + a x + b over F_p.

Synthetic research use only (p small). Points are (x, y) tuples or None for infinity.
Correctness is cross-checked by tests/test_toyec.py (group axioms, Hasse bound,
brute-force vs baby-step giant-step discrete logarithms). Not constant time; not optimized.
"""
from math import isqrt


def is_prime(n):
    if n < 2:
        return False
    for q in range(2, isqrt(n) + 1):
        if n % q == 0:
            return False
    return True


class Curve:
    def __init__(self, a, b, p):
        if not is_prime(p) or p < 5:
            raise ValueError('p must be a prime >= 5')
        if (4 * a ** 3 + 27 * b ** 2) % p == 0:
            raise ValueError('singular curve')
        self.a, self.b, self.p = a % p, b % p, p

    def on_curve(self, P):
        if P is None:
            return True
        x, y = P
        return (y * y - (x ** 3 + self.a * x + self.b)) % self.p == 0

    def neg(self, P):
        return None if P is None else (P[0], (-P[1]) % self.p)

    def add(self, P, Q):
        p = self.p
        if P is None:
            return Q
        if Q is None:
            return P
        if P[0] == Q[0] and (P[1] + Q[1]) % p == 0:
            return None
        if P == Q:
            lam = (3 * P[0] * P[0] + self.a) * pow(2 * P[1], -1, p) % p
        else:
            lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
        x3 = (lam * lam - P[0] - Q[0]) % p
        return (x3, (lam * (P[0] - x3) - P[1]) % p)

    def mul(self, k, P):
        if k < 0:
            return self.mul(-k, self.neg(P))
        R = None
        while k:
            if k & 1:
                R = self.add(R, P)
            P = self.add(P, P)
            k >>= 1
        return R

    def points(self):
        p = self.p
        sq = {}
        for y in range(p):
            sq.setdefault(y * y % p, []).append(y)
        pts = [None]
        for x in range(p):
            for y in sq.get((x ** 3 + self.a * x + self.b) % p, []):
                pts.append((x, y))
        return pts

    def order(self):
        return len(self.points())

    def point_order(self, P, n=None):
        n = n or self.order()
        for d in sorted(d for d in range(1, n + 1) if n % d == 0):
            if self.mul(d, P) is None:
                return d
        raise AssertionError('Lagrange violated')


def dlog_bruteforce(E, P, Q):
    R, k = None, 0
    while True:
        if R == Q:
            return k
        R, k = E.add(R, P), k + 1
        if R is None and Q is not None and k > 0:
            return None


def dlog_bsgs(E, P, Q, n):
    m = isqrt(n) + 1
    table, R = {}, None
    for j in range(m):
        table.setdefault(R, j)
        R = E.add(R, P)
    step, G = E.neg(E.mul(m, P)), Q
    for i in range(m + 1):
        if G in table:
            return (i * m + table[G]) % n
        G = E.add(G, step)
    return None
