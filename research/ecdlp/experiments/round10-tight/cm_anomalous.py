"""Verify the structural lemma for anomalous j=0 curves (r=p, p=1 mod 3, N=(p-1)/2, target k^2):
g(zeta X) = lambda^2 g(X) where omega(x,y)=(zeta x,y), omega P = lambda P, so supp(g) is in {i = s mod 3}, zeta^s = lambda^2,
and hence deg g <= N-3+s.  Also reports exact mindeg.  stdlib only; deterministic enumeration (no seed needed)."""
import sys
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime

def interp_coeffs(xs, vals, p):
    """monomial coefficients (low->high) of the interpolant of degree < len(xs) via Newton form."""
    n = len(xs); d = list(vals); c = [d[0]]
    for j in range(1, n):
        d = [(d[i+1]-d[i]) * pow(xs[i+j]-xs[i], -1, p) % p for i in range(n-j)]
        c.append(d[0])
    poly = [0]  # Horner in Newton form
    for j in range(n-1, -1, -1):
        # poly = poly*(X - xs[j]) + c[j]
        new = [0]*(len(poly)+1)
        for i, a in enumerate(poly):
            new[i+1] = (new[i+1] + a) % p
            new[i] = (new[i] - a*xs[j]) % p
        new[0] = (new[0] + c[j]) % p
        poly = new
    while len(poly) > 1 and poly[-1] == 0: poly.pop()
    return poly

tot = ok = forced = 0; table = {}
for p in range(7, 500):
    if not is_prime(p) or p % 3 != 1: continue
    zeta = next(z for z in range(2, p) if pow(z, 3, p) == 1)
    for b in range(1, p):
        E = Curve(0, b, p); pts = E.points()
        if len(pts) != p: continue          # anomalous
        P = pts[1]; N = (p-1)//2
        xs = []; Q = None
        for k in range(1, N+1):
            Q = E.add(Q, P); xs.append(Q[0])
        k0 = next(k for k in range(1, N+1) if xs[k-1] == zeta * xs[0] % p)   # x(k0 P) = zeta x(P) so lambda = +-k0
        lam2 = k0*k0 % p
        s = next(s for s in range(3) if pow(zeta, s, p) == lam2)
        g = interp_coeffs(xs, [k*k % p for k in range(1, N+1)], p)
        supp = [i for i, a in enumerate(g) if a]
        good = all(i % 3 == s for i in supp)
        tot += 1; ok += good
        dg = len(g)-1
        assert dg <= N-3+s
        table.setdefault((s, N-1-dg), 0); table[(s, N-1-dg)] += 1
print('anomalous j=0 cases', tot, 'support-lemma holds', ok)
print('(s, deficit N-1-mindeg) -> count', sorted(table.items()))
