"""ECDLP-8 / RUN-60986daa: moments of full- and half-range mixed character sums
sum_k chi(g([k]P)) e(ck/r) on toy curves (p < 3000, #E = r prime).  Synthetic data only.
Usage: python3 mixed_sums.py [seed]
"""
import sys, random, math
import numpy as np
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime

def legendre_table(p):
    t = np.zeros(p, dtype=np.int8)
    for a in range(1, p):
        t[a * a % p] = 1
    t[t == 0] = -1
    t[0] = 0
    return t

FUNCS = {  # name -> (function of x,y,p, deg of g, sign behaviour under Q->-Q)
    'chi(x)': lambda x, y, p: x,
    'chi(y)': lambda x, y, p: y,
    'chi(x+1)': lambda x, y, p: x + 1,
    'chi(2x)': lambda x, y, p: 2 * x,
    'chi(x^2+x+1)': lambda x, y, p: x * x + x + 1,
    'chi(xy)': lambda x, y, p: x * y,
    'chi(x^3+ax+b=y^2)->trivial': None,
}
DEG = {'chi(x)': 2, 'chi(y)': 3, 'chi(x+1)': 2, 'chi(2x)': 2, 'chi(x^2+x+1)': 4, 'chi(xy)': 5}

def make_curves(seed, n_per_p=1, plo=1000, phi=3000, maxc=40):
    rng = random.Random(seed)
    primes = [p for p in range(plo, phi) if is_prime(p)]
    out = []
    while len(out) < maxc:
        p = rng.choice(primes)
        a, b = rng.randrange(p), rng.randrange(p)
        try:
            E = Curve(a, b, p)
        except ValueError:
            continue
        pts = E.points()
        r = len(pts)
        if not is_prime(r) or r < 100:
            continue
        P = pts[1]
        seq = [None]
        Q = None
        seq = []
        for k in range(r):
            seq.append(Q)
            Q = E.add(Q, P)
        out.append((E, r, seq))
    return out

def stats(vals):
    v = np.asarray(vals)
    return v.mean(), v.var(), (v ** 2).mean()

def analyse(E, r, seq):
    p = E.p
    L = legendre_table(p)
    res = {}
    for name, fn in FUNCS.items():
        if fn is None:
            continue
        f = np.zeros(r)
        for k in range(1, r):
            x, y = seq[k]
            f[k] = L[fn(x, y, p) % p]
        N = int(np.count_nonzero(f))
        F = np.fft.fft(f)          # F[c] = sum_k f_k e(-ck/r); |F| same as for +c
        I = (np.abs(F[1:]) ** 2) / N
        # full-range
        d = dict(N=N, meanI=I.mean(), varI=I.var(), M4=(I ** 2).mean(),
                 maxF=np.abs(F[1:]).max() / math.sqrt(p))
        # exact autocorrelation formula for the 4th moment: sum_R A(R)^2 / N^2 (A = f*f cyclic)
        A = np.real(np.fft.ifft(F * F))
        d['M4_corr'] = (A ** 2).sum() / N ** 2 - ((np.abs(F[0]) ** 2 / N) ** 2) / r  # remove c=0 term
        d['M4_corr'] *= r / (r - 1)  # average over c != 0 only
        # Weil-type: |F+eps_O| for g=x type (unramified at O): eps=1
        d['maxF_plus1'] = np.abs(F[1:] + 1).max() / math.sqrt(p)
        # half-range DFT as in the observation: s_k, k=1..h, frequencies c/h
        h = (r - 1) // 2
        s = f[1:h + 1]
        ks = np.arange(1, h + 1)
        Xh = np.fft.fft(np.concatenate([[0], s]))[1:h]   # sum_k s_k e(-ck/h), c=1..h-1 (|.| equals +c up to conj)
        Ih = np.abs(Xh) ** 2 / np.count_nonzero(s)
        d['half_meanI'], d['half_varI'] = Ih.mean(), Ih.var()
        # half-range, frequencies on the r-grid: sum_{k=1}^h s_k e(ck/r)
        Xr = np.fft.fft(np.concatenate([[0], s, np.zeros(r - h - 1)]))[1:r]
        Ir = np.abs(Xr) ** 2 / np.count_nonzero(s)
        d['halfr_meanI'], d['halfr_varI'] = Ir.mean(), Ir.var()
        res[name] = d
    # controls
    for cname in ['parity(x)', 'hashbit(x)']:
        f = np.zeros(r)
        for k in range(1, r):
            x = seq[k][0]
            f[k] = (1 - 2 * (x & 1)) if cname == 'parity(x)' else (1 - 2 * (((x * 2654435761) >> 7) & 1))
        N = r - 1
        F = np.fft.fft(f)
        I = (np.abs(F[1:]) ** 2) / N
        h = (r - 1) // 2
        s = f[1:h + 1]
        Xh = np.fft.fft(np.concatenate([[0], s]))[1:h]
        Ih = np.abs(Xh) ** 2 / h
        res[cname] = dict(N=N, meanI=I.mean(), varI=I.var(), M4=(I ** 2).mean(),
                          maxF=np.abs(F[1:]).max() / math.sqrt(p), half_meanI=Ih.mean(), half_varI=Ih.var(),
                          halfr_meanI=float('nan'), halfr_varI=float('nan'), M4_corr=float('nan'), maxF_plus1=float('nan'))
    return res

if __name__ == '__main__':
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    curves = make_curves(seed)
    print('seed', seed, 'curves', len(curves), 'p range', min(c[0].p for c in curves), max(c[0].p for c in curves))
    agg = {}
    for E, r, seq in curves:
        for name, d in analyse(E, r, seq).items():
            agg.setdefault(name, []).append(d)
    keys = ['meanI', 'varI', 'M4', 'M4_corr', 'maxF', 'maxF_plus1', 'half_meanI', 'half_varI', 'halfr_meanI', 'halfr_varI']
    print('%-16s' % 'g' + ''.join('%11s' % k for k in keys))
    for name, ds in agg.items():
        print('%-16s' % name + ''.join('%11.4f' % np.mean([d[k] for d in ds]) for k in keys))
    print('worst-case (max over curves) maxF/sqrt(p) and maxF_plus1:')
    for name, ds in agg.items():
        print('%-16s deg=%s max maxF=%.3f max |F+1|/sqrt p=%.3f' % (name, DEG.get(name), max(d['maxF'] for d in ds), max(d['maxF_plus1'] for d in ds)))
