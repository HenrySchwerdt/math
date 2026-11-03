"""Genus-2 hyperelliptic Jacobian arithmetic for y^2 = F(w), F monic of degree 6 over F_p.

Even-degree ("real") model: two rational points infty+ and infty- at infinity, K = infty+ + infty-.
Class of  D - K  with D effective, deg 2, finite support  <->  Mumford pair (u, v), u monic deg 2,
deg v <= 1, u | F - v^2.  Identity = None.  Classes whose representative involves infinity raise
Degenerate (probability O(1/p) for random elements); callers skip/retry.
Polynomials: tuples of ints mod p, low degree first, no trailing zeros ((): zero polynomial).
Synthetic research code, not constant time.
"""

OPS = {'cantor': 0}


class Degenerate(Exception):
    pass


def trim(a):
    a = list(a)
    while a and a[-1] == 0:
        a.pop()
    return tuple(a)


def padd(a, b, p):
    n = max(len(a), len(b))
    return trim([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p for i in range(n)])


def psub(a, b, p):
    n = max(len(a), len(b))
    return trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p for i in range(n)])


def pmul(a, b, p):
    if not a or not b:
        return ()
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] += x * y
    return trim([c % p for c in r])


def pscal(a, s, p):
    return trim([(c * s) % p for c in a])


def pdivmod(a, b, p):
    """Quotient and remainder of a by b (b != 0)."""
    a = list(a)
    db = len(b) - 1
    inv = pow(b[-1], -1, p)
    q = [0] * max(len(a) - db, 0)
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i] * inv % p
        if c:
            q[i - db] = c
            for j in range(db + 1):
                a[i - db + j] = (a[i - db + j] - c * b[j]) % p
    return trim(q), trim(a[:db])


def pmod(a, b, p):
    return pdivmod(a, b, p)[1]


def monic(a, p):
    if not a:
        return a
    return pscal(a, pow(a[-1], -1, p), p)


def xgcd(a, b, p):
    """(g, s, t) with g = s a + t b, g monic."""
    r0, r1 = a, b
    s0, s1 = (1,), ()
    t0, t1 = (), (1,)
    while r1:
        q, r = pdivmod(r0, r1, p)
        r0, r1 = r1, r
        s0, s1 = s1, psub(s0, pmul(q, s1, p), p)
        t0, t1 = t1, psub(t0, pmul(q, t1, p), p)
    if not r0:
        return (), (), ()
    inv = pow(r0[-1], -1, p)
    return pscal(r0, inv, p), pscal(s0, inv, p), pscal(t0, inv, p)


class Genus2:
    def __init__(self, F, p):
        assert len(F) == 7 and F[6] == 1
        self.F, self.p = tuple(F), p

    # ---- elements ----
    def neg(self, D):
        if D is None:
            return None
        u, v = D
        return (u, trim([(-c) % self.p for c in v]))

    def is_valid(self, D):
        if D is None:
            return True
        u, v = D
        return (len(u) == 3 and u[-1] == 1 and len(v) <= 2 and
                pmod(psub(self.F, pmul(v, v, self.p), self.p), u, self.p) == ())

    def pair(self, P1, P2):
        """Class of P1+P2-K for finite points with distinct w (interpolation)."""
        p = self.p
        (w1, y1), (w2, y2) = P1, P2
        if w1 == w2:
            raise Degenerate('same w')
        u = pmul((-w1 % p, 1), (-w2 % p, 1), p)
        sl = (y2 - y1) * pow(w2 - w1, -1, p) % p
        v = trim([(y1 - sl * w1) % p, sl])
        return (u, v)

    def fibre(self, x, y, c):
        """pi^*(Q) for Q = (x, y) != O."""
        u = trim([(c - x) % self.p, 0, 1])
        return (u, trim([y % self.p]))

    # ---- group law ----
    def add(self, D1, D2):
        if D1 is None:
            return D2
        if D2 is None:
            return D1
        OPS['cantor'] += 1
        p, F = self.p, self.F
        u1, v1 = D1
        u2, v2 = D2
        d1, e1, e2 = xgcd(u1, u2, p)
        vs = padd(v1, v2, p)
        if len(d1) == 1:                      # gcd(u1,u2)=1: d = 1, s1,s2 = e1,e2, s3 = 0
            d, s1, s2, s3 = (1,), e1, e2, ()
        else:
            d, c1, c2 = xgcd(d1, vs, p)
            s1, s2, s3 = pmul(c1, e1, p), pmul(c1, e2, p), c2
        if len(d) == 3:
            return None  # D1 + D2 ~ 2K  (u1 = u2, v2 = -v1)
        if len(d) == 1:
            u = pmul(u1, u2, p)
            num = padd(padd(pmul(pmul(s1, u1, p), v2, p), pmul(pmul(s2, u2, p), v1, p), p),
                       pmul(s3, padd(pmul(v1, v2, p), F, p), p), p)
            v = pmod(num, u, p)
        else:
            d2 = pmul(d, d, p)
            u, r0 = pdivmod(pmul(u1, u2, p), d2, p)
            assert r0 == ()
            num = padd(padd(pmul(pmul(s1, u1, p), v2, p), pmul(pmul(s2, u2, p), v1, p), p),
                       pmul(s3, padd(pmul(v1, v2, p), F, p), p), p)
            q, r0 = pdivmod(num, d, p)
            assert r0 == ()
            v = pmod(q, u, p)
        # u monic of degree 4 - 2 deg d
        if len(u) == 3:                       # deg d = 1: already the answer
            return (u, v)
        # deg u = 4: one reduction step, answer = iota of residual divisor
        t = psub(F, pmul(v, v, p), p)
        up, r0 = pdivmod(t, u, p)
        assert r0 == ()
        if len(up) != 3:
            raise Degenerate('infinite point in result')
        up = monic(up, p)
        vp = pmod(pscal(v, p - 1, p), up, p)
        return (up, vp)

    def mul(self, k, D):
        if k < 0:
            return self.mul(-k, self.neg(D))
        R = None
        while k:
            if k & 1:
                R = self.add(R, D)
            k >>= 1
            if k:
                D = self.add(D, D)
        return R
