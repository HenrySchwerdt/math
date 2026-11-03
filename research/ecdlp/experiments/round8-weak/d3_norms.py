#!/usr/bin/env python3
"""D3 check: minimal nonscalar norms in Z[pi] and in the maximal order O_K, all ordinary traces, primes 5<p<PMAX.
Pure stdlib, deterministic enumeration; SEED only picks the (p,t) sample for an independent brute-force cross-check."""
import random, sys, math
SEED = 20261103
PMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
random.seed(SEED)

def primes(n):
    s = bytearray([1]) * (n + 1); s[:2] = b"\0\0"
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i*i::i] = bytearray(len(s[i*i::i]))
    return [i for i in range(n + 1) if s[i]]

def isqrt_exact(n):
    r = math.isqrt(n); return r if r * r == n else None

def fund_disc(D):
    """D<0, D = f^2 * dK, dK fundamental discriminant. returns (dK, f)."""
    m = -D; f = 1; d = 2; sf = m
    # squarefree part via trial division
    core = 1; rest = m; f = 1
    q = 2
    while q * q <= rest:
        e = 0
        while rest % q == 0: rest //= q; e += 1
        core *= q ** (e % 2); f *= q ** (e // 2)
        q += 1
    core *= rest          # rest is 1 or a prime with exponent 1
    # core squarefree, D = -f^2 * core. fundamental iff -core = 1 mod 4, else multiply by 4
    if (-core) % 4 == 1: return -core, f
    return -4 * core, f // 2 if f % 2 == 0 else None

def min_norm_Zpi(t, p):           # closed form (b=1, optimal a)
    return (4*p - t*t + (t & 1)) // 4

def min_norm_Zpi_brute(t, p, B=6, A=None):
    A = A or (abs(t) + 3 * B + 5)
    return min(a*a + t*a*b + p*b*b for b in range(1, B+1) for a in range(-A*B, A*B+1))

def min_norm_maxorder(dK):       # a + b*w, w=(dK+sqrt dK)/2 ; N = a^2 + ab dK + b^2 (dK^2-dK)/4
    return (-dK + (dK & 1)) // 4  # b=1, a=-(dK//2) region; verified by brute force below

def min_norm_maxorder_brute(dK, B=6):
    c = (dK*dK - dK)//4
    A = abs(dK) * B + 5
    return min(a*a + a*b*dK + b*b*c for b in range(1, B+1) for a in range(-A, A+1))

rows = []; viol = 0; tot = 0
stats = {}
for p in primes(PMAX):
    if p < 5: continue
    lim = math.isqrt(4*p)
    for t in range(-lim, lim + 1):
        if t % p == 0: continue            # skip supersingular t=0 (p>3): End is a quaternion order
        D = t*t - 4*p
        if D >= 0: continue
        n1 = min_norm_Zpi(t, p)
        assert 4 * n1 >= -D                 # N >= |D|/4
        dK, f = fund_disc(D)
        assert D == f * f * dK, (p, t, D, dK, f)
        n2 = min_norm_maxorder(dK)
        assert 4 * n2 >= -dK
        tot += 1
        # lemma: nonscalar norm in Z[pi] >= |D|/4 ; in particular |D|>=c p => norm >= c p/4
        if -D >= p and 4 * n1 < p: viol += 1
        s = stats.setdefault(p, [0, 0, 0, 0, 0])
        s[0] += 1
        if dK in (-3, -4): s[1] += 1        # extra automorphisms possible in max order
        if -D < p: s[2] += 1                # |D| < p
        if -D >= p and dK in (-3, -4): s[3] += 1   # large |D| yet End can be big-disc-free (u large)
        if n1 == 1: s[4] += 1               # nonscalar unit in Z[pi] itself

# cross-check closed forms by brute force on a seeded sample
pl = [p for p in primes(min(PMAX, 400)) if p >= 5]
checked = 0
for _ in range(300):
    p = random.choice(pl); lim = math.isqrt(4*p); t = random.randint(-lim, lim)
    if t % p == 0 or t*t - 4*p >= 0: continue
    assert min_norm_Zpi_brute(t, p) == min_norm_Zpi(t, p), (p, t)
    dK, f = fund_disc(t*t - 4*p)
    assert min_norm_maxorder_brute(dK) == min_norm_maxorder(dK), dK
    checked += 1

print("SEED", SEED, "PMAX", PMAX)
print("ordinary (p,t) pairs enumerated:", tot)
print("violations of [|D|>=p => min nonscalar norm in Z[pi] >= p/4]:", viol)
print("closed-form vs brute-force cross-checks passed:", checked)
tp = sum(s[0] for s in stats.values()); t12 = sum(s[1] for s in stats.values())
print("pairs with fundamental disc dK in {-3,-4}:", t12, "(%.4f%% of pairs)" % (100*t12/tp))
print("  of which |D| >= p (i.e. conductor large; End(E) may be the big order j=0/1728 curve):", sum(s[3] for s in stats.values()))
print("pairs where Z[pi] itself has a nonscalar unit (D in {-3,-4}):", sum(s[4] for s in stats.values()))
# worst ratio min_norm_Zpi / p over |D|>=c p
for c in (0.1, 0.5, 1.0, 2.0):
    best = min((min_norm_Zpi(t, p) / p) for p in stats for t in range(-math.isqrt(4*p), math.isqrt(4*p)+1)
               if t % p and t*t-4*p < 0 and 4*p - t*t >= c*p)
    print("c=%.1f: min over pairs with |D|>=c*p of normZpi/p = %.4f  (lemma bound c/4 = %.4f)" % (c, best, c/4))
# j=0 / 1728 fraction of j-invariants, per p, sample
for p in (101, 1009, 2999):
    if p <= PMAX: print("p=%d: <=2 of %d j-invariants have Aut>2: fraction <= %.5f" % (p, p, 2/p))
# distribution of minimal norm in max order across small primes: fraction of traces with dK=-3,-4 per p
for p in (101, 1009, 2999):
    if p in stats: print("p=%d: ordinary traces %d, with dK in {-3,-4}: %d" % (p, stats[p][0], stats[p][1]))
