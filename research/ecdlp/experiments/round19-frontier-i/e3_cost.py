"""E3: cost scaling of Problem-L solvers vs Pollard rho on the same toy groups.
Solvers (counted units in brackets):
  EXH  paper Algorithm 1 + exhaustive Problem-L solver (test all C(N,l) supports)   [support tests]
  MITM generic zero-sum-subset meet-in-the-middle over the N points                 [group additions]
  RHO  r-adding Pollard rho with Brent cycle detection (control)                    [group additions]
EXH/MITM use the dlog-equivalent zero-sum test (validated equal to the rank test in E1)
so that C(N,l) ~ 1e6 supports are feasible in pure python. Every returned m is verified by m*P==Q (RHO)
or by the log model (EXH/MITM)."""
import sys, random, itertools, json, time
from math import comb, log2, isqrt
from ecL import *

def pick_nl(r):
    """paper regime l = 3n' (N = 2l): largest n' with C(6n',3n') <= r (n'=1 minimum)."""
    n = 1
    while comb(6 * (n + 1), 3 * (n + 1)) <= r: n += 1
    return n, 3 * n, comb(6 * n, 3 * n)

def exh(r, m, rng, n, l):
    """returns (tests, passes, ok)"""
    N = 3 * n + l; tests = 0; passes = 0
    kP = N // 2; kQ = N - kP
    while True:
        passes += 1; tests += int(N * 1.5 * log2(r))  # point generation (group ops) counted too
        I = rng.sample(range(1, r), kP) if r > kP + 2 else list(range(1, kP + 1))
        J = rng.sample(range(1, r), kQ)
        logs = [s % r for s in I] + [(-m * s) % r for s in J]
        for S in itertools.combinations(range(N), 3 * n):
            tests += 1
            if sum(logs[i] for i in S) % r == 0:
                A = sum(I[i] for i in S if i < kP) % r; B = sum(J[i - kP] for i in S if i >= kP) % r
                if B and A * pow(B, -1, r) % r == m: return tests, passes
        if passes > 60: return tests, passes

def mitm(r, m, rng, extra=1):
    """N points; enumerate subsets of each half (group additions counted), match sums.  zero-sum subset of any size."""
    N = 1
    while 2 ** N < extra * r: N += 1
    ops = 0; passes = 0
    while True:
        passes += 1; ops += int(N * 1.5 * log2(r))
        kP = N // 2
        I = rng.sample(range(1, r), kP); J = rng.sample(range(1, r), N - kP)
        logs = [s % r for s in I] + [(-m * s) % r for s in J]
        h = N // 2
        left = {}
        sums = [(0, 0)]  # (sum, mask)
        for i in range(h):
            sums += [((s + logs[i]) % r, mk | 1 << i) for s, mk in sums]; ops += len(sums) // 2
        for s, mk in sums:
            left.setdefault(s, mk)
        sums2 = [(0, 0)]
        for i in range(h, N):
            sums2 += [((s + logs[i]) % r, mk | 1 << i) for s, mk in sums2]; ops += len(sums2) // 2
        for s, mk in sums2:
            mk1 = left.get((-s) % r)
            if mk1 is not None and (mk1 | mk):
                full = mk1 | mk
                A = sum(I[i] for i in range(kP) if full >> i & 1) % r
                B = sum(J[i - kP] for i in range(kP, N) if full >> i & 1) % r
                if B and A * pow(B, -1, r) % r == m: return ops, passes
        if passes > 60: return ops, passes

