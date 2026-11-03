# Frobenius-structure test for g=y (and x): twisted sums over F_{p^n}, n=1,2,3, with psi o Tr_{F_{p^n}/F_p}.
# Prediction (derivation, conjecture): eigenvalues of Frob on H^1 (dim 4) are {a*l_i, b*l_i}, b/a a primitive cube root of 1
# => S3 = A^3 - 3 A B with A=zeta*S1, B=conj(zeta)*S2 (zeta = exp(+-2 pi i/3)), and |A^2-B|/2 = p.
import sys, random, cmath, math, json
import numpy as np
from common import *
SEED = 20261105
rng = random.Random(SEED)

class Fq:
    def __init__(self, p, n):
        self.p, self.n, self.q = p, n, p**n
        while True:
            self.poly = [rng.randrange(p) for _ in range(n)]   # x^n = -sum poly[i] x^i  (monic x^n + ...)
            if self.poly[0] == 0: continue
            if self._build(): break
    def _build(self):
        p, n, q = self.p, self.n, self.q
        cur = [0]*n; cur[0] = 1
        exp = []; seen = 0
        for i in range(q-1):
            v = 0
            for d in reversed(cur): v = v*p + d
            if i and v == 1: return False
            if v == 0: return False
            exp.append(v)
            top = cur[-1]; cur = [0] + cur[:-1]
            if top:
                cur = [(c - top*self.poly[j]) % p for j, c in enumerate(cur)]
        if len(set(exp)) != q-1: return False
        self.exp = exp; self.log = {v: i for i, v in enumerate(exp)}
        return True
    def digits(self, v):
        d = []
        for _ in range(self.n): v, m = divmod(v, self.p); d.append(m)
        return d
    def add(self, u, v):
        if self.n == 1: return (u+v) % self.p
        du, dv = self.digits(u), self.digits(v); r = 0
        for a, b in reversed(list(zip(du, dv))): r = r*self.p + (a+b) % self.p
        return r
    def neg(self, u):
        r = 0
        for a in reversed(self.digits(u)): r = r*self.p + (-a) % self.p
        return r
    def mul(self, u, v):
        if u == 0 or v == 0: return 0
        return self.exp[(self.log[u] + self.log[v]) % (self.q-1)]
    def inv(self, u): return self.exp[(-self.log[u]) % (self.q-1)]
    def frob(self, u):
        return 0 if u == 0 else self.exp[(self.log[u]*self.p) % (self.q-1)]
    def const(self, c): return c % self.p
    def chi(self, u):
        return 0 if u == 0 else (1 if self.log[u] % 2 == 0 else -1)

def ec_add(F, a, P, Q):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0]:
        if F.add(P[1], Q[1]) == 0: return None
        num = F.add(F.mul(F.const(3), F.mul(P[0], P[0])), F.const(a)); den = F.mul(F.const(2), P[1])
    else:
        num = F.add(Q[1], F.neg(P[1])); den = F.add(Q[0], F.neg(P[0]))
    lam = F.mul(num, F.inv(den))
    x3 = F.add(F.mul(lam, lam), F.neg(F.add(P[0], Q[0])))
    y3 = F.add(F.mul(lam, F.add(P[0], F.neg(x3))), F.neg(P[1]))
    return (x3, y3)

def run_curve(p, a, b, r, ns=(1, 2, 3)):
    E = Curve(a, b, p); P0 = None
    pts = orbit(E, r)
    dlog = {Q: k for k, Q in enumerate(pts)}
    out = {}
    for n in ns:
        F = Fq(p, n); q = F.q
        sq = {}
        for u in range(q): sq.setdefault(F.mul(u, u), []).append(u)
        Ny = np.zeros(r); Nx = np.zeros(r)
        for x in range(q):
            x3 = F.mul(x, F.mul(x, x))
            rhs = F.add(F.add(x3, F.mul(F.const(a), x)), F.const(b))
            for y in sq.get(rhs, []):
                Q = (x, y); T = None; Z = Q
                for _ in range(n):
                    T = ec_add(F, a, T, Z); Z = (F.frob(Z[0]), F.frob(Z[1]))
                if T is None: k = 0
                else:
                    assert T[0] < p and T[1] < p
                    k = dlog[T]
                Ny[k] += F.chi(y); Nx[k] += F.chi(x)
        out[n] = (np.fft.fft(Ny)[1:], np.fft.fft(Nx)[1:])
    return out

if __name__ == '__main__':
    rows = []
    for p in [11, 13, 17, 19, 23, 29, 31, 37]:
        L = legendre_table(p)
        for _ in range(3):
            res = random_prime_order_curve(p, rng, L)
            if not res or res[2] < 5: continue
            a, b, r = res
            out = run_curve(p, a, b, r)
            for gi, g in enumerate(['y', 'x']):
                S1, S2, S3 = (out[n][gi] for n in (1, 2, 3))
                best = None
                for z in (cmath.exp(2j*math.pi/3), cmath.exp(-2j*math.pi/3)):
                    A = z*S1; B = z.conjugate()*S2
                    res3 = np.abs(S3 - (A**3 - 3*A*B)) / p**1.5
                    wt = np.abs(np.abs(A*A - B)/2 - p) / p
                    cand = (float(np.median(res3)), float(res3.max()), float(wt.max()))
                    if best is None or cand[1] < best[1]: best = cand
                rows.append(dict(g=g, p=p, a=a, b=b, r=r, struct_resid_median=round(best[0], 6), struct_resid_max=round(best[1], 6),
                                 weight_dev_max=round(best[2], 6), typical_S3_over_p15=round(float(np.mean(np.abs(S3)))/p**1.5, 4),
                                 max_S1_over_sqrtp=round(float(np.abs(S1).max())/p**0.5, 4)))
    for rw in rows: print(json.dumps(rw))
