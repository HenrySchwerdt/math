import sys, time, random
sys.path.insert(0, '/home/user/math/research/ecdlp/experiments/lib')
from toyec import Curve, is_prime
from math import gcd, ceil
T0 = time.time(); LIMIT = 240
rng = random.Random(7)
primes = [p for p in range(61, 212) if is_prime(p)]

def gen(strict_gcd=True):
    while True:
        p = rng.choice(primes); a = rng.randrange(p); b = rng.randrange(p)
        try: E = Curve(a, b, p)
        except ValueError: continue
        pts = E.points(); N = len(pts)
        if gcd(N, 6) == 1: return E, pts, N

def build(E, pts, m):
    X = sorted({P[0] for P in pts if P})
    phi = {}
    for P in pts:
        if P: phi[P[0]] = E.mul(m, P)[0]
    return X, phi

def cycles(X, phi):
    seen, c = set(), 0
    for x in X:
        if x in seen: continue
        c += 1; y = x
        while y not in seen: seen.add(y); y = phi[y]
    return c

def dstar(X, sig, p):
    M = len(X); basis = {}  # pivot index -> (vec normalized pivot=1)
    pw = [1]*M; sp = [1]*M
    for i in range(1, M+1):
        pw = [a*x % p for a, x in zip(pw, X)]
        sp = [a*sig[x] % p for a, x in zip(sp, X)]
        v = [(a-b) % p for a, b in zip(pw, sp)]
        for piv, bv in basis.items():
            f = v[piv]
            if f: v = [(a - f*b) % p for a, b in zip(v, bv)]
        piv = next((j for j, a in enumerate(v) if a), None)
        if piv is None: return i
        inv = pow(v[piv], -1, p); v = [a*inv % p for a in v]
        basis[piv] = v
    return None

def null_sigma(X, phi):
    perm = X[:]; rng.shuffle(perm); pi = dict(zip(X, perm)); inv = {v: k for k, v in pi.items()}
    return {x: pi[phi[inv[x]]] for x in X}

rows = []
def run(E, pts, N, m, stratum):
    if time.time() - T0 > LIMIT: return False
    X, phi = build(E, pts, m); M = len(X); c = cycles(X, phi)
    d = dstar(X, phi, E.p)
    nl = [dstar(X, null_sigma(X, phi), E.p) for _ in range(3)]
    rows.append((stratum, E.p, E.a, E.b, N, m, M, c, d, nl, M-c+1, ceil(M/m**2)))
    print(*rows[-1], flush=True); return True
print("stratum p a b N m M c dstar null_dstar generic_pred bound")
for _ in range(20):
    E, pts, N = gen()
    for m in (2, 3):
        if not run(E, pts, N, m, 'A'): break
cand = []
for _ in range(300):
    E, pts, N = gen()
    if (N-1)//2 < 30: continue
    X, phi = build(E, pts, 2); cand.append((cycles(X, phi)/len(X), E, pts, N))
cand.sort(key=lambda t: -t[0])
for _, E, pts, N in cand[:10]: run(E, pts, N, 2, 'B')
r2 = [row for row in rows if row[5] == 2]
ratios = sorted(row[8]/row[10] for row in r2)
print("SUMMARY n_m2=%d elapsed=%.1fs" % (len(r2), time.time()-T0))
print("bound_violations", sum(1 for row in rows if row[8] < row[11]))
print("median_r", ratios[len(ratios)//2], "frac_r>=0.98", sum(r >= 0.98 for r in ratios)/len(ratios))
print("frac_below_nullmin-2", sum(1 for row in r2 if row[8] < min(row[9]) - 2)/len(r2))
print("n_curves_with_c>1:", sum(1 for row in r2 if row[7] > 1), "max_c", max(row[7] for row in r2))
