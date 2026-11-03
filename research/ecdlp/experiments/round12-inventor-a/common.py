"""Shared helpers: instance generation, counted group ops, DP rho, regression."""
import sys, os, json, random, math
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from toyec import Curve, is_prime, dlog_bsgs

HERE = os.path.dirname(os.path.abspath(__file__))
SIZES = [12, 14, 16, 18, 20, 22, 24]

def seeds_for(b):
    return range(1, 9) if b >= 22 else range(1, 11)

def count_points(a, b, p):
    sq = np.zeros(p, dtype=np.int8)
    xs = np.arange(p, dtype=np.int64)
    sq[(xs * xs) % p] = 1
    tot = 1
    ch = 1 << 22
    for s in range(0, p, ch):
        x = xs[s:s + ch]
        v = (x * x % p * x + a * x + b) % p
        tot += int((2 * sq[v].astype(np.int64)).sum()) + int((v == 0).sum())
        # v==0: one point; sq[0]=1 would give 2, correct by subtracting
        tot -= int((v == 0).sum()) * 2 - int((v == 0).sum())
    return tot

def rand_prime34(rng, b):
    while True:
        p = rng.randrange(int(0.75 * 2 ** b), 2 ** b) | 1
        if p % 4 == 3 and is_prime(p):
            return p

def sqrt34(v, p):
    return pow(v, (p + 1) // 4, p)

def gen_instance(b, seed):
    rng = random.Random(1000 * b + seed)
    while True:
        p = rand_prime34(rng, b)
        for _ in range(60):
            a, c = rng.randrange(p), rng.randrange(p)
            if (4 * a ** 3 + 27 * c * c) % p == 0:
                continue
            N = count_points(a, c, p)
            if is_prime(N):
                while True:
                    x = rng.randrange(p)
                    v = (x ** 3 + a * x + c) % p
                    y = sqrt34(v, p)
                    if y * y % p == v and v != 0:
                        break
                k = rng.randrange(1, N)
                E = Curve(a, c, p)
                P = (x, y)
                Q = E.mul(k, P)
                return dict(bits=b, seed=seed, p=p, a=a, b=c, r=N, P=P, k=k, Q=Q)

class CC:
    """Curve with counted additions."""
    def __init__(self, a, b, p):
        self.E = Curve(a, b, p); self.p = p; self.n = 0
    def add(self, P, Q):
        self.n += 1
        return self.E.add(P, Q)
    def neg(self, P): return self.E.neg(P)
    def mul(self, k, P):
        R = None
        while k:
            if k & 1: R = self.add(R, P) if R is not None else P
            k >>= 1
            if k: P = self.add(P, P)
        return R

def load_instances():
    out = []
    with open(os.path.join(HERE, 'instances.jsonl')) as f:
        for l in f:
            d = json.loads(l)
            d['P'] = tuple(d['P']); d['Q'] = tuple(d['Q'])
            out.append(d)
    return out

def rho_dp(inst, rng_seed=1):
    C = CC(inst['a'], inst['b'], inst['p']); r = inst['r']; P, Q = inst['P'], inst['Q']
    rng = random.Random(rng_seed)
    B = 32
    T, ab = [], []
    for _ in range(B):
        a, b = rng.randrange(1, r), rng.randrange(1, r)
        T.append(C.add(C.mul(a, P), C.mul(b, Q))); ab.append((a, b))
    d = max(0, int(round(math.log2(max(1.0, math.sqrt(r) / 16)))))
    mask = (1 << d) - 1
    seen = {}
    cap = 200 * int(math.sqrt(r)) + 1000
    steps = 0
    while steps < cap:
        a, b = rng.randrange(1, r), rng.randrange(1, r)
        X = C.add(C.mul(a, P), C.mul(b, Q))
        for _ in range(20 * (mask + 1) + 50):
            if X is None: break
            steps += 1
            if X[0] & mask == 0:
                key = X
                if key in seen:
                    a2, b2 = seen[key]
                    if (b - b2) % r != 0:
                        k = (a2 - a) * pow(b - b2, -1, r) % r
                        return k, C.n
                    break
                seen[key] = (a, b); break
            j = X[0] % B
            X = C.add(X, T[j]); a = (a + ab[j][0]) % r; b = (b + ab[j][1]) % r
    return None, C.n

TQ = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
      15: 2.131, 20: 2.086, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980}
def tq(df):
    ks = sorted(TQ)
    for k in ks:
        if df <= k: return TQ[k]
    return 1.96

def fit(xs, ys):
    xs, ys = np.array(xs, float), np.array(ys, float)
    n = len(xs); mx, my = xs.mean(), ys.mean()
    sxx = ((xs - mx) ** 2).sum(); al = ((xs - mx) * (ys - my)).sum() / sxx
    c = my - al * mx; res = ys - (al * xs + c)
    se = math.sqrt((res ** 2).sum() / (n - 2) / sxx)
    h = tq(n - 2) * se
    return dict(alpha=al, se=se, lo=al - h, hi=al + h, c=c, n=n)
