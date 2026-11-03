"""Round 10 / ECDLP-33: minimal degree of g in F_p[X] with g(x(kP)) = f(k), k=1..N, f(k)=k or k^2.
Newton divided differences c_j = f[x_1..x_{j+1}] depend only on the first j+1 nodes, so the interpolant
of nodes 1..N has degree max{j<N : c_j != 0}; one pass gives every N <= Nmax=(r-1)/2.
Usage: python3 tight.py SEED PMAX NCURVES   (stdlib only; multiprocessing over primes)
"""
import sys, random, json
from multiprocessing import Pool
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime

def factor(n):
    f, q = [], 2
    while q * q <= n:
        while n % q == 0: f.append(q); n //= q
        q += 1
    if n > 1: f.append(n)
    return sorted(set(f))

def newton_coeffs(xs, vals, p):
    """returns list c with c[j]=f[x_0..x_j] mod p."""
    n = len(xs); d = list(vals); c = [d[0]]
    inv = [0] + [pow(i, -1, p) for i in range(1, p)]
    for j in range(1, n):
        d = [(d[i+1] - d[i]) * inv[(xs[i+j] - xs[i]) % p] % p for i in range(n - j)]
        c.append(d[0])
    return c

def run_curve(E, P, r):
    p = E.p; Nmax = (r - 1) // 2
    xs, Q = [], None
    for k in range(1, Nmax + 1):
        Q = E.add(Q, P); xs.append(Q[0])
    assert len(set(xs)) == Nmax
    out = {}
    for name, f in (('k', lambda k: k % p), ('k2', lambda k: k * k % p)):
        c = newton_coeffs(xs, [f(k) for k in range(1, Nmax + 1)], p)
        out[name] = [j for j, v in enumerate(c) if v == 0]   # zero Newton coeffs (index j = degree level)
    return out

def worker(args):
    seed, p, ncurves = args
    rnd = random.Random(seed * 1000003 + p)
    recs = []
    pairs = [(rnd.randrange(p), rnd.randrange(p)) for _ in range(ncurves)]
    pairs += [(0, rnd.randrange(1, p)) for _ in range(max(3, ncurves // 6))]   # j=0
    pairs += [(rnd.randrange(1, p), 0) for _ in range(max(3, ncurves // 6))]   # j=1728
    for a, b in pairs:
        try: E = Curve(a, b, p)
        except ValueError: continue
        pts = E.points(); n = len(pts)
        for r in [q for q in factor(n) if q >= 7]:
            # random point of order r
            for _ in range(20):
                P = E.mul(n // r, rnd.choice(pts))
                if P is not None: break
            else: continue
            z = run_curve(E, P, r)
            recs.append(dict(p=p, a=a, b=b, n=n, r=r, anom=(r == p), j0=(a == 0), j1728=(b == 0), zk=z['k'], zk2=z['k2']))
    return recs

if __name__ == '__main__':
    seed, pmax, nc = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    primes = [p for p in range(17, pmax + 1) if is_prime(p)]
    with Pool(4) as pool:
        res = pool.map(worker, [(seed, p, nc) for p in primes], chunksize=1)
    recs = [r for rr in res for r in rr]
    json.dump(recs, open('out_raw_seed%d.json' % seed, 'w'))
    print(len(recs), 'curve/point cases')
