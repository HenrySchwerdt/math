"""Exhaustive check over ALL (A,x0,y0) in F_p^3 (B := y0^2-x0^3-A x0, nonsingular curves, nodes x(kP), k<=N distinct,
all kP != O): fraction with c_{N-1}=0 (target k and k^2). Compares to the Schwartz-Zippel-type bound (Thm D) and to 1/p.
Also real scan: existence of real curves with c_2=0 (target k), so 'generic' cannot be dropped in char 0. Stdlib."""
import sys
def run(p, Nmax):
    cnt = {N: [0, 0, 0] for N in range(3, Nmax+1)}   # total valid, bad k, bad k^2
    for A in range(p):
        for x0 in range(p):
            for y0 in range(1, p):
                B = (y0*y0 - x0**3 - A*x0) % p
                if (4*A**3 + 27*B*B) % p == 0: continue
                xs = [x0]; R = (x0, y0); ok = True
                lam = (3*x0*x0 + A) * pow(2*y0, -1, p) % p
                x3 = (lam*lam - 2*x0) % p; R = (x3, (lam*(x0-x3)-y0) % p); xs.append(x3)
                for _ in range(Nmax-2):
                    if R[0] == x0: ok = False; break
                    lam = (R[1]-y0) * pow(R[0]-x0, -1, p) % p
                    x3 = (lam*lam - x0 - R[0]) % p
                    R = (x3, (lam*(x0-x3)-y0) % p); xs.append(x3)
                if not ok: continue
                for N in range(3, Nmax+1):
                    sub = xs[:N]
                    if len(set(sub)) < N: continue
                    cnt[N][0] += 1
                    for t, vals in ((1, list(range(1, N+1))), (2, [k*k % p for k in range(1, N+1)])):
                        c = list(vals)
                        for lvl in range(1, N):
                            c = [(c[i+1]-c[i]) * pow(sub[i+lvl]-sub[i], -1, p) % p for i in range(len(c)-1)]
                        if c[0] == 0: cnt[N][t] += 1
    return cnt
for p in (31, 43):
    cnt = run(p, 8)
    print("p =", p, "(1/p = %.4f)" % (1/p))
    for N, (tot, bk, bk2) in cnt.items():
        print("  N=%d valid=%d  frac_bad(k)=%.4f  frac_bad(k^2)=%.4f   N^4/(3p)=%.2f" % (N, tot, bk/tot, bk2/tot, N**4/(3*p)))
# real scan for c_2 = 0 (target k): x1 + x3 = 2 x2, P=(1,1), B=-A
from fractions import Fraction as Fr
def x123(A):
    A = Fr(A); P = (Fr(1), Fr(1)); lam = (3+A)/2; x2 = lam*lam-2; R = (x2, lam*(1-x2)-1)
    lam = (R[1]-1)/(R[0]-1); x3 = lam*lam-1-R[0]; return Fr(1), x2, x3
vals = []
for i in range(-60, 61):
    A = Fr(i, 10)
    try: a, b, c = x123(A); vals.append((float(A), float(a+c-2*b)))
    except ZeroDivisionError: pass
sc = [(vals[i][0], vals[i+1][0]) for i in range(len(vals)-1) if vals[i][1]*vals[i+1][1] < 0]
print("real scan, P=(1,1), B=-A, sign changes of x1+x3-2x2 for A in", sc[:6])
