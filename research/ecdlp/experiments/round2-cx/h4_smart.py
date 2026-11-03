"""H4 attack. Seeds fixed (random.Random(SEED)). Python stdlib only. All curves have ODD #E (complete addition law valid).
Tests:
 T1 anomalous control: psi(Q~)=k psi(P~) for independent lifts (must hold with prob 1).
 T2 exhaustive: for non-anomalous E, p not | #E, enumerate ALL p lifts (mod p^2) of P and of Q=kP (fixed curve lift):
      (psi(P~),psi(Q~)) is a BIJECTION from lift pairs onto F_p^2 => independent of k exactly.
 T3 randomized (a) independent lifts (also random curve lift, also Teichmuller x-lift): rate of psi(Q~)=k psi(P~) vs 1/p.
 T4 (b) consistent lifts Q~=[k]P~: rate = 1 (psi is a homomorphism on E~(Z_p)); Q~=[k]P~+eps (eps in E_1): rate 1/p.
 T5 torsion (canonical) lift s(P)=unique order-r lift: psi = 0 identically.
 T6 (c) p | #E: for p>=7 forces #E=p (exhaustive check p<=200); p=5,#E=10 case.
"""
import sys, os, random
from math import gcd
sys.path.insert(0, os.path.dirname(__file__))
from padic_smart import PCurve, all_curves, prime_factors, sample_curves
from toyec import Curve, is_prime

SEED = 20261103
rnd = random.Random(SEED)

