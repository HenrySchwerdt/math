"""Explicit verification of the (2) counterexample (p=r=7) and the corrected class-count bound on anomalous curves."""
import sys, random
sys.path.insert(0, 'research/ecdlp/experiments/lib')
from toyec import Curve
src = open('research/ecdlp/experiments/round8-review/crit_check.py').read().split("viol = []")[0]
exec(src)
E = Curve(0,5,7); P = next(Q for Q in E.points() if Q is not None)
print('curve y^2=x^3+5 over F_7, #E =', E.order(), ' P =', P, ' order', E.point_order(P))
xs = {k: E.mul(k,P)[0] for k in range(1,7)}; print('x(kP):', xs)
for c1 in range(7):
    for c0 in range(7):
        if all((c1*xs[k]+c0 - k*k) % 7 == 0 for k in range(1,7)): print('g(X)=%d X + %d satisfies g(x(kP))=k^2 mod 7 for all k=1..6' % (c1,c0))
A = list(range(1,7)); print('N=6<min(p,r)=7, m=6, S_1 =', Sj(A,1), '=> claimed deg g >= 4/3, i.e. >=2; but deg g = 1')
# corrected bound: distinct x-classes among K_j
random.seed(5); viol = 0; n = 0
for p in (7,11,13,17,19,23,29,31,37,41,43):
    for a in range(p):
        for b in range(p):
            try: E = Curve(a,b,p)
            except ValueError: continue
            if E.order() != p: continue
            P = next(Q for Q in E.points() if Q is not None); kp = {k: E.mul(k,P) for k in range(1,p)}
            for N in range(p//2, p):
                for _ in range(8):
                    base = sorted(random.sample(range(1,N+1), random.randint(3,N)))
                    A = sorted(set(base) | {p-k for k in base if p-k <= N}); s = set(A)
                    dg = min_g_deg(p, [kp[k][0] for k in A], [k*k % p for k in A])
                    if dg is None: continue
                    best = 0
                    for j in range(1,N):
                        K = [k for k in A if k-j in s and k+j in s]
                        best = max(best, len({min(k, p-k) for k in K}))
                    n += 1
                    if dg < best/3 - 1e-9: viol += 1; print('VIOL corrected', p, N, A, dg, best)
print('corrected class-count bound deg g >= (#classes of K_j)/3: tests', n, 'violations', viol)
