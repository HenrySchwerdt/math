"""E3: relation SUPPLY.  H[z] = #{ordered (x1,x2) in V^2, x1!=x2 : z in {x(P1+P2), x(P1-P2)}}.
  target relations  for x_T=z : N_T(z) = H[z]            (mean predicted 2 s^2 / p)
  closed triples    N_3 = sum_{z in V} H[z]               (mean predicted 2 s^3 / p)
A linear system for the s unknown logs needs >= s-1 independent relations => N_3 >= s => s >= sqrt(p/2).
Also reports Poisson dispersion of H on the curve x-set (is the yield 'random'?)."""
import sys, os, random, numpy as np, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'round13-inventor-d'))
from d2lib import is_prime, sqrt_mod
def vinv(x, p):
    r = np.ones_like(x); b = x.copy(); e = p-2
    while e:
        if e & 1: r = r*b % p
        b = b*b % p; e >>= 1
    return r
def run(p, a, b, V, rng):
    xs = np.array(sorted(V), dtype=np.int64); ys = np.array([V[int(x)] for x in xs], dtype=np.int64)
    s = len(xs); H = np.zeros(p, dtype=np.int64)
    for i in range(s):
        x1, y1 = xs[i], ys[i]
        dx = (xs - x1) % p; m = dx != 0
        inv = vinv(np.where(m, dx, 1), p)
        for sgn in (1, -1):
            lam = ((sgn*ys - y1) % p) * inv % p
            x3 = (lam*lam - x1 - xs) % p
            np.add.at(H, x3[m], 1)
    return xs, H
def coset_base(p, n, a, b, rng):
    d = 1 << n
    while True:
        z = rng.randrange(2, p); zeta = pow(z, (p-1) >> n, p)
        if pow(zeta, d >> 1, p) != 1: break
    g = rng.randrange(1, p); V = {}; x = g
    for _ in range(d):
        v = (x**3 + a*x + b) % p
        y = sqrt_mod(v, p) if v else None
        if y: V[x] = y
        x = x*zeta % p
    return V
def random_base(p, s, a, b, rng):
    V = {}
    while len(V) < s:
        x = rng.randrange(p); v = (x**3 + a*x + b) % p; y = sqrt_mod(v, p) if v else None
        if y: V[x] = y
    return V
rng = random.Random(14)
print("kind   p      s   s/sqrt(p)   N3(obs)   2s^3/p(pred)  N3/s    meanH(curve x)  2s^2/p   Var/Mean(H)")
for n, p_lo in ((10, 2**14), (11, 2**16)):
    while True:
        p = (rng.randrange(p_lo//2 // (1 << n), p_lo // (1 << n)) << n) + 1
        if is_prime(p): break
    a, b = rng.randrange(1, p), rng.randrange(1, p)
    for kind in ('coset', 'random'):
        for fr in (0.25, 0.5, 1.0, 2.0):
            if kind == 'coset':
                if fr != 1.0: continue
                V = coset_base(p, n - 0, a, b, rng)    # d = 2^n ~ sqrt(p)*... 
            else:
                V = random_base(p, int(fr*math.sqrt(p)), a, b, rng)
            s = len(V); xs, H = run(p, a, b, V, rng)
            N3 = int(H[xs].sum())
            sq = np.array([1 if (x**3+a*x+b) % p and pow((x**3+a*x+b) % p, (p-1)//2, p) == 1 else 0 for x in range(p)], dtype=bool)
            Hc = H[sq]
            print(f"{kind:6s} {p:6d} {s:5d} {s/math.sqrt(p):7.2f} {N3:9d} {2*s**3/p:12.1f} {N3/s:7.2f}  {Hc.mean():10.3f}   {2*s*s/p:7.3f}   {Hc.var()/Hc.mean():6.2f}")
