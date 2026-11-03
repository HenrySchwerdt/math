"""Round 8 critic part 2: p=5,r=7 counterexample; N=p boundary; anomalous r=p x-only symmetric stress."""
import sys, random, math, importlib.util
sys.path.insert(0, 'research/ecdlp/experiments/lib'); sys.path.insert(0, 'research/ecdlp/experiments/round8-review')
from toyec import Curve, is_prime
import io, contextlib
src = open('research/ecdlp/experiments/round8-review/crit_check.py').read().split("viol = []")[0]
exec(src)
random.seed(77)
# (a) p=5 curves with a point of order 7
for a in range(5):
    for b in range(5):
        try: E = Curve(a,b,5)
        except ValueError: continue
        if E.order() == 7:
            P = E.points()[1]; print('p=5 curve', a, b, 'order 7; P order', E.point_order(P))
            pts = [E.mul(1,P), E.mul(6,P)]
            print('  1P,6P', pts, ' f=1 : f(1P)=1=1 mod5, f(6P)=1=6 mod 5 ; T_5=1 => bound deg f>=1/2 violated by deg 0')
            break
    else: continue
    break
# (b) boundary N=p: exhaustive-ish: all subsets A of {1..p} for small p, curves with r>=p
bad = 0; cnt = 0
for p in (5, 7, 11):
    for a in range(p):
        for b in range(p):
            try: E = Curve(a,b,p)
            except ValueError: continue
            n = E.order()
            for r in [q for q in range(p, n+1) if n % q == 0 and is_prime(q)]:
                P = next(E.mul(n//r, Q) for Q in E.points() if Q is not None and E.mul(n//r, Q) is not None)
                N = p  # boundary N = p (<= r)
                if N == r: N = p  # k=r gives O; skip those A containing r
                kp = {k: E.mul(k,P) for k in range(1, N+1)}
                for mask in range(1, 1 << N):
                    A = [k for k in range(1, N+1) if mask >> (k-1) & 1]
                    if len(A) < 2 or any(kp[k] is None for k in A): continue
                    pts = [kp[k] for k in A]; vals = [k % p for k in A]
                    d = min_poly_order(p, pts, vals, 3*len(A)+6)
                    mT = max(Tj(A,j) for j in range(1,N))
                    cnt += 1
                    if d is not None and d < mT/2: bad += 1; print('VIOL N=p', p,a,b,r,A,d)
print('N=p boundary cases', cnt, 'violations', bad)
# (c) anomalous r=p: x-only g with symmetric A
viol = 0; tested = 0; worst = None
for p in (7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43):
    for a in range(p):
        for b in range(p):
            try: E = Curve(a,b,p)
            except ValueError: continue
            if E.order() != p: continue
            P = next(Q for Q in E.points() if Q is not None)
            kp = {k: E.mul(k,P) for k in range(1,p)}
            for N in range(p//2, p):
                for _ in range(8):
                    base = sorted(random.sample(range(1, N+1), random.randint(3, N)))
                    A = sorted(set(base) | {p-k for k in base if p-k <= N})
                    pts = [kp[k] for k in A]
                    dg = min_g_deg(p, [q[0] for q in pts], [k*k % p for k in A])
                    if dg is None: continue
                    tested += 1
                    mS = max(Sj(A,j) for j in range(1,N))
                    ratio = dg/(mS/3) if mS else None
                    if worst is None or (ratio is not None and ratio < worst[0]): worst = (ratio, p, N, A, dg, mS)
                    if dg < mS/3 - 1e-9: viol += 1; print('VIOL (2) anomalous', p, a, b, N, A, dg, mS)
print('anomalous symmetric x-only tests', tested, 'violations', viol, 'worst ratio deg/(maxS/3)', worst)