def rho(E, P, Q, r, rng, tw=16):
    """r-adding walk, Brent cycle detection, restart on failure. returns (ops, m)"""
    ops = 0
    tab = []
    for _ in range(tw):
        a, b = rng.randrange(r), rng.randrange(r)
        tab.append((E.add(E.mul(a, P), E.mul(b, Q)), a, b)); 
    ops += tw * 3 * int(1.5 * log2(r)) // 2  # table setup: each entry ~ two short scalar mults, honest-ish
    def step(R, a, b):
        if R is None: h = 0
        else: h = (R[0] * 2654435761 + R[1]) % tw
        T, ta, tb = tab[h]
        return E.add(R, T), (a + ta) % r, (b + tb) % r
    while True:
        a, b = rng.randrange(r), rng.randrange(r)
        R = E.add(E.mul(a, P), E.mul(b, Q)); ops += int(3 * log2(r))
        pw = lam = 1; X = (R, a, b); Y = step(*X); ops += 1
        while X[0] != Y[0]:
            if pw == lam: X = Y; pw *= 2; lam = 0
            Y = step(*Y); ops += 1; lam += 1
            if ops > 400 * isqrt(r) + 5000: break
        else:
            (_, a1, b1), (_, a2, b2) = X, Y
            db = (b1 - b2) % r
            if db:
                m = (a2 - a1) * pow(db, -1, r) % r
                if E.mul(m, P) == Q: return ops, m
        # failure: restart

RAW = []
def emit(d): RAW.append(d)

def finish(tag):
    import statistics as st
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw_%s.jsonl' % tag)
    with open(path, 'w') as f:
        for d in RAW: f.write(json.dumps(d) + '\n')
    keys = sorted({(d['alg'], d['bits']) for d in RAW})
    for alg, bits in keys:
        v = [d['ops'] for d in RAW if d['alg'] == alg and d['bits'] == bits]
        rr = [d['r'] for d in RAW if d['alg'] == alg and d['bits'] == bits]
        print(json.dumps(dict(alg=alg, bits=bits, n=len(v), mean_r=sum(rr) / len(rr), mean_ops=st.mean(v), median_ops=st.median(v), sd=st.pstdev(v),
              mean_ops_over_sqrt_r=st.mean(o / x ** 0.5 for o, x in zip(v, rr)), mean_ops_over_r=st.mean(o / x for o, x in zip(v, rr)))))
    print('raw file', path, 'rows', len(RAW))

if __name__ == '__main__':
    which = sys.argv[1]; seed = int(sys.argv[2]); rng = random.Random(seed)
    if which in ('RHO', 'SMALL'):
        bits_list = [int(x) for x in sys.argv[3].split(',')]; ninst = int(sys.argv[4])
        for bits in bits_list:
            curves = 0
            for ci in range(3):
                E, r, pts = gen_curve(int(2 ** bits * 0.9), int(2 ** bits * 1.1), rng)
                for _ in range(ninst):
                    P, Q, m = random_instance(E, r, pts, rng)
                    ops, mm = rho(E, P, Q, r, rng)
                    emit(dict(alg='RHO', bits=bits, r=r, ops=ops, ok=(mm == m)))
                    if which == 'SMALL':
                        n, l, c = pick_nl(r)
                        t, ps = exh(r, m, rng, n, l)
                        emit(dict(alg='EXH', bits=bits, r=r, n=n, l=l, C=c, ops=t, passes=ps))
                        t, ps = mitm(r, m, rng)
                        emit(dict(alg='MITM', bits=bits, r=r, ops=t, passes=ps))
    else:  # LOGMODEL: random prime r (no curve), alg in EXH/MITM
        bits_list = [int(x) for x in sys.argv[3].split(',')]; ninst = int(sys.argv[4])
        for bits in bits_list:
            for _ in range(ninst):
                while True:
                    r = rng.randrange(2 ** bits, 2 ** (bits + 1))
                    if is_prime(r): break
                m = rng.randrange(1, r)
                if which == 'LOGEXH':
                    n, l, c = pick_nl(r)
                    t, ps = exh(r, m, rng, n, l)
                    emit(dict(alg='EXH', bits=bits, r=r, n=n, l=l, C=c, ops=t, passes=ps))
                else:
                    t, ps = mitm(r, m, rng)
                    emit(dict(alg='MITM', bits=bits, r=r, ops=t, passes=ps))
    finish('%s_%s_%s' % (which, seed, sys.argv[3].replace(',', '-')))
