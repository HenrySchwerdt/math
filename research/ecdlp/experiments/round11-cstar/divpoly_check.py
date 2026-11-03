"""Check (seeded, mod p): (i) x(mP) = x - psi_{m-1}psi_{m+1}/psi_m^2; (ii) x_i-x_l = -psi_{i+l}psi_{i-l}/(psi_i^2 psi_l^2);
(iii) cusp values psi_m(A=B=0) = m * monomial (nonzero for p>m); (iv) weight formula for numerator degree vs actual weights."""
import random
def psis(A, B, x, y, M, p):
    ps = {0: 0, 1: 1, 2: 2*y % p, 3: (3*x**4+6*A*x*x+12*B*x-A*A) % p,
          4: 4*y*(x**6+5*A*x**4+20*B*x**3-5*A*A*x*x-4*A*B*x-8*B*B-A**3) % p}
    for m in range(5, M+1):
        if m % 2:
            n = (m-1)//2; ps[m] = (ps[n+2]*ps[n]**3 - ps[n-1]*ps[n+1]**3) % p
        else:
            n = m//2; ps[m] = (ps[n]*(ps[n+2]*ps[n-1]**2 - ps[n-2]*ps[n+1]**2)) * pow(2*y, -1, p) % p
    return ps
random.seed(11); p = 10007; bad = 0; tests = 0
for _ in range(40):
    A, x, y = (random.randrange(p) for _ in range(3)); B = (y*y-x**3-A*x) % p
    # point multiples by group law
    def add(P, Q):
        if P[0] == Q[0]:
            lam = (3*P[0]**2+A)*pow(2*P[1], -1, p) % p
        else: lam = (Q[1]-P[1])*pow(Q[0]-P[0], -1, p) % p
        x3 = (lam*lam-P[0]-Q[0]) % p; return (x3, (lam*(P[0]-x3)-P[1]) % p)
    P = (x, y); mult = {1: P}
    try:
        for m in range(2, 8): mult[m] = add(mult[m-1], P)
        ps = psis(A, B, x, y, 16, p)
        for m in range(2, 8):
            assert mult[m][0] == (x - ps[m-1]*ps[m+1]*pow(ps[m]**2, -1, p)) % p; tests += 1
        for i in range(2, 8):
            for l in range(1, i):
                lhs = (mult[i][0]-mult[l][0]) % p
                rhs = -ps[i+l]*ps[i-l]*pow(ps[i]**2*ps[l]**2, -1, p) % p
                assert lhs == rhs; tests += 1
    except (ZeroDivisionError, ValueError): pass
print("identities (i),(ii) checked:", tests, "assertions OK")
ps = psis(0, 0, 1, 1, 20, p)
print("cusp psi_m(x=y=1) == m (mod p) for m<=20:", all(ps[m] == m for m in range(1, 21)))
# (iv) weight of numerator terms: 2(N-1)S2-(N-1)(N+2); degree bound w_N
for N in (2, 3, 4, 8, 16, 100):
    S2 = N*(N+1)*(2*N+1)//6; wt = 2*(N-1)*S2-(N-1)*(N+2); print("N", N, "weight", wt, "deg<=", wt//2, "N^4/3 =", round(N**4/3))
