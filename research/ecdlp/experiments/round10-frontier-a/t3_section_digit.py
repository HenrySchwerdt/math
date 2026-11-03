"""T3: complexity of second p-adic digit of the homomorphic section of E(Z/p^2) -> E(F_p)."""
import sys, random
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime

def rcb_add(P, Q, a, b3, M):
    X1,Y1,Z1 = P; X2,Y2,Z2 = Q
    t0=X1*X2%M; t1=Y1*Y2%M; t2=Z1*Z2%M; t3=(X1+Y1)%M; t4=(X2+Y2)%M
    t3=t3*t4%M; t4=(t0+t1)%M; t3=(t3-t4)%M; t4=(X1+Z1)%M; t5=(X2+Z2)%M
    t4=t4*t5%M; t5=(t0+t2)%M; t4=(t4-t5)%M; t5=(Y1+Z1)%M; X3=(Y2+Z2)%M
    t5=t5*X3%M; X3=(t1+t2)%M; t5=(t5-X3)%M; Z3=a*t4%M; X3=b3*t2%M
    Z3=(X3+Z3)%M; X3=(t1-Z3)%M; Z3=(t1+Z3)%M; Y3=X3*Z3%M; t1=(t0+t0)%M
    t1=(t1+t0)%M; t2=a*t2%M; t4=b3*t4%M; t1=(t1+t2)%M; t2=(t0-t2)%M
    t2=a*t2%M; t4=(t4+t2)%M; t0=t1*t4%M; Y3=(Y3+t0)%M; t0=t5*t4%M
    X3=t3*X3%M; X3=(X3-t0)%M; t0=t3*t1%M; Z3=t5*Z3%M; Z3=(Z3+t0)%M
    return (X3,Y3,Z3)

def mul(k, P, a, b3, M):
    R = (0,1,0)
    while k:
        if k & 1: R = rcb_add(R, P, a, b3, M)
        P = rcb_add(P, P, a, b3, M)
        k >>= 1
    return R

