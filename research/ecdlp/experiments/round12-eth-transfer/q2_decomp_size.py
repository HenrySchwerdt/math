"""E4: CNF size of the m=2 Semaev decomposition test  S_3(x1,x2,xR)=0 (mod p), x1,x2 in a factor base V indexed by b bits each
(small-x base V={0..2^b-1}), xR a constant.  Counts Boolean variables N_dec versus log2 p (no solving).
Purpose: calibrate N_dec for the ETH-technique route (a). Usage: python3 e4... (seed 5)"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(EXP, 'lib')); sys.path.insert(0, os.path.join(EXP, 'round10-frontier-b'))
import sat_ecdlp as S
from toyec import is_prime

def mc(C, A, c, p, m):          # (A * constant c) mod p via existential quotient
    c %= p
    if c == 0: return C.const(0, m)
    q = C.vec(c.bit_length()); r = C.vec(m); C.lt_const(r, p)
    lhs = C.mulc(A, c); rhs = C.add(C.mulc(q, p), r, max(len(lhs), len(q) + p.bit_length() + 1) + 1)
    C.eq(lhs, rhs); return r

def encode_S3(p, a, b, xR, bits):
    m = p.bit_length(); C = S.CNF()
    i1 = C.vec(bits); i2 = C.vec(bits)
    x1 = i1 + [-C.T] * (m - bits); x2 = i2 + [-C.T] * (m - bits)
    mm = lambda A, B: S.modmul(C, A, B, p, m); ad = lambda A, B: S.modadd(C, A, B, p, m); sb = lambda A, B: S.modsub(C, A, B, p, m)
    s = ad(x1, x2); d = sb(x1, x2); pr = mm(x1, x2)
    t1 = mc(C, mm(d, d), xR * xR, p, m)
    inner = ad(mm(s, ad(pr, C.const(a % p, m))), C.const((2 * b) % p, m))
    t2 = mc(C, inner, (-2 * xR) % p, p, m)
    u = sb(pr, C.const(a % p, m)); t3 = sb(mm(u, u), mc(C, s, 4 * b, p, m))
    tot = ad(ad(t1, t2), t3)
    C.eq(tot, C.const(0, m))
    return C

rng = random.Random(5); rows = []
for m in (8, 12, 16, 20, 24, 32, 40, 48, 64):
    while True:
        p = rng.randrange(1 << (m - 1), 1 << m)
        if is_prime(p) if m <= 40 else pow(2, p - 1, p) == 1: break
    C = encode_S3(p, rng.randrange(p), rng.randrange(p), rng.randrange(p), bits=m // 2)
    rows.append(dict(log2p=m, N_dec=C.n, clauses=len(C.cl)))
    print(json.dumps(rows[-1]))
xs = [math.log2(r['log2p']) for r in rows]; ys = [math.log2(r['N_dec']) for r in rows]
n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
print('fit N_dec ~ (log2 p)^%.3f ; N_dec/(log2 p)^2 at 64 bits = %.2f' % (a, rows[-1]['N_dec'] / 64 ** 2))
json.dump(rows, open(os.path.join(HERE, 'out_e4.json'), 'w'), indent=1)
