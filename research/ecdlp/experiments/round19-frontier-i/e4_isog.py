"""E4: isogeny-invariance check + class statistics (weakness probability, conductor/ascent cost)."""
import sys, random, json, os
from math import isqrt, gcd, log2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from toyec import Curve, is_prime

def factor(n):
    f = {}; d = 2
    while d * d <= n:
        while n % d == 0: f[d] = f.get(d, 0) + 1; n //= d
        d += 1
    if n > 1: f[n] = f.get(n, 0) + 1
    return f

def fund_disc(n):
    """n = 4p - t^2 > 0 ; return (|d_K|, f) with -n = d_K f^2, d_K fundamental."""
    fa = factor(n); s = 1; f = 1
    for pr, e in fa.items():
        if e % 2: s *= pr
        f *= pr ** (e // 2)
    # -n = -s f^2 ; -s fundamental iff -s = 1 mod 4
    if (-s) % 4 == 1: return s, f
    return 4 * s, f * 1 // 2 if f % 2 == 0 else None  # placeholder fixed below

def dK_f(n):
    fa = factor(n); s = 1; f = 1
    for pr, e in fa.items():
        if e % 2: s *= pr
        f *= pr ** (e // 2)
    if (-s) % 4 == 1: return s, f
    # d_K = -4s, n = 4 s f^2 /4.. : -n = -s f^2 = (-4 s) (f/2)^2 requires f even
    # if f odd then -s*f^2 with -s = 3 mod 4: -n = 3 mod 4 impossible since n = 4p - t^2 = 0 or 3 mod 4 -> consistent: n=3 mod4 => s f^2 = 3 mod 4 -> -s=1 mod 4 contradiction handled above
    assert f % 2 == 0, (n, s, f)
    return 4 * s, f // 2

def kron_class_number(n):
    """number of reduced positive definite forms (a,b,c), b^2-4ac=-n, all (not nec primitive)."""
    cnt = 0
    amax = isqrt(n // 3) + 1
    for a in range(1, amax + 1):
        for b in range(-a + 1, a + 1):
            if (b * b + n) % (4 * a): continue
            c = (b * b + n) // (4 * a)
            if c < a: continue
            if c == a and b < 0: continue
            cnt += 1
    return cnt

def class_stats(p, prime_only):
    """returns weighted list of (t, N_t, dK, f, r)"""
    out = []
    for t in range(-isqrt(4 * p), isqrt(4 * p) + 1):
        n = 4 * p - t * t
        if n <= 0: continue
        r = p + 1 - t
        if prime_only and not is_prime(r): continue
        Nt = kron_class_number(n) if True else None
        d, f = dK_f(n)
        out.append((t, Nt, d, f, r))
    return out

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'INV':   # explicit Velu 2-isogenies keep #E, order r, embedding degree, and transport the dlog
        rng = random.Random(int(sys.argv[2])); tested = 0; bad = 0; transported = 0; steps = 0
        for trial in range(int(sys.argv[3])):
            p = rng.choice([q for q in range(300, 2000) if is_prime(q)])
            a, b = rng.randrange(p), rng.randrange(p)
            try: E = Curve(a, b, p)
            except ValueError: continue
            pts = E.points(); N0 = len(pts)
            cur = E; curpts = pts
            # pick point of odd prime order r | N0
            fa = factor(N0); r = max(fa)
            if r < 5: continue
            P0 = None
            for _ in range(50):
                R = rng.choice(curpts)
                if R is not None:
                    P0 = cur.mul(N0 // r, R)
                    if P0 is not None: break
            if P0 is None: continue
            k = rng.randrange(1, r); Q0 = cur.mul(k, P0)
            Pc, Qc = P0, Q0
            for step in range(4):
                # rational 2-torsion roots
                roots = [x for x in range(p) if (x ** 3 + cur.a * x + cur.b) % p == 0]
                if not roots: break
                x0 = rng.choice(roots); t = (3 * x0 * x0 + cur.a) % p
                A2 = (cur.a - 5 * t) % p; B2 = (cur.b - 7 * x0 * t) % p
                try: E2 = Curve(A2, B2, p)
                except ValueError: break
                def phi(Pt):
                    if Pt is None: return None
                    x, y = Pt
                    if x == x0: return None
                    inv = pow(x - x0, -1, p)
                    return ((x + t * inv) % p, y * (1 - t * inv * inv) % p)
                P2, Q2 = phi(Pc), phi(Qc)
                pts2 = E2.points(); tested += 1; steps += 1
                same_order = (len(pts2) == N0)
                # embedding degree of r in F_p^* is order of p mod r: depends only on (p, r)
                ok_map = (P2 is not None and E2.on_curve(P2) and E2.mul(k, P2) == Q2 and E2.mul(r, P2) is None)
                if not same_order: bad += 1
                transported += ok_map
                cur, curpts, Pc, Qc = E2, pts2, P2, Q2
                if P2 is None: break
        print(json.dumps(dict(mode='INV', isogeny_steps_tested=tested, order_changed=bad, dlog_transported_ok=transported)))
    elif mode == 'CM':   # exact CM weight Sum_t N_t / (2p+6) for d_K in {-3,-4}; no full-trace sweep
        for p in [int(x) for x in sys.argv[2].split(',')]:
            w3 = w4 = 0; rows = []
            for t in range(-isqrt(4 * p), isqrt(4 * p) + 1):
                n = 4 * p - t * t
                if n <= 0: continue
                d, f = dK_f(n)
                if d in (3, 4):
                    Nt = kron_class_number(n)
                    if d == 3: w3 += Nt
                    else: w4 += Nt
                    rows.append((t, d, f, Nt, sum(e * l for l, e in factor(f).items()), (max(factor(f)) if f > 1 else 1)))
            print(json.dumps(dict(p=p, p_mod_12=p % 12, P_dK3=w3 / (2 * p), P_dK4=w4 / (2 * p), P_cm=(w3 + w4) / (2 * p),
                  sqrt_p=isqrt(p), n_cm_traces=len(rows), min_ascent_cost=min((r[4] for r in rows), default=None),
                  frac_cm_traces_ascent_lt_sqrtp=(sum(1 for r in rows if r[4] < isqrt(p)) / len(rows)) if rows else None,
                  weight_frac_ascent_lt_sqrtp=(sum(r[3] for r in rows if r[4] < isqrt(p)) / max(1, sum(r[3] for r in rows))))))
    else:  # STAT p-list
        ps = [int(x) for x in sys.argv[2].split(',')]
        prime_only = sys.argv[3] == 'prime'
        for p in ps:
            st = class_stats(p, prime_only)
            tot = sum(x[1] for x in st)
            def frac(pred): return sum(x[1] for x in st if pred(x)) / tot
            rec = dict(p=p, prime_only=prime_only, total_classes=tot, n_traces=len(st),
                       P_dK3=frac(lambda x: x[2] == 3), P_dK4=frac(lambda x: x[2] == 4),
                       P_dK_le_100=frac(lambda x: x[2] <= 100), P_dK_le_1000=frac(lambda x: x[2] <= 1000),
                       P_dK_le_sqrtp=frac(lambda x: x[2] <= isqrt(p)),
                       median_dK_over_p=sorted((x[2] / p, x[1]) for x in st)[len(st) // 2][0],
                       P_f_gt1=frac(lambda x: x[3] > 1))
            # ascent cost for CM (d_K in {3,4}) classes: sum e*l over conductor f (Velu cost ~ l per prime step)
            cm = [x for x in st if x[2] in (3, 4)]
            rec['cm_traces'] = [dict(t=x[0], f=x[3], dK=-x[2], N_t=x[1], ascent_cost=sum(e * l for l, e in factor(x[3]).items()), max_prime_f=max(factor(x[3])) if x[3] > 1 else 1) for x in cm]
            print(json.dumps(rec))
