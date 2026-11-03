import sys, json, random, time
from gen import *
kind, bits, N = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rng = random.Random(1000 + bits + (1 if kind == 'j1728' else 0))
E, P0, r, info = cm_curve(kind, bits, rng)
meths = {'none': aut_group('none', E, P0, r), 'neg': aut_group('neg', E, P0, r), 'aut': aut_group(kind, E, P0, r)}
out = open(f'out_t1_{kind}_{bits}.jsonl', 'w')
for s in range(N):
    r2 = random.Random(s)
    # random point of order r: cofactor times random point
    while True:
        X = r2.randrange(E.p); rhs = (X**3 + E.a*X + E.b) % E.p
        if pow(rhs, (E.p-1)//2, E.p) == 1:
            Pt = (X, sqrt_mod(rhs, E.p)); P = emul(info['cof'], Pt, E.a, E.p, Counter())
            if P is not None: break
    k = r2.randrange(1, r); Q = emul(k, P, E.a, E.p, Counter())
    for name, G in meths.items():
        t = time.time(); kk, ops, inf = rho(E, P, Q, r, G, random.Random(10_000 + s))
        ok = kk is not None
        if ok: assert emul(kk, P, E.a, E.p, Counter()) == Q and (r > 1 << 30 or dlog_bsgs(E, P, Q, r) == kk)
        out.write(json.dumps(dict(kind=kind, bits=bits, rbits=r.bit_length(), r=r, p=E.p, seed=s, method=name, ok=ok, ops=ops,
                                  cyc=inf['cyc'], d=inf['d'], sec=round(time.time()-t, 3))) + '\n')
out.close()
