"""ECDLP-8: check |F(c) + eps| <= D sqrt(p) for all c != 0 (c=0 excluded: trivial group character),
eps = chi(leading coeff at O) if g has even pole order at O (unramified), else 0; D = conductor degree
(geometric ramified points of div(g), weighted by degree) = 2g-2+deg f(chi) with g(E)=1."""
import sys, math, numpy as np
sys.path.insert(0, '../lib')
from mixed_sums import make_curves, legendre_table
# name: (fn, D, eps(p) )
G = {'x': (lambda x,y,p: x, 2, lambda L,p: 1), 'x+1': (lambda x,y,p: x+1, 2, lambda L,p: 1),
     '2x': (lambda x,y,p: 2*x, 2, lambda L,p: int(L[2])), 'x^2+x+1': (lambda x,y,p: x*x+x+1, 4, lambda L,p: 1),
     'y': (lambda x,y,p: y, 4, lambda L,p: 0), 'xy': (lambda x,y,p: x*y, 6, lambda L,p: 0)}
worst = {k: 0.0 for k in G}; worst_ratio = {k: 0.0 for k in G}
for seed in (11, 12):
    for E, r, seq in make_curves(seed, maxc=40):
        p = E.p; L = legendre_table(p)
        for n, (fn, D, epsf) in G.items():
            f = np.zeros(r)
            for k in range(1, r):
                x, y = seq[k]; f[k] = L[fn(x,y,p) % p]
            F = np.fft.fft(f)[1:]
            m = np.abs(F + epsf(L, p)).max() / math.sqrt(p)
            worst[n] = max(worst[n], m)
for n, (fn, D, e) in G.items():
    print('g=%-8s D=%d  max_c |F+eps|/sqrt(p) = %.3f  %s' % (n, D, worst[n], 'OK' if worst[n] <= D else 'VIOLATION'))
