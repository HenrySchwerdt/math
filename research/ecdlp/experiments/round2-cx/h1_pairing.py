"""H1 attack: toy embedding-degree-2 curves; Weil and reduced Tate pairings over F_{p^2} = F_p[i]/(i^2+1), p = 3 mod 4.
Checks which functionals f(x)=e(x,R) are equivariant for the p-power Frobenius pi in two senses:
  (G) Galois-equivariant: f(pi x) = f(x)^p      (the 'c = q' reading: target mu_r with Frobenius acting by q-th power)
  (T) eigen-equivariant: f(pi x) = f(x)^c for the scalar c given by the adjoint eigenvalue (target action ignored).
Seeded, stdlib only.  Usage: python3 h1_pairing.py"""
import random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
from toyec import Curve, is_prime

class F2:
    """F_{p^2}, element (a,b)=a+b i, i^2=-1"""
    p = None
    def __init__(s, a, b=0): s.a, s.b = a % F2.p, b % F2.p
    def __add__(s, o): return F2(s.a + o.a, s.b + o.b)
    def __sub__(s, o): return F2(s.a - o.a, s.b - o.b)
    def __neg__(s): return F2(-s.a, -s.b)
    def __mul__(s, o):
        if isinstance(o, int): return F2(s.a * o, s.b * o)
        return F2(s.a * o.a - s.b * o.b, s.a * o.b + s.b * o.a)
    def inv(s):
        n = pow(s.a * s.a + s.b * s.b, -1, F2.p); return F2(s.a * n, -s.b * n)
    def __truediv__(s, o): return s * o.inv()
    def __eq__(s, o): return s.a == o.a and s.b == o.b
    def __hash__(s): return hash((s.a, s.b))
    def __pow__(s, e):
        r, x = F2(1), s
        while e:
            if e & 1: r = r * x
            x = x * x; e >>= 1
        return r
    def iszero(s): return s.a == 0 and s.b == 0
    def __repr__(s): return f'({s.a}+{s.b}i)'
    def frob(s): return F2(s.a, -s.b)       # x -> x^p
ONE = None

