"""Seeded check of the Theorem B identity (ECDLP-14).
g interpolates k^2 mod p at x(kP), k=1..(r-1)/2, deg g = D.  Define s,t via x_P=x(P):
  x(Q+P)+x(Q-P) = [2(x x_P + a)(x + x_P) + 4b]/(x-x_P)^2 ,  x(Q+P)x(Q-P) = [(x x_P - a)^2 - 4b(x+x_P)]/(x-x_P)^2.
Then g(x+)+g(x-) = 2 g(x) + 2 holds at x=x(kP) for 2<=k<=(r-3)/2 (x != x_P), so M(x)=N(x)-(2g(x)+2)(x-x_P)^(2D)
vanishes there; deg M = 3D (leading coeff 2 g_D != 0).  We check vanishing numerically and the formulas against E.add."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from toyec import Curve, is_prime
random.seed(20261103)

def poly_eval(c, x, p): # c low->high
    r = 0
    for a in reversed(c): r = (r * x + a) % p
    return r

def interp(xs, ys, p):
    n = len(xs); coeffs = [0] * n
    for i in range(n):
        num = [1]; den = 1
        for j in range(n):
            if j == i: continue
            num = [( (num[k-1] if k else 0) - xs[j] * (num[k] if k < len(num) else 0)) % p for k in range(len(num) + 1)]
            den = den * (xs[i] - xs[j]) % p
        f = ys[i] * pow(den, -1, p) % p
        for k in range(n): coeffs[k] = (coeffs[k] + f * num[k]) % p
    while len(coeffs) > 1 and coeffs[-1] == 0: coeffs.pop()
    return coeffs

tested = 0; bad = 0
for p in [31, 53, 67, 83, 101, 127, 151]:
    for trial in range(40):
        a, b = random.randrange(p), random.randrange(1, p)
        if (4 * a**3 + 27 * b * b) % p == 0: continue
        E = Curve(a, b, p); pts = E.points(); N = len(pts)
        rs = [q for q in range(7, N + 1) if is_prime(q) and N % q == 0 and q % 2 == 1]
        if not rs: continue
        r = max(rs); P = next((Q for Q in pts[1:] if E.mul(r, Q) is None), None)
        if P is None: continue
        xP = P[0]; Q = P; xs = []; 
        for k in range(1, (r - 1) // 2 + 1): xs.append(Q[0]); Q = E.add(Q, P)
        if len(set(xs)) != len(xs): continue
        g = interp(xs, [k * k % p for k in range(1, len(xs) + 1)], p); D = len(g) - 1
        if D < 1: continue
        for k in range(2, (r - 3) // 2 + 1):
            Qk = E.mul(k, P); x = Qk[0]
            xp = E.add(Qk, P)[0]; xm = E.add(Qk, E.neg(P))[0]
            d2 = pow((x - xP) ** 2, -1, p)
            s = (2 * (x * xP + a) * (x + xP) + 4 * b) * d2 % p
            t = ((x * xP - a) ** 2 - 4 * b * (x + xP)) * d2 % p
            assert (xp + xm - s) % p == 0 and (xp * xm - t) % p == 0, "addition formula mismatch"
            lhs = (poly_eval(g, xp, p) + poly_eval(g, xm, p)) % p
            rhs = (2 * poly_eval(g, x, p) + 2) % p
            tested += 1
            if lhs != rhs: bad += 1
print("pointwise identity checks:", tested, "failures:", bad)
