"""E1b: kernel-coset base. Curve over F_p with a rational l-torsion point K (l=5, N=#E divisible by l, N composite so this is NOT the prime-order setting).
Base V = {x(P_i + j K)}, i<n, j<l, P_i random. Predicted raw closure 8*C(s,4)/N (no excess); distinct coset-quadruples should be N4/l^3."""
import sys, json, random, math
from f_lib import *
from toyec import Curve
bits, ell, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
rng = random.Random(31 * bits + 7 * ell + seed)
def count(a, b, p):
    x = np.arange(p, dtype=np.int64); v = (x * x % p * x + a * x + b) % p
    leg = np.zeros(p, dtype=np.int64); sq = np.zeros(p, dtype=bool); sq[(x * x) % p] = True
    return 1 + int((v == 0).sum()) + 2 * int(((sq[v]) & (v != 0)).sum())
while True:
    p = rng.randrange(2 ** (bits - 1), 2 ** bits)
    if not is_prime(p): continue
    a, b = rng.randrange(p), rng.randrange(p)
    if (4 * a ** 3 + 27 * b * b) % p == 0: continue
    N = count(a, b, p)
    if N % ell: continue
    E = Curve(a, b, p)
    while True:
        x = rng.randrange(p); y = sqrt_mod(x ** 3 + a * x + b, p)
        if y: break
    K = E.mul(N // ell, (x, y))
    if K is not None: break
assert E.mul(ell, K) is None
n = int(2.5 * p ** (1 / 3) / ell) + 1
pts = []; coset = []
while len(pts) < n:
    x = rng.randrange(p); y = sqrt_mod(x ** 3 + a * x + b, p)
    if y: pts.append((x, y))
V = {}; lab = {}
for i, P in enumerate(pts):
    Rr = P
    for j in range(ell):
        if Rr is not None and Rr[0] not in V: V[Rr[0]] = Rr[1]; lab[Rr[0]] = i
        Rr = E.add(Rr, K)
xs, ys = arrays(V); s = len(xs)
# closed quadruples with identity (need the quadruple sets): reuse pair table
z, I, J, S, adds = pair_table(p, a, xs, ys); keep = I != J; z, I, J = z[keep], I[keep], J[keep]
o = np.argsort(z, kind='stable'); z, I, J = z[o], I[o], J[o]
quads = set(); coll = 0; i0 = 0; nz = len(z)
while i0 < nz:
    i1 = i0 + 1
    while i1 < nz and z[i1] == z[i0]: i1 += 1
    for u in range(i0, i1):
        for v in range(u + 1, i1):
            q = {int(I[u]), int(J[u]), int(I[v]), int(J[v])}
            if len(q) == 4: coll += 1; quads.add(frozenset(q))
    i0 = i1
labs = [lab[int(x)] for x in xs]
cq = {frozenset(labs[i] for i in q) for q in quads}
pred = 8 * math.comb(s, 4) / N
print(json.dumps(dict(exp='kernel', bits=bits, ell=ell, seed=seed, p=p, N=N, s=s, N4=coll / 3, pred=pred, ratio=(coll / 3) / pred,
      distinct_quads=len(quads), distinct_coset_quads=len(cq), coset_quads_with_4_distinct_cosets=sum(1 for c in cq if len(c) == 4))), flush=True)