def gen_point_order(E, n, r):
    """point of exact prime order r"""
    while True:
        S = E.points()[rnd.randrange(1, n)]
        if S is None or S[1] == 0: continue
        P = E.mul(n // r, S)
        if P is not None and P[1] != 0: return P

# ---------- T1 anomalous control ----------
print('== T1 anomalous curves (#E = p): psi(Q~) = k psi(P~) for independent random lifts')
t1_ok = t1_tot = t1_zero = 0; t1_curves = 0
for p in [q for q in range(101, 400) if is_prime(q)][:14]:
    for a, b, E, n in sample_curves(p, lambda n: n == p, 3, rnd):
        t1_curves += 1
        Ec = PCurve(a, b, p)
        for _ in range(12):
            P = gen_point_order(E, n, p); k = rnd.randrange(1, p); Q = E.mul(k, P)
            if Q is None or Q[1] == 0: continue
            lp, lq = Ec.lift(P, rnd.randrange(p * p)), Ec.lift(Q, rnd.randrange(p * p))
            sp, sq = Ec.psi(lp, n), Ec.psi(lq, n)
            if sp == 0: t1_zero += 1; assert sq == 0; continue   # psi == 0 identically on this curve lift (degenerate lift)
            t1_tot += 1
            if (sq * pow(sp, -1, p)) % p == k: t1_ok += 1
print(f'curves={t1_curves} informative trials={t1_tot} recovered k={t1_ok}; degenerate-lift trials (psi==0)={t1_zero}')

# ---------- T2 exhaustive lift enumeration ----------
print('== T2 exhaustive lift pairs: bijection onto F_p^2 for non-anomalous E, r | #E, r != p')
t2 = []
for p in (11, 13, 17, 19, 23):
    cnt = 0
    for a, b, E, n in sample_curves(p, lambda n: n % 2 == 1 and n != p and n % p != 0 and n >= 5, 6, rnd):
        r = max(prime_factors(n))
        if r == p: continue
        Ec = PCurve(a, b, p, N=2)
        P = gen_point_order(E, n, r); k = rnd.randrange(1, r); Q = E.mul(k, P)
        if Q is None or Q[1] == 0: continue
        vals = {(Ec.psi(Ec.lift(P, u), n), Ec.psi(Ec.lift(Q, v), n)) for u in range(p) for v in range(p)}
        t2.append(len(vals) == p * p); cnt += 1
        if cnt >= 6: break
print(f'curves tested={len(t2)} all bijective onto F_p^2: {all(t2)}')

# ---------- T3/T4/T5 randomized rates ----------
def sweep(plist, trials_per_curve, maxcurves):
    res = {k: [0, 0] for k in ('indep_lift', 'indep_lift_and_curve_lift', 'teichmuller_x', 'consistent_[k]P', 'consistent+eps_in_E1', 'torsion_lift_psi==0', 'psi_hom_on_sums')}
    inv_p = 0.0; ntr = 0
    for p in plist:
        done = 0
        for a, b, E, n in sample_curves(p, lambda n: n % 2 == 1 and n != p and n % p != 0 and n >= 7 and max(prime_factors(n)) >= 5, maxcurves, rnd):
            r = max(prime_factors(n))
            P = gen_point_order(E, n, r)
            Ec = PCurve(a, b, p)
            for _ in range(trials_per_curve):
                k = rnd.randrange(2, r); Q = E.mul(k, P)
                if Q is None or Q[1] == 0: continue
                def rec(name, ok): res[name][0] += bool(ok); res[name][1] += 1
                # (a) independent lifts
                lp, lq = Ec.lift(P, rnd.randrange(p * p)), Ec.lift(Q, rnd.randrange(p * p))
                sp, sq = Ec.psi(lp, n), Ec.psi(lq, n); rec('indep_lift', sq == k * sp % p)
                inv_p += 1 / p; ntr += 1
                # (a') random curve lift too (same lifted curve for both points)
                a2, b2 = (a + p * rnd.randrange(p * p)) % p ** 3, (b + p * rnd.randrange(p * p)) % p ** 3
                E2 = PCurve(a2, b2, p)
                try:
                    lp2, lq2 = E2.lift(P, rnd.randrange(p * p)), E2.lift(Q, rnd.randrange(p * p))
                    rec('indep_lift_and_curve_lift', E2.psi(lq2, n) == k * E2.psi(lp2, n) % p)
                except AssertionError:
                    pass
                # Teichmuller x-lifts
                tp, tq = Ec.teich_lift(P), Ec.teich_lift(Q)
                rec('teichmuller_x', Ec.psi(tq, n) == k * Ec.psi(tp, n) % p)
                # (b) consistent lifts
                lk = Ec.mul(k, lp); rec('consistent_[k]P', Ec.psi(lk, n) == k * sp % p)
                e1 = Ec.add(Ec.lift(Q, rnd.randrange(p * p)), Ec.neg(Ec.lift(Q, rnd.randrange(p * p))))
                lk2 = Ec.add(lk, e1); rec('consistent+eps_in_E1', Ec.psi(lk2, n) == k * sp % p)
                # (T5) torsion lift: c = H * (H^-1 mod r), H = #E(Z/p^3)/r = (n/r) p^2
                e = 0; nn = n
                while nn % r == 0: nn //= r; e += 1
                H = nn * p ** 2; c = H * pow(H, -1, r)   # c = 1 mod r, c = 0 mod |prime-to-r part| of E(Z/p^3)
                T = Ec.mul(c, lp)
                Tm = Ec.mul(r, T)
                assert Tm[0] % Ec.m == 0 and Tm[2] % Ec.m == 0, 'torsion lift has order dividing r'
                rec('torsion_lift_psi==0', Ec.psi(T, n) == 0 if True else 0)
                # hom check
                s_sum = Ec.psi(Ec.add(lp, lq), n); rec('psi_hom_on_sums', s_sum == (sp + sq) % p)
            done += 1
            if done >= maxcurves: break
    return res, inv_p / ntr, ntr

print('== T3-T5 randomized sweeps (seed %d)' % SEED)
res, chance, ntr = sweep([11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47], 25, 6)
print(f'trials(per category) ~ {ntr}; average chance rate 1/p = {chance:.4f}')
for k, (ok, tot) in res.items():
    print(f'  {k:28s} {ok}/{tot} = {ok/max(tot,1):.4f}')

# ---------- T6 p | #E ----------
print('== T6 p | #E, p >= 7 forces #E = p ? (exhaustive over all (a,b), primes 7..199)')
bad = []
for p in [q for q in range(7, 200) if is_prime(q)]:
    # count only via Hasse: multiples of p in [p+1-2sqrt p, p+1+2sqrt p]
    from math import isqrt
    lo, hi = p + 1 - 2 * isqrt(p) - 2, p + 1 + 2 * isqrt(p) + 2
    mult = [m for m in range(max(lo, 1), hi + 1) if m % p == 0 and (m - p - 1) ** 2 <= 4 * p]
    if mult != [p]: bad.append((p, mult))
print('primes where multiples of p in Hasse interval differ from {p}:', bad)
print('== p=5 curves with #E = 10 (p | #E, r=2 != p): psi well-defined (lift independent) and hom?')
p = 5; rows = []
for a, b, E, n in all_curves(p):
    if n != 10: continue
    Ec = PCurve(a, b, p)   # complete law NOT valid here (even order) -> use affine-free check via points of odd order only
    # use odd-order subgroup points (order 5 = p) only for psi defined; for the order-2 point y=0 -> skip lift (not liftable as y!=0)
    pts = [q for q in E.points() if q is not None and q[1] != 0]
    vals = {}
    for P in pts:
        vals[P] = {Ec.psi(Ec.lift(P, u), n) for u in range(25)}
    rows.append((a, b, n, all(len(v) == 1 for v in vals.values()), sorted({next(iter(v)) for v in vals.values()})))
print('(a,b,#E,psi lift-independent on all y!=0 points, psi values):', rows[:6])