class EC2:
    def __init__(s, a, b): s.a, s.b = F2(a), F2(b)
    def add(s, P, Q):
        if P is None: return Q
        if Q is None: return P
        if P[0] == Q[0] and (P[1] + Q[1]).iszero(): return None
        if P == Q: lam = (P[0] * P[0] * 3 + s.a) / (P[1] * 2)
        else: lam = (Q[1] - P[1]) / (Q[0] - P[0])
        x3 = lam * lam - P[0] - Q[0]
        return (x3, lam * (P[0] - x3) - P[1])
    def neg(s, P): return None if P is None else (P[0], -P[1])
    def mul(s, k, P):
        if k < 0: return s.mul(-k, s.neg(P))
        R = None
        while k:
            if k & 1: R = s.add(R, P)
            P = s.add(P, P); k >>= 1
        return R
    def frob(s, P): return None if P is None else (P[0].frob(), P[1].frob())
    def sqrt_point(s, x):
        rhs = x * x * x + s.a * x + s.b
        # sqrt in F_{p^2}: p = 3 mod 4 -> use Tonelli-free formula for q=p^2 = 1 mod 8? do generic: try y = rhs^((p^2+3)/8)... use brute: Cipolla-free: exponent (q+1)/4 invalid. use random search over y via Euler + Tonelli
        q = F2.p ** 2
        if rhs.iszero(): return F2(0)
        if rhs ** ((q - 1) // 2) != F2(1): return None
        # Tonelli-Shanks in F_q
        Q, S = q - 1, 0
        while Q % 2 == 0: Q //= 2; S += 1
        z = F2(2, 1)
        while z ** ((q - 1) // 2) == F2(1): z = F2(random.randrange(F2.p), random.randrange(F2.p))
        M, c, t, R = S, z ** Q, rhs ** Q, rhs ** ((Q + 1) // 2)
        while t != F2(1):
            i, t2 = 0, t
            while t2 != F2(1): t2 = t2 * t2; i += 1
            b = c
            for _ in range(M - i - 1): b = b * b
            M, c, t, R = i, b * b, t * b * b, R * b
        return R

def miller(E, P, Q, r):
    """f_{r,P}(Q) (full rational function incl. vertical lines), P of order r, Q not in <P>, Q != O"""
    f, T = F2(1), P
    xq, yq = Q
    for bit in bin(r)[3:]:
        # doubling
        lam = (T[0] * T[0] * 3 + E.a) / (T[1] * 2)
        x3 = lam * lam - T[0] * 2
        num = yq - T[1] - lam * (xq - T[0])
        den = xq - x3
        f = f * f * num / den
        T = E.add(T, T)
        if bit == '1':
            if T[0] == P[0]:      # T = -P at the last step: vertical line
                f = f * (xq - P[0]); T = None; continue
            lam = (P[1] - T[1]) / (P[0] - T[0])
            x3 = lam * lam - T[0] - P[0]
            num = yq - T[1] - lam * (xq - T[0]); den = xq - x3
            f = f * num / den
            T = E.add(T, P)
    return f

def weil(E, P, Q, r):
    return ((-1) ** r * 1) and (miller(E, P, Q, r) / miller(E, Q, P, r)) * (F2(1) if r % 2 == 0 else F2(-1)).__mul__(F2(1)) if False else _weil(E, P, Q, r)
def _weil(E, P, Q, r):
    s = F2(-1) if r % 2 == 1 else F2(1)
    return s * miller(E, P, Q, r) / miller(E, Q, P, r)
def tate(E, P, Q, r, p):
    return miller(E, P, Q, r) ** ((p * p - 1) // r)

def run(p, a, b, r, rnd, label):
    F2.p = p
    Ep = Curve(a, b, p); n = Ep.order(); t = p + 1 - n
    E = EC2(a, b)
    assert r % 1 == 0 and n % r == 0 and (p + 1) % r == 0 and r > 2 and is_prime(r)
    # P: rational point of order r
    while True:
        S = Ep.points()[rnd.randrange(1, n)]
        if S is None: continue
        Pr = Ep.mul(n // r, S)
        if Pr is not None: break
    P = (F2(Pr[0]), F2(Pr[1]))
    n2 = n * (p + 1 + t)
    assert n2 % (r * r) == 0
    m2 = n2
    while m2 % r == 0: m2 //= r      # cofactor onto the r-Sylow subgroup of E(F_{p^2})
    while True:
        x = F2(rnd.randrange(p), rnd.randrange(p)); y = E.sqrt_point(x)
        if y is None: continue
        R0 = E.mul(m2, (x, y))
        if R0 is None or E.mul(r, R0) is not None: continue   # need R0 in E[r]
        Rm = E.add(R0, E.neg(E.frob(R0)))        # R0 - pi R0 : pi-eigenvalue -1 = p mod r
        Rp = E.add(R0, E.frob(R0))               # R0 + pi R0 : pi-eigenvalue +1 (rational)
        if Rm is not None: break
    assert E.mul(r, Rm) is None and E.frob(Rm) == E.neg(Rm)
    zeta = _weil(E, P, Rm, r)
    out = {'label': label, 'p': p, 'curve': (a, b), '#E(F_p)': n, 'trace t': t, 'r': r, 'p mod r': p % r,
           'ss?': t == 0, 'P': (Pr), 'R-': (Rm[0], Rm[1]), 'e(P,R-)': zeta, 'e(P,R-)^r': zeta ** r}
    # galois property e(pi X, pi Y) = e(X,Y)^p  (sanity of the pairing code)
    X, Y = E.add(P, Rm), Rm
    out['sanity e(piX,piY)==e(X,Y)^p'] = _weil(E, E.frob(X), E.frob(Y), r) == _weil(E, X, Y, r) ** p if False else (_weil(E, E.frob(P), E.frob(Rm), r) == _weil(E, P, Rm, r) ** p)
    # functional f(x) = e(x, R-)  on x = P + R- (non-rational) :
    X = E.add(P, Rm)                       # pi X = P - R-
    fX = _weil(E, X, Rm, r) if E.add(X, E.neg(Rm)) is not None else None
    # e(X,Rm) with X = P+Rm: bilinear => e(P,Rm) e(Rm,Rm) = zeta
    piX = E.frob(X)
    fpiX = _weil(E, piX, Rm, r)            # e(P - Rm, Rm) = zeta
    out['f(X)=e(P+R-,R-)'] = fX
    out['f(piX)'] = fpiX
    out['f(X)^p  (Galois-equivariance would need f(piX)=f(X)^p)'] = fX ** p
    out['f(piX)==f(X)  (c=1 eigen-equivariance)'] = fpiX == fX
    out['f(piX)==f(X)^p  (c=p Galois-equivariance)'] = fpiX == fX ** p
    out['zeta^2==1 ?'] = (zeta * zeta) == F2(1)
    # rational auxiliary point R+ (pi-eigenvalue +1): then P, R+ both in the cyclic group E(F_p)[r]
    if Rp is not None:
        assert E.frob(Rp) == Rp
        al = next(a_ for a_ in range(r) if E.mul(a_, P) == Rp)
        out['R+ = R0+pi R0 is rational and equals alpha*P, alpha'] = al
        out['=> e(P,R+) = e(P,P)^alpha = 1 (Weil alternating); the pi-fixed auxiliary point gives the trivial functional'] = True
    else:
        out['R+ = O'] = True
    # reduced Tate, same tests
    tt = tate(E, P, Rm, r, p)
    tX = tate(E, X, Rm, r, p) if True else None
    tpiX = tate(E, piX, Rm, r, p)
    out['Tate t(P,R-)'] = tt
    out['Tate: t(piX,R-)==t(X,R-)'] = tpiX == tX
    out['Tate: t(piX,R-)==t(X,R-)^p'] = tpiX == tX ** p
    out['Tate bilinear check t(P+P,R-)==t(P,R-)^2'] = tate(E, E.add(P, P), Rm, r, p) == tt * tt
    # pi^2 on E[r]: identity?
    out['pi^2 = id on E[r] (pi^2 R0 = R0)'] = E.frob(E.frob(R0)) == R0
    return out

if __name__ == '__main__':
    rnd = random.Random(20261103)
    cases = []
    # supersingular y^2 = x^3 + x, p = 3 mod 4, r | p+1 = #E
    for p in range(100, 3000):
        if not is_prime(p) or p % 4 != 3: continue
        for r in (q for q in range(5, 200) if is_prime(q) and (p + 1) % q == 0):
            cases.append((p, 1, 0, r, 'supersingular y^2=x^3+x')); break
        if len(cases) >= 2: break
    # ordinary, k=2: random curves over F_p with r | #E, r | p+1, t != 0
    for p in range(100, 1500):
        if not is_prime(p) or p % 4 != 3: continue
        found = False
        for a in range(1, 40):
            for b in range(1, 40):
                if (4 * a ** 3 + 27 * b * b) % p == 0: continue
                n = Curve(a, b, p).order(); t = p + 1 - n
                for r in (q for q in range(5, 200) if is_prime(q) and (p + 1) % q == 0 and n % q == 0):
                    if t != 0 and abs(t) > 1:
                        cases.append((p, a, b, r, 'ordinary, k=2')); found = True; break
                if found: break
            if found: break
        if sum(1 for c in cases if c[4].startswith('ordinary')) >= 2: break
    for c in cases:
        res = run(*c[:4], rnd, c[4])
        print('-' * 70)
        for k, v in res.items(): print(f'  {k}: {v}')
