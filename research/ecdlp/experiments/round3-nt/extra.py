"""ECDLP-8: extra g's, autocorrelation A(R) variance, cos/sin split of the half-range DFT. Usage: python3 extra.py seed"""
import sys, math
import numpy as np
sys.path.insert(0, '../lib')
from mixed_sums import make_curves, legendre_table
G = {
 'x (deg2)': lambda x,y,p: x,
 'y (deg3)': lambda x,y,p: y,
 'y+1 (deg3)': lambda x,y,p: y+1,
 'x+y (deg3)': lambda x,y,p: x+y,
 'x(x+1) (deg4)': lambda x,y,p: x*(x+1),
 'x^2+1 (deg4)': lambda x,y,p: x*x+1,
 'x^2+x+1 (deg4)': lambda x,y,p: x*x+x+1,
 'x*y (deg5)': lambda x,y,p: x*y,
 'x^2*y (deg7)': lambda x,y,p: x*x*y,
 'x^3 (deg6, = x*x^2, equiv chi(x))': lambda x,y,p: x**3,
}
seed = int(sys.argv[1]) if len(sys.argv)>1 else 1
curves = make_curves(seed, maxc=40)
acc = {k: [] for k in G}
for E, r, seq in curves:
    p = E.p; L = legendre_table(p); h = (r-1)//2
    for name, fn in G.items():
        f = np.zeros(r)
        for k in range(1, r):
            x, y = seq[k]; f[k] = L[fn(x,y,p) % p]
        N = np.count_nonzero(f)
        F = np.fft.fft(f); I = np.abs(F[1:])**2 / N
        A = np.real(np.fft.ifft(F*F))
        A0 = A[0]
        VarA = (A[1:]**2).mean() / p           # E_R[A(R)^2]/p, R != 0
        s = f[1:h+1]; ks = np.arange(1, h+1)
        # cos/sin sums on r-grid, a = 1..r-1 (a<=h suffices by symmetry for cos)
        Xr = np.fft.fft(np.concatenate([[0], s, np.zeros(r-h-1)]))[1:r]
        C = Xr.real; S = -Xr.imag
        Nh = np.count_nonzero(s)
        Ih = np.abs(Xr)**2 / Nh
        acc[name].append((I.var(), (I**2).mean(), A0/N, VarA, Ih.var(),
                          (C**2).var()/Nh**2, (S**2).var()/Nh**2, np.corrcoef(C**2, S**2)[0,1], (C**2).mean()/Nh, (S**2).mean()/Nh))
print('seed', seed, 'n_curves', len(curves))
print('%-34s %7s %7s %7s %8s %8s %8s %8s %7s %7s %7s' % ('g','varI','M4','A0/N','EA2/p','varHalf','vC2/h2','vS2/h2','corrCS','EC2/h','ES2/h'))
for name, v in acc.items():
    m = np.mean(v, axis=0)
    print('%-34s %7.3f %7.3f %7.3f %8.3f %8.3f %8.3f %8.3f %7.3f %7.3f %7.3f' % ((name,)+tuple(m)))
