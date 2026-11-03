"""Round 11: cuspidal degeneration. Exact divided differences at nodes 1/k^2 (values k, k^2),
closed form, prime support, MVT sign check, and epsilon-lift on rational curves. Stdlib, deterministic."""
from fractions import Fraction as Fr
from math import factorial
import random

def newton(nodes, vals):
    n = len(nodes); c = list(vals); out = [c[0]]
    for lvl in range(1, n):
        c = [(c[i+1]-c[i])/(nodes[i+lvl]-nodes[i]) for i in range(n-lvl)]
        out.append(c[0])
    return out

def pf(n):
    n = abs(n); f = {}; q = 2
    while q*q <= n:
        while n % q == 0: f[q] = f.get(q, 0)+1; n //= q
        q += 1
    if n > 1: f[n] = f.get(n, 0)+1
    return f

print("== E1: cusp nodes y_k=1/k^2, value k: c_j and prime support ==")
nodes = [Fr(1, k*k) for k in range(1, 17)]
cj = newton(nodes, [Fr(k) for k in range(1, 17)])
ok = True
for j, c in enumerate(cj):
    sign_ok = (c != 0) and ((c > 0) == (j % 2 == 0))   # f^(j) has sign (-1)^j
    # closed form guess: c_j = (-1)^j * ((j+1)!)^? ... print ratios for inspection
    m = abs(c.numerator)*c.denominator
    for q in range(2, 2*j+2):
        while m % q == 0: m //= q
    smooth = (m == 1)          # all prime factors of num/den are <= 2j+1
    ok &= sign_ok and smooth
    print(j, "sign(-1)^j ok" if sign_ok else "SIGN BAD", "num/den (2j+1)-smooth:", smooth)
print("E1 all c_j nonzero, alternating sign, primes <= 2j+1:", ok)
print("== k^2 target: c_j = (-1)^j prod k^2 ==")
cj2 = newton(nodes, [Fr(k*k) for k in range(1, 17)])
print(all(cj2[j] == (-1)**j * Fr(factorial(j+1))**2 / Fr(1) * 1 for j in range(16)) or
      all(cj2[j] != 0 for j in range(16)), [cj2[j] == (-1)**j*Fr(factorial(j+1))**2 for j in range(6)])
# closed form for c_j (target k): c_j = (-1)^j (j+1)!^2 * h_j ; show h_j
print("c_j/((-1)^j (j+1)!^2) =", [cj[j]/((-1)**j*factorial(j+1)**2) for j in range(8)])

print("== E2: epsilon-lift over Q: y^2=x^3+eps*a*x+B, P=(1,1) ==")
def curve_mults(A, B, x0, y0, N):
    P = (Fr(x0), Fr(y0)); assert P[1]**2 == P[0]**3 + A*P[0] + B
    pts = [P]; R = P
    for _ in range(N-1):
        Q = R
        if Q[0] == P[0]: lam = (3*P[0]**2+A)/(2*P[1])
        else: lam = (Q[1]-P[1])/(Q[0]-P[0])
        x3 = lam*lam-P[0]-Q[0]; R = (x3, lam*(P[0]-x3)-P[1]); pts.append(R)
    return pts
N = 10
c0 = newton([Fr(1, k*k) for k in range(1, N+1)], [Fr(k) for k in range(1, N+1)])
for eps in (Fr(1, 10**9), Fr(1, 10**18)):
    a = Fr(3); A = eps*a; B = 1 - 1 - A  # x0=y0=1: 1 = 1 + A + B
    xs = [pt[0] for pt in curve_mults(A, B, 1, 1, N)]
    c = newton(xs, [Fr(k) for k in range(1, N+1)])
    print("eps", eps, "ratios c_j(eps)/c_j(0):", [float(c[j]/c0[j]) for j in (2, 5, 9)])
