"""T2: spectral bias of integer-structured coordinate predicates. See PROTOCOL.md."""
import sys, random, math
import numpy as np
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime

def prime_order_curve(rng, lo):
    p = lo
    while True:
        p += 1
        if not is_prime(p): continue
        for _ in range(40):
            a, b = rng.randrange(p), rng.randrange(p)
            if (4 * a ** 3 + 27 * b * b) % p == 0: continue
            E = Curve(a, b, p)
            # count via Legendre sums with numpy
            xs = np.arange(p, dtype=object)
            f = [(x ** 3 + a * x + b) % p for x in range(p)]
            sq = np.zeros(p, dtype=np.int8)
            for y in range(p): sq[y * y % p] += 1
            r = 1 + sum(int(sq[v]) for v in f)
            if r != p and is_prime(r) and r > 1000: return E, r
        # next p

def seq_xy(E, r):
    P = None
    # pick generator: any non-identity point
    for x in range(2, E.p):
        v = (x ** 3 + E.a * x + E.b) % E.p
        if pow(v, (E.p - 1) // 2, E.p) == 1:
            y = pow(v, (E.p + 1) // 4, E.p) if E.p % 4 == 3 else None
            if y is None:
                for yy in range(E.p):
                    if yy * yy % E.p == v: y = yy; break
            P = (x, y); break
    X = np.zeros(r, dtype=np.int64); Y = np.zeros(r, dtype=np.int64)
    R = None
    for k in range(r):
        if R is not None: X[k], Y[k] = R
        R = E.add(R, P)
    assert R is None  # order r
    return X, Y

def spf_sieve(n):
    s = np.zeros(n + 1, dtype=np.int64)
    for i in range(2, n + 1):
        if s[i] == 0:
            s[i::i][s[i::i] == 0] = i
    return s

def features(spf, v, B):
    """per-value predicates for v in [0,p): smooth, prime, squarefree, omega parity"""
    n = len(v); smooth = np.zeros(n, bool); isprime = np.zeros(n, bool)
    sqfree = np.ones(n, bool); lam = np.ones(n, np.int8)
    for i, x in enumerate(v):
        x = int(x)
        if x < 2:
            smooth[i] = True; sqfree[i] = x == 1 or True; continue
        isprime[i] = spf[x] == x
        mx, om, seen = 0, 0, set()
        while x > 1:
            q = int(spf[x]); mx = max(mx, q)
            x //= q; om += 1
            if x % q == 0: sqfree[i] = False
        smooth[i] = mx <= B; lam[i] = -1 if om % 2 else 1
    return smooth, isprime, sqfree, lam

def stat(g):
    g = g.astype(float); g = g - g.mean(); var = g.var()
    F = np.abs(np.fft.rfft(g)) ** 2
    h = np.arange(1, (len(g) - 1) // 2 + 1)
    return (F[h] / (len(g) * var)).max(), int(h[np.argmax(F[h])])

def shuffle_even(g, rng):
    # g indexed by k=0..r-1 with g[k]=g[r-k]; permute values among pairs
    r = len(g); pairs = np.arange(1, (r + 1) // 2); vals = g[pairs].copy(); rng.shuffle(vals)
    out = g.copy(); out[pairs] = vals; out[r - pairs] = vals
    return out

def run(seed, nshuf=200):
    rng = random.Random(seed); nr = np.random.default_rng(seed)
    E, r = prime_order_curve(rng, 2 ** 19 + rng.randrange(2 ** 13))
    p = E.p; print('seed', seed, 'p', p, 'a,b', E.a, E.b, 'r', r, flush=True)
    X, Y = seq_xy(E, r)
    B = int(round(p ** (1 / 3)))
    spf = spf_sieve(p + 2)
    sx = features(spf, X, B); sy = features(spf, Y, B); sx1 = features(spf, (X + 1) % p, B)
    jac = np.array([pow(int(x), (p - 1) // 2, p) == 1 if x else False for x in X])
    preds = {'S1 x smooth': sx[0], 'S2 x prime': sx[1], 'S3 x squarefree': sx[2], 'S4 y smooth': sy[0],
             'S5 Liouville(x)': sx[3], 'S6 Jacobi(x/p) control': jac, 'S7 x+1 smooth': sx1[0],
             'S8 gcd(x,6)==1': (np.gcd(X, 6) == 1),
             'C+ interval-in-k': np.minimum(np.arange(r), r - np.arange(r)) < r / 4}
    c_minus = np.zeros(r); half = nr.random((r + 1) // 2); c_minus[1:(r + 1) // 2 + 0] = half[1:(r + 1) // 2]
    c_minus[r - np.arange(1, (r + 1) // 2)] = c_minus[1:(r + 1) // 2]
    preds['C- random even'] = c_minus
    nulls = np.random.default_rng(seed + 100); out = {}
    for name, g in preds.items():
        g = np.asarray(g)
        if g.var() == 0: print(name, 'constant'); continue
        T, h = stat(g)
        null = np.array([stat(shuffle_even(g, nulls))[0] for _ in range(nshuf)])
        rank_p = (1 + (null >= T).sum()) / (nshuf + 1)
        print('%-26s dens/mean=%.3f T=%.2f at h=%d  null mean=%.2f max=%.2f  rank_p=%.4f  ln(r/2)=%.2f' %
              (name, float(np.mean(g)), T, h, null.mean(), null.max(), rank_p, math.log(r / 2)), flush=True)
        out[name] = (T, null.max(), rank_p)
    return out

if __name__ == '__main__':
    for s in (1, 2): run(s)
