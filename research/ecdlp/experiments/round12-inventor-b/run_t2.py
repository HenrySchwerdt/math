import sys, json, random, time
from iso import *
from gen import sqrt_mod
a = int(sys.argv[1]); N = int(sys.argv[2])
rng = random.Random(2000 + a)
def find(a):
    while True:
        s = rng.randrange(2**(a-1), 2**a) | 1
        if (s-1) % 4 != 2: continue
        p = s*s + 3*4**(a-1)
        if not is_prime(p): continue
        n = p + 1 - 2*s
        if n % 4 == 0 and is_prime(n//4): return p, s, n
p, s, n = find(a); r = n // 4
b = 1
while True:
    X = rng.randrange(1, p)
    while pow((X**3 + b) % p, (p-1)//2, p) != 1: X = rng.randrange(1, p)
    Y = sqrt_mod((X**3 + b) % p, p)
    if emul(n, (X, Y), 0, p, Counter()) is None and len(roots_cubic(0, b, p, rng)) == 3: break
    b += 1
out = open(f'out_t2_{a}.jsonl', 'w')
for sd in range(N):
    r2 = random.Random(sd)
    C = Counter(); A, B = 0, b; pj = None
    for i in range(a):   # generator-side descent to the floor
        opts = step_options((A, B), pj, p, r2, C); pj = jinv(A, B, p); A, B, _ = r2.choice(opts)
    assert not step_options((A, B), pj, p, r2, Counter())
    E = Curve(A, B, p)
    while True:
        X = r2.randrange(p); rhs = (X**3 + A*X + B) % p
        if pow(rhs, (p-1)//2, p) == 1:
            pt = (X, sqrt_mod(rhs, p)); P = emul(4, pt, A, p, Counter())
            if P is not None and emul(r, P, A, p, Counter()) is None: break
    k = r2.randrange(1, r); Q = emul(k, P, A, p, Counter())
    row = dict(a=a, rbits=r.bit_length(), r=r, p=p, seed=sd)
    for name in ('none', 'neg'):
        kk, ops, inf = rho(E, P, Q, r, aut_group(name, E, P, r), random.Random(10_000 + sd))
        row[name] = dict(ok=kk is not None, ops=ops)
        if kk is not None: assert kk == k
    # B2
    t = time.time(); C2 = Counter(); ar = random.Random(30_000 + sd)
    res = ascend(A, B, p, ar, C2, [P, Q], stop=lambda A, B: A == 0)
    assert res is not None
    A2, B2, (P2, Q2), steps = res
    E2 = Curve(A2, B2, p); assert E2.on_curve(P2) and E2.on_curve(Q2)
    kk, ops, inf = rho(E2, P2, Q2, r, aut_group('j0', E2, P2, r), random.Random(10_000 + sd))
    ok = kk is not None
    if ok:
        assert emul(kk, P, A, p, Counter()) == Q and (r > 1 << 30 or dlog_bsgs(E, P, Q, r) == kk)
    row['b2'] = dict(ok=ok, rho_ops=ops, steps=steps, iso=C2.iso, cyc=inf['cyc'], sec=round(time.time()-t, 2))
    out.write(json.dumps(row) + '\n'); out.flush()
out.close()
