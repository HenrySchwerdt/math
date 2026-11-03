"""A3: lift to E(Q) (Miller/xedni setting) on E0: y^2 = x^3 - 2 (rank 1, generator G=(3,5)).
Algorithm: lift P,Q to rational points of height <= p (exact Q arithmetic, nG), then k = m/n mod r.
Measures coverage of E(F_p) by reductions of E(Q) points with H(x) < p, and success on random instances."""
import json
from fractions import Fraction as F
from common import *

def qadd(P, Q):
    (x1, y1), (x2, y2) = P, Q
    lam = (3 * x1 * x1) / (2 * y1) if P == Q else (y2 - y1) / (x2 - x1)
    x3 = lam * lam - x1 - x2
    return (x3, lam * (x1 - x3) - y1)

def red(pt, p):
    x, y = pt
    return (x.numerator * pow(x.denominator, -1, p) % p, y.numerator * pow(y.denominator, -1, p) % p)

def find_p(b, rng):
    while True:
        p = rng.randrange(2 ** (b - 1), 2 ** b) | 1
        if p % 3 == 1 and is_prime(p) and p % 4 == 3:
            N = count_points(0, p - 2, p)
            if is_prime(N): return p, N

def run(b, nrand=300):
    rng = random.Random(77 + b)
    p, r = find_p(b, rng)
    E = Curve(0, p - 2, p)
    G = (F(3), F(5)); pts = {}; cur = G; n = 1; nmax = 0
    while True:
        h = max(abs(cur[0].numerator), cur[0].denominator).bit_length()
        if h > b: break
        rp = red(cur, p); pts[rp] = n; pts[(rp[0], (-rp[1]) % p)] = -n; nmax = n
        cur = qadd(cur, G); n += 1
    g = red(G, p); assert E.on_curve(g)
    # planted instances (both lifts exist)
    planted_ok = 0; tot = 0
    for _ in range(50):
        n1, m1 = rng.randrange(1, max(2, nmax + 1)), rng.randrange(1, max(2, nmax + 1))
        if nmax < 1: break
        P = E.mul(n1, g); Q = E.mul(m1, g); k_true = m1 * pow(n1, -1, r) % r
        nn, mm = pts.get(P), pts.get(Q)
        if nn and mm:
            k = mm * pow(nn, -1, r) % r; tot += 1; planted_ok += (E.mul(k, P) == Q)
    # random instances
    succ = 0
    for _ in range(nrand):
        a_, b_ = rng.randrange(1, r), rng.randrange(1, r)
        P, Q = E.mul(a_, g), E.mul(b_, g)
        if P in pts and Q in pts:
            k = pts[Q] * pow(pts[P], -1, r) % r; succ += (E.mul(k, P) == Q)
    return dict(bits=b, p=p, r=r, nmax=nmax, table=len(pts), coverage=len(pts) / r, planted=f'{planted_ok}/{tot}',
                random_success=f'{succ}/{nrand}')
if __name__ == '__main__':
    with open(os.path.join(HERE, 'out_a3.jsonl'), 'w') as f:
        for b in (12, 16, 20, 24):
            res = run(b); f.write(json.dumps(res) + '\n'); print(res, flush=True)
