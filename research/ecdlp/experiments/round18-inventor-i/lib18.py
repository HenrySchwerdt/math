"""Round 18 inventor I: m=4 decomposition finders on structured bases. Pure Python ints (+ python-flint 0.9.0 for TOWER)."""
import random, math, time

def is_prime(n):
    if n < 2: return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0: return n == q
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

def sqrt_mod(a, p):
    a %= p
    if a == 0: return 0
    if pow(a, (p - 1) // 2, p) != 1: return None
    if p % 4 == 3: return pow(a, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1: z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1: t2 = t2 * t2 % p; i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r

class EC:
    def __init__(s, a, b, p): s.a, s.b, s.p = a, b, p
    def add(s, P, Q):
        p = s.p
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P; x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0: return None
            l = (3 * x1 * x1 + s.a) * pow(2 * y1, -1, p) % p
        else:
            l = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (l * l - x1 - x2) % p
        return (x3, (l * (x1 - x3) - y1) % p)
    def neg(s, P): return None if P is None else (P[0], (-P[1]) % s.p)
    def sub(s, P, Q): return s.add(P, s.neg(Q))
    def on(s, P): return P is None or (P[1] ** 2 - P[0] ** 3 - s.a * P[0] - s.b) % s.p == 0
    def rand_point(s, rng):
        while True:
            x = rng.randrange(s.p); y = sqrt_mod(x ** 3 + s.a * x + s.b, s.p)
            if y: return (x, y if rng.random() < .5 else (-y) % s.p)

def S3(a, b, p, u, v, w):
    return ((u - v) ** 2 * w * w - 2 * ((u + v) * (u * v + a) + 2 * b) * w + (u * v - a) ** 2 - 4 * b * (u + v)) % p

def S3_coeffs_in_v(a, b, p, u, w):
    """S_3(u,v,w) = c2 v^2 + c1 v + c0 (derived by hand; checked against S3 in t_smoke.py)."""
    c2 = (w - u) ** 2 % p
    c1 = (-2 * u * w * w - 2 * w * (u * u + a) - 2 * a * u - 4 * b) % p
    c0 = (u * u * w * w - 2 * w * (a * u + 2 * b) + a * a - 4 * b * u) % p
    return c2, c1, c0

def gen_instance(bits, seed, kappa=1.0, base='coset'):
    rng = random.Random(18000 * bits + 97 * seed + int(kappa * 10))
    d = max(4, 2 * round(kappa * 2 ** (bits / 5.0) / 2))
    while True:
        c = rng.randrange(max(1, int(0.75 * 2 ** bits) // d), (2 ** bits) // d + 1)
        p = c * d + 1
        if 0.75 * 2 ** bits < p < 2 ** bits and is_prime(p): break
    while True:
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        if (4 * a ** 3 + 27 * b * b) % p: break
    E = EC(a, b, p)
    xs = []
    if base == 'coset':
        fac = [q for q in range(2, d + 1) if d % q == 0 and is_prime(q)]
        while True:
            zeta = pow(rng.randrange(2, p), (p - 1) // d, p)
            if all(pow(zeta, d // q, p) != 1 for q in fac): break
        g = rng.randrange(1, p); x = g
        for _ in range(d): xs.append(x); x = x * zeta % p
    else:  # random control, d x-values
        xs = [rng.randrange(p) for _ in range(d)]
    cls = []   # base x-classes with one y each
    for x in dict.fromkeys(xs):
        y = sqrt_mod(x ** 3 + a * x + b, p)
        if y: cls.append((x, y))
    return dict(bits=bits, seed=seed, kappa=kappa, p=p, a=a, b=b, d=d, E=E, cls=cls, rng=rng)

def pair_sums(E, cls):
    """x-class -> point for all U = P_i +- P_j (i<j), 2P_i; both signs of U are implied by x. Returns dict xU -> (U, i, j, sgn)."""
    D = {}
    n = len(cls)
    for i in range(n):
        Pi = cls[i]
        for j in range(i, n):
            Pj = cls[j]
            for sg in (1, -1):
                if i == j and sg == -1: continue
                U = E.add(Pi, Pj if sg == 1 else E.neg(Pj))
                if U is not None and U[0] not in D: D[U[0]] = (U, i, j, sg)
    return D

def mitm_test(E, D, R, count_ops=None):
    """Find U,T in pair-sum set with R = +-U +-T. Returns (U_x, T_point) or None. ops counted as list [adds, lookups]."""
    adds = 0; hit = None
    p = E.p
    for xU, (U, i, j, sg) in D.items():
        for T in (E.sub(R, U), E.add(R, U)):
            adds += 1
            if T is not None and T[0] in D:
                hit = (U, T) if hit is None else hit
        if hit is not None and count_ops is None: break
    if count_ops is not None: count_ops[0] += adds
    return hit