def lift_point(pt, A, B, p):
    x, y0 = pt
    M = p*p
    f = (x**3 + A*x + B) % M
    # Hensel: y = y0 + p t, y^2 = y0^2 + 2 y0 p t = f mod p^2
    r = ((f - y0*y0) // p) % p if (f - y0*y0) % p == 0 else None
    assert r is not None
    t = r * pow(2*y0, -1, p) % p
    y = (y0 + p*t) % M
    assert (y*y - f) % M == 0
    return (x, y, 1)

def bm(s, p):
    C=[1]; B=[1]; L=0; m=1; b=1
    for n in range(len(s)):
        d = s[n]
        for i in range(1, L+1):
            d = (d + C[i]*s[n-i]) % p
        if d == 0:
            m += 1
        else:
            T = C[:]
            coef = d * pow(b, -1, p) % p
            if len(C) < len(B)+m: C += [0]*(len(B)+m-len(C))
            for i in range(len(B)):
                C[i+m] = (C[i+m] - coef*B[i]) % p
            if 2*L <= n:
                L = n+1-L; B = T; b = d; m = 1
            else:
                m += 1
    return L

def holonomic(s, p, order, deg, window=None):
    """search nonzero (c_i(k)) with sum_i c_i(k) s[k+i]=0; return (found, nullity, validated_out_of_window)."""
    n = len(s) - order
    unk = (order+1)*(deg+1)
    W = window or min(n, 4*unk+20)
    def row(k):
        return [pow(k, j, p)*s[k+i] % p for i in range(order+1) for j in range(deg+1)]
    rows = [row(k) for k in range(1, 1+W)]
    # gaussian elimination -> nullspace
    mat = [r[:] for r in rows]; piv = []; r = 0
    for c in range(unk):
        pr = None
        for i in range(r, len(mat)):
            if mat[i][c]: pr = i; break
        if pr is None: continue
        mat[r], mat[pr] = mat[pr], mat[r]
        inv = pow(mat[r][c], -1, p); mat[r] = [v*inv % p for v in mat[r]]
        for i in range(len(mat)):
            if i != r and mat[i][c]:
                f = mat[i][c]; mat[i] = [(vi - f*vr) % p for vi, vr in zip(mat[i], mat[r])]
        piv.append(c); r += 1
    free = [c for c in range(unk) if c not in piv]
    if not free: return (False, 0, False)
    c0 = free[0]
    vec = [0]*unk; vec[c0] = 1
    for i, pc in enumerate(piv): vec[pc] = (-mat[i][c0]) % p
    ok = all(sum(a*b for a, b in zip(row(k), vec)) % p == 0 for k in range(1+W, 1+n-1))
    return (True, len(free), ok)

def run(p0, seed):
    rnd = random.Random(seed)
    p = p0
    while True:
        p += 1
        if not is_prime(p): continue
        for _ in range(60):
            a = rnd.randrange(1, p); b = rnd.randrange(1, p)
            try: E = Curve(a, b, p)
            except ValueError: continue
            N = E.order()
            if is_prime(N) and N != p and N > 100: break
        else: continue
        break
    M = p*p
    A = (a + p*rnd.randrange(p)) % M; B = (b + p*rnd.randrange(p)) % M
    b3 = 3*B % M
    m = pow(p, -1, N)
    pts = E.points() if hasattr(E, 'points') else None
    # random generator
    while True:
        x = rnd.randrange(p)
        rhs = (x**3 + a*x + b) % p
        ys = [y for y in range(p) if y*y % p == rhs] if p < 5000 else None
        if ys is None:
            from math import isqrt
            if pow(rhs, (p-1)//2, p) != 1: continue
            # tonelli via brute for p%4==3 else brute force
            y0 = None
            if p % 4 == 3: y0 = pow(rhs, (p+1)//4, p)
            else:
                y0 = next(y for y in range(p) if y*y % p == rhs)
            ys = [y0]
        if ys and ys[0] != 0: P = (x, ys[0]); break
    def sect(k):
        R = E.mul(k, P)
        if R is None: return None
        Rt = lift_point(R, A, B, p)
        S = mul(p*m, Rt, A, b3, M)
        X, Y, Z = S
        assert Z % p != 0
        zi = pow(Z, -1, M)
        return (X*zi % M, Y*zi % M, R)
    # sanity: group law match F_p
    for _ in range(50):
        k1, k2 = rnd.randrange(1, N), rnd.randrange(1, N)
        R1 = lift_point(E.mul(k1, P), A, B, p); R2 = lift_point(E.mul(k2, P), A, B, p)
        S = rcb_add(R1, R2, A, b3, M)
        Z = S[2]
        assert Z % p
        xs = S[0]*pow(Z, -1, M) % M
        R3 = E.mul(k1+k2, P)
        assert R3 is not None and xs % p == R3[0]
    # homomorphism + on-curve + reduction
    for _ in range(200):
        k1, k2 = rnd.randrange(1, N), rnd.randrange(1, N)
        s1 = sect(k1); s2 = sect(k2); s3 = sect((k1+k2) % N)
        if s3 is None or s1 is None or s2 is None: continue
        S = rcb_add((s1[0], s1[1], 1), (s2[0], s2[1], 1), A, b3, M)
        zi = pow(S[2], -1, M)
        assert (S[0]*zi - s3[0]) % M == 0 and (S[1]*zi - s3[1]) % M == 0, 'homomorphism fails'
        assert (s1[1]**2 - (s1[0]**3 + A*s1[0] + B)) % M == 0
        assert (s1[0] - s1[2][0]) % p == 0 and (s1[1] - s1[2][1]) % p == 0
    u = []; v = []
    for k in range(1, N):
        s = sect(k)
        u.append(((s[0] - s[2][0]) // p) % p); v.append(((s[1] - s[2][1]) // p) % p)
    return p, a, b, N, u, v

if __name__ == '__main__':
    p0 = int(sys.argv[1]); seed = int(sys.argv[2])
    p, a, b, N, u, v = run(p0, seed)
    n = len(u)
    print(f'p={p} a={a} b={b} N={N} seed={seed} sanity checks passed (homomorphism, on-curve, reduction)')
    rnd = random.Random(1000+seed)
    rand_seq = [rnd.randrange(p) for _ in range(n)]
    g = 3
    ctrl1 = [(5*k+7) % p for k in range(1, N)]
    ctrl2 = [k*pow(g, k, p) % p for k in range(1, N)]
    for name, s in [('u=dx digit', u), ('v=dy digit', v), ('random(neg ctrl)', rand_seq), ('ck+d (pos ctrl)', ctrl1), ('k*g^k (pos ctrl)', ctrl2)]:
        L = bm(s, p)
        hol = {}
        for (o, d) in [(1,1),(1,3),(2,2),(3,3)]:
            hol[(o,d)] = holonomic(s, p, o, d)
        print(f'{name:18s} n={n} BM L={L} L/n={L/n:.3f} holonomic(order,deg)->(found,nullity,validated): {hol}')
