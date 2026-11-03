import sys, json, random, math
import numpy as np
sys.path.insert(0, '/home/user/math/research/ecdlp/experiments/lib')
from toyec import Curve, is_prime

BUCKETS = [(1000, 2000), (4000, 8000), (16000, 32000), (64000, 128000)]
NCURVES = 12
DEG = {'x': 1, 'y': 1, 'x+1': 1, 'x^2+x+1': 2, 'x*y': 2, 'x^3+2': 3}
PREDS = list(DEG) + ['parity_x', 'hash_x', 'random_pm1']

def legendre_table(p):
    t = -np.ones(p, dtype=np.int64)
    t[0] = 0
    sq = (np.arange(1, p, dtype=np.int64) ** 2) % p
    t[sq] = 1
    return t

def count_points(a, b, p, chi):
    x = np.arange(p, dtype=np.int64)
    f = (x * x % p * x + a * x + b) % p
    return p + 1 + int(chi[f].sum())

def sample_curve(rng, lo, hi):
    while True:
        p = rng.randint(lo, hi)
        if not is_prime(p):
            continue
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a ** 3 + 27 * b ** 2) % p == 0:
            continue
        chi = legendre_table(p)
        r = count_points(a, b, p, chi)
        if r == p or r < 100 or not is_prime(r):
            continue
        return p, a, b, r, chi

def random_point(E, rng, chi):
    p = E.p
    while True:
        x = rng.randrange(p)
        f = (x ** 3 + E.a * x + E.b) % p
        if chi[f] == 1:
            for y in range(p):  # find sqrt (only once per curve)
                if y * y % p == f:
                    return (x, y)

def orbit(E, P, r):
    xs = np.zeros(r, dtype=np.int64); ys = np.zeros(r, dtype=np.int64)
    Q = None
    for k in range(r):
        if Q is not None:
            xs[k], ys[k] = Q
        Q = E.add(Q, P)
    assert Q is None, 'order mismatch'
    return xs, ys  # k=0 is O (stored as 0,0, masked by caller)

def predicate(name, xs, ys, p, chi, rng, r):
    if name == 'x': v = xs
    elif name == 'y': v = ys
    elif name == 'x+1': v = xs + 1
    elif name == 'x^2+x+1': v = xs * xs + xs + 1
    elif name == 'x*y': v = xs * ys
    elif name == 'x^3+2': v = xs * xs % p * xs + 2
    if name in DEG:
        s = chi[v % p].astype(float)
    elif name == 'parity_x':
        s = np.where(xs & 1, 1.0, -1.0)
    elif name == 'hash_x':
        s = np.where(((xs * 2654435761) % (2 ** 32) >> 7) & 1, 1.0, -1.0)
    else:
        s = np.array([rng.choice((-1.0, 1.0)) for _ in range(r)])
    s[0] = 0.0  # point at infinity
    return s

def ks_st(A):
    # POST-HOC: KS distance of A=|X|^2 from the Sato-Tate law of X^2, X=2cos(t), density sqrt(4-x^2)/(2pi) on [-2,2]
    xs_ = np.linspace(-2, 2, 4001); dens = np.sqrt(4 - xs_ ** 2) / (2 * math.pi)
    cdfx = np.cumsum(dens) * (xs_[1] - xs_[0])
    t = np.sort(A); cdf_a = np.interp(np.sqrt(t), xs_[xs_ >= 0], (2 * cdfx[xs_ >= 0] - cdfx[xs_ >= 0][0] * 2)[:len(xs_[xs_ >= 0])] if False else np.zeros(1)) if False else None
    ax = xs_[xs_ >= 0]; c = np.cumsum(dens[xs_ >= 0]) * (ax[1] - ax[0]) * 2  # P(|X|<=u)
    F = np.interp(np.sqrt(t), ax, c, right=1.0)
    n = len(t); e = np.arange(1, n + 1) / n
    return float(max(np.max(e - F), np.max(F - (e - 1.0 / n))))

def spectrum(s):
    r = len(s)
    return np.conj(np.fft.fft(s)) / math.sqrt(r)  # X_c = r^-1/2 sum s_k e(+ck/r)

def direct(s, c):
    r = len(s)
    k = np.arange(r, dtype=np.int64)
    ph = 2 * math.pi * ((c * k) % r) / r
    return (s * (np.cos(ph) + 1j * np.sin(ph))).sum() / math.sqrt(r)

def classstat(s, m):
    r = len(s); k = np.arange(r) % m
    mu = s.mean(); var = s.var()
    st = 0.0
    for j in range(m):
        sel = s[k == j]
        st += len(sel) * (sel.mean() - mu) ** 2 / var
    return st  # approx chi2 with m-1 df under null

def main(seed, out):
    rng = random.Random(seed)
    rows, oracle, leak = [], [], []
    for bi, (lo, hi) in enumerate(BUCKETS):
        for ci in range(NCURVES):
            p, a, b, r, chi = sample_curve(rng, lo, hi)
            E = Curve(a, b, p)
            P = random_point(E, rng, chi)
            xs, ys = orbit(E, P, r)
            for name in PREDS:
                s = predicate(name, xs, ys, p, chi, rng, r)
                if name == 'x':
                    assert all(int(s[i]) == (0 if xs[i] % p == 0 else (1 if pow(int(xs[i]), (p - 1) // 2, p) == 1 else -1)) for i in range(1, min(r, 300)))
                X = spectrum(s)
                A = np.abs(X[1:]) ** 2
                row = dict(bucket=bi, curve=ci, p=p, a=a, b=b, r=r, pred=name,
                           M=float(A.max()), mean=float(A.mean()), m2=float((A ** 2).mean()),
                           M_over_lnr=float(A.max() / math.log(r)),
                           m3=float((A ** 3).mean()), frac_gt4=float((A > 4.0).mean()), q999=float(np.quantile(A, 0.999)),
                           ks_st=ks_st(A),
                           parseval_err=float(abs((np.abs(X) ** 2).sum() - (s ** 2).sum())),
                           mean_expected=float(((s ** 2).sum() - abs(X[0]) ** 2) / (r - 1)),
                           p_over_r=p / r, deg=DEG.get(name))
                rows.append(row)
                if bi == 1:
                    leak.append(dict(curve=ci, pred=name, chi2_mod2=classstat(s, 2), chi2_mod3=classstat(s, 3)))
                if (bi, ci) in ((0, 0), (1, 0)) and name in ('x', 'y', 'x*y', 'random_pm1'):
                    cs = [1, 2, r // 2, r - 1, rng.randrange(1, r)]
                    for c in cs:
                        d = direct(s, c)
                        oracle.append(dict(bucket=bi, p=p, r=r, pred=name, c=c, fft_re=float(X[c].real), fft_im=float(X[c].imag),
                                           direct_re=float(d.real), direct_im=float(d.imag), abs_diff=float(abs(X[c] - d))))
        print('bucket', bi, 'done', flush=True)
    json.dump(dict(seed=seed, rows=rows, oracle=oracle, leak=leak,
                   versions=dict(python=sys.version, numpy=np.__version__)), open(out, 'w'))

if __name__ == '__main__':
    main(int(sys.argv[1]), sys.argv[2])
