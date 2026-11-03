# Control: #E = 2r (one rational 2-torsion point T1=(e1,0)), psi of odd prime order r (trivial on T1), g=y.
# Derivation: y(Q+T1) = -B*y(Q)/(x(Q)-e1)^2 with B=f'(e1)  => S(psi) = chi(-B) S(psi)  => S=0 if chi(-B)=-1.
import random, json, numpy as np
from common import *
SEED = 20261106; rng = random.Random(SEED); random.seed(SEED)
stats = {+1: [], -1: []}
for p in [q for q in range(500, 3000) if is_prime(q)][::7]:
    L = legendre_table(p)
    for _ in range(300):
        a, b = rng.randrange(p), rng.randrange(p)
        if (4*a**3+27*b**2) % p == 0: continue
        n = count_points(a, b, p, L)
        if n % 2 or not is_prime(n//2) or n//2 < 5: continue
        roots = [e for e in range(p) if (e**3+a*e+b) % p == 0]
        if len(roots) != 1: continue
        e1 = roots[0]; B = (3*e1*e1 + a) % p
        s = int(L[(-B) % p]); E = Curve(a, b, p)
        # generator of order 2r: random point, check order
        while True:
            x = random.randrange(p); rhs = (x**3+a*x+b) % p
            if L[rhs] == 1:
                y = next(y for y in range(p) if y*y % p == rhs); P = (x, y)
                if E.mul(n//2, P) is not None and E.mul(2, P) is not None: break
        pts = [None]; Q = None
        for k in range(1, n):
            Q = E.add(Q, P); pts.append(Q)
        assert E.add(Q, P) is None
        seq = np.array([0 if Q is None else int(L[Q[1] % p]) for Q in pts], dtype=float)
        r = n//2
        # psi(kP) = e(c k / r): FFT of length n at frequencies 2c (c=1..r-1)
        F = np.fft.fft(seq)[[2*c for c in range(1, r)]] / np.sqrt(p)
        stats[s].append((p, np.abs(F).max(), float((np.abs(F)**2).mean()), float((np.abs(F)**4).mean())))
        break
for s, v in stats.items():
    if v: print(json.dumps(dict(chi_minusB=s, curves=len(v), max_abs_Y=round(max(t[1] for t in v), 6), mean_m2=round(float(np.mean([t[2] for t in v])), 4), mean_m4=round(float(np.mean([t[3] for t in v])), 4))))
