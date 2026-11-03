"""ECDLP-8: pooled normalized values u = |F|/sqrt(N) for g=x,y,x^2+x+1 ; compare with semicircle (SU(2) Sato-Tate for 2cos) and Gaussian."""
import sys, math, numpy as np
sys.path.insert(0, '../lib')
from mixed_sums import make_curves, legendre_table
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 3
G = {'x': lambda x,y,p: x, 'y': lambda x,y,p: y, 'x^2+x+1': lambda x,y,p: x*x+x+1}
vals = {k: [] for k in G}
for E, r, seq in make_curves(seed, maxc=60):
    p = E.p; L = legendre_table(p)
    for n, fn in G.items():
        f = np.zeros(r)
        for k in range(1, r):
            x, y = seq[k]; f[k] = L[fn(x,y,p) % p]
        N = np.count_nonzero(f); F = np.fft.fft(f)[1:]
        # F is real up to a global phase (f(-Q)=+-f(Q)); take signed real part after rotating
        ph = np.abs(F.real).sum() >= np.abs(F.imag).sum()
        u = (F.real if ph else F.imag) / math.sqrt(N)
        vals[n].append(u)
sc = lambda u: math.sqrt(max(4-u*u,0))/(2*math.pi)
for n, v in vals.items():
    u = np.concatenate(v)
    # symmetrize sign (global sign of F(c) vs F(-c) is irrelevant for even moments)
    m = [np.mean(u**j) for j in (2,4,6)]
    # KS distance of |u| distribution to semicircle |u|: cdf of |u| for semicircle on [0,2]
    xs = np.linspace(0, 2, 2001); pdf = np.array([2*sc(t) for t in xs]); cdf = np.cumsum(pdf)*(xs[1]-xs[0])
    au = np.sort(np.abs(u)); emp = np.arange(1, len(au)+1)/len(au)
    ks = np.max(np.abs(np.interp(au, xs, cdf) - emp))
    print('g=%-8s n=%d  E u^2=%.3f E u^4=%.3f E u^6=%.3f  max|u|=%.3f  KS(|u|, semicircle)=%.3f' % (n, len(u), *m, au[-1], ks))
print('reference: semicircle (SU(2)) 1,2,5 ; real Gaussian 1,3,15')
