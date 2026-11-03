"""Round 8 critic: counterexample search for HYP-5da6025e bounds. Seeded, small p. Stdlib only."""
import sys, random, math
sys.path.insert(0, 'research/ecdlp/experiments/lib')
from toyec import Curve, is_prime
random.seed(8023)

def solvable(rows, rhs, p):
    """Is the system sum_c coeff[c]*rows[i][c] = rhs[i] solvable mod p? (rows: equations x unknowns)"""
    n = len(rows[0]) if rows else 0
    M = [r[:] + [b] for r, b in zip(rows, rhs)]
    rk = 0
    for c in range(n):
        piv = next((i for i in range(rk, len(M)) if M[i][c] % p), None)
        if piv is None: continue
        M[rk], M[piv] = M[piv], M[rk]
        inv = pow(M[rk][c], -1, p)
        M[rk] = [v * inv % p for v in M[rk]]
        for i in range(len(M)):
            if i != rk and M[i][c] % p:
                f = M[i][c]; M[i] = [(a - f * b) % p for a, b in zip(M[i], M[rk])]
        rk += 1
    return all(any(v % p for v in row[:n]) or row[n] % p == 0 for row in M)

def basis_cols(pts, order_max):
    """monomials x^a y^b (b in 0,1) sorted by pole order 2a+3b, up to order_max; values at pts."""
    mons = sorted((2*a+3*b, a, b) for a in range(order_max//2+1) for b in (0,1) if 2*a+3*b <= order_max)
    return mons

def min_poly_order(p, pts, vals, cap):
    mons = basis_cols(pts, cap)
    for n in range(0, cap+1):
        use = [m for m in mons if m[0] <= n]
        rows = [[pow(x,a,p)*pow(y,b,p) % p for (_,a,b) in use] for (x,y) in pts]
        if solvable(rows, vals, p): return n
    return None

def min_rat_upper(p, pts, vals, cap, allx):
    """f=N/D(x), D=prod (x-c), c in allx not hit; deg f <= max(ord N, 2|C|). upper bound on rational degree."""
    hit = {x for x,_ in pts}
    free = [c for c in allx if c not in hit]
    best = min_poly_order(p, pts, vals, cap)
    for c in range(1, min(len(free), 5)+1):
        if 2*c >= (best if best is not None else cap+1): break
        for _ in range(6):
            C = random.sample(free, c)
            Dv = [math.prod((x-cc) for cc in C) % p for (x,_) in pts]
            tv = [v*d % p for v, d in zip(vals, Dv)]
            n = min_poly_order(p, pts, tv, cap)
            if n is not None:
                d = max(n, 2*c)
                if best is None or d < best: best = d
    return best

def min_g_deg(p, xs, vals):
    d = {}
    for x, v in zip(xs, vals):
        if d.setdefault(x, v) != v: return None
    X = list(d); V = [d[x] for x in X]
    for deg in range(len(X)):
        rows = [[pow(x, e, p) for e in range(deg+1)] for x in X]
        if solvable(rows, V, p): return deg
    return len(X)-1

def Tj(A, j): s = set(A); return sum(1 for k in A if k+j in s)
def Sj(A, j): s = set(A); return sum(1 for k in A if k-j in s and k+j in s)

def gen_A(N, kind):
    if kind == 'rand':
        m = random.randint(2, N); return sorted(random.sample(range(1,N+1), m))
    if kind == 'interval':
        m = random.randint(2, N); s = random.randint(1, N-m+1); return list(range(s, s+m))
    if kind == 'ap':
        d = random.randint(2, max(2,N//3)); s = random.randint(1, d); return list(range(s, N+1, d))
    if kind == 'dense':
        return sorted(set(range(1,N+1)) - set(random.sample(range(1,N+1), random.randint(0, N//4))))
    if kind == 'sym':  # symmetric about r/2 handled by caller
        return None

viol = []; stats = {'cases':0,'N_eq_p':0,'N_eq_r':0,'p_lt_r':0,'r_lt_p':0,'r_eq_p':0}
tight = []
primes = [q for q in range(5, 48) if is_prime(q)]
t0 = __import__('time').time()
for p in primes:
    for a in range(p):
        for b in range(p):
            if __import__('time').time()-t0 > 100: break
            if random.random() > 0.08: continue
            try: E = Curve(a, b, p)
            except ValueError: continue
            n = E.order(); pts_all = E.points()
            allx = list(range(p))
            # pick prime-order subgroup generator
            for r in [q for q in range(2, n+1) if n % q == 0 and is_prime(q)]:
                if r < 3: continue
                cand = [Q for Q in pts_all if Q is not None]
                random.shuffle(cand)
                P = next((E.mul(n//r, Q) for Q in cand if E.mul(n//r, Q) is not None), None)
                if P is None: continue
                mp = min(p, r)
                for N in sorted({mp, mp-1, max(2, mp//2), max(2,mp-2)}):
                    if N < 3: continue
                    kp = {k: E.mul(k, P) for k in range(1, N+1)}
                    for kind in ('rand','interval','ap','dense','rand'):
                        A = gen_A(N, kind)
                        if len(A) < 3: continue
                        pts = [kp[k] for k in A]
                        vals = [k % p for k in A]
                        if None in pts or len(set(pts)) < len(pts): continue
                        cap = 3*len(A)+6
                        dpoly = min_poly_order(p, pts, vals, cap)
                        drat = min_rat_upper(p, pts, vals, cap, allx)
                        maxT = max(Tj(A, j) for j in range(1, N))
                        T1 = Tj(A,1)
                        stats['cases'] += 1; stats['N_eq_p'] += (N==p); stats['N_eq_r'] += (N==r)
                        stats['p_lt_r'] += p<r; stats['r_lt_p'] += r<p; stats['r_eq_p'] += r==p
                        lb = math.ceil(maxT/2)
                        for name, d in (('poly', dpoly), ('rat_upper', drat)):
                            if d is not None and d < lb:
                                viol.append(('(1)', name, p, a, b, r, N, A, d, lb))
                        m = len(A); lb1b = math.ceil(m*(m-1)/(4*(N-1)))
                        if drat is not None and drat < lb1b: viol.append(('(1b)', p,a,b,r,N,A,drat,lb1b))
                        if dpoly is not None and dpoly < (2*m-N-1)/2: viol.append(('(1a)',p,a,b,r,N,A))
                        if dpoly is not None: tight.append((dpoly - lb, p, r, N, kind))
                        # x-only
                        xs = [pt[0] for pt in pts]; sq = [k*k % p for k in A]
                        dg = min_g_deg(p, xs, sq)
                        if dg is not None:
                            maxS = max([Sj(A,j) for j in range(1, N)] or [0])
                            if dg < maxS/3 - 1e-9:
                                viol.append(('(2)', p,a,b,r,N,A,dg,maxS))
                            if r == p and any((r-k) in set(A) for k in A): stats['x_sym_cases'] = stats.get('x_sym_cases',0)+1
print('stats', stats)
print('violations', len(viol))
for v in viol[:20]: print(v)
if tight:
    gaps = [t[0] for t in tight]; print('poly - ceil(maxT/2): min', min(gaps), 'max', max(gaps), 'zero-gap cases', sum(g==0 for g in gaps))
