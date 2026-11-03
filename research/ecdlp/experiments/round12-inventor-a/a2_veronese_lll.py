"""A2: Coppersmith-style lattice decomposition of a target R as +-P1 +-P2 with P1,P2 Farey-height points.
Linearisation: Semaev S3(x1,x2,x(R)) = 0 with x_i=u_i/v_i is a bilinear form in the Veronese vectors
(u^2,uv,v^2); solutions are short vectors z in a 9-dim lattice of determinant p (rank-one structure)."""
import sys, json, itertools, time
from a1_farey_ic import fb_farey, add_arr
from common import *

def S3coef(x3, a, b, p):
    c = np.zeros((3, 3), dtype=object)
    c[2][2] = 1; c[2][1] = c[1][2] = -2 * x3; c[2][0] = c[0][2] = x3 * x3
    c[1][1] = -2 * x3 * x3 - 2 * a; c[1][0] = c[0][1] = -2 * a * x3 - 4 * b; c[0][0] = a * a - 4 * b * x3
    return [[int(c[i][j]) % p for j in range(3)] for i in range(3)]

def S3eval(x1, x2, x3, a, b, p):
    c = S3coef(x3, a, b, p)
    return sum(c[i][j] * pow(x1, i, p) * pow(x2, j, p) for i in range(3) for j in range(3)) % p

def lll(B, delta=0.99):
    B = [list(map(int, r)) for r in B]; n = len(B)
    def gs():
        Bf = np.array(B, dtype=float); Bs = np.zeros_like(Bf); mu = np.zeros((n, n))
        for i in range(n):
            v = Bf[i].copy()
            for j in range(i):
                mu[i, j] = Bf[i] @ Bs[j] / (Bs[j] @ Bs[j]); v -= mu[i, j] * Bs[j]
            Bs[i] = v
        return Bs, mu
    Bs, mu = gs(); k = 1; it = 0
    while k < n and it < 20000:
        it += 1
        for j in range(k - 1, -1, -1):
            q = round(mu[k, j])
            if q:
                B[k] = [x - q * y for x, y in zip(B[k], B[j])]; Bs, mu = gs()
        if Bs[k] @ Bs[k] >= (delta - mu[k, k - 1] ** 2) * (Bs[k - 1] @ Bs[k - 1]): k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]; Bs, mu = gs(); k = max(k - 1, 1)
    return B

COMBOS = np.array(list(itertools.product((-1, 0, 1), repeat=9)), dtype=np.int64)[1:]

def lattice_decompose(x3, a, b, p, fbx):
    c = S3coef(x3, a, b, p)  # c[i][j] for z[i][j]
    cv = [c[i][j] for i in range(3) for j in range(3)]  # index 3i+j ; z22 is index 8, c=1
    basis = []
    for t in range(8):
        row = [0] * 9; row[t] = 1; row[8] = (-cv[t]) % p; basis.append(row)
    basis.append([0] * 8 + [p])
    Bred = np.array(lll(basis), dtype=np.int64)
    V = COMBOS @ Bred
    Z = V.reshape(-1, 3, 3)
    ok = (Z[:, 0, :] * Z[:, 2, :] == Z[:, 1, :] ** 2).all(1) & (Z[:, :, 0] * Z[:, :, 2] == Z[:, :, 1] ** 2).all(1)
    ok &= Z[:, 0, 0] != 0
    for z in Z[ok]:
        for j in range(3):
            if z[0][j] % p == 0: continue
            x1 = int(z[1][j]) * pow(int(z[0][j]), -1, p) % p
            break
        else: continue
        if z[0][0] % p == 0: continue
        x2 = int(z[0][1]) * pow(int(z[0][0]), -1, p) % p
        if x1 != x2 and x1 in fbx and x2 in fbx and S3eval(x1, x2, x3, a, b, p) == 0:
            return True, len(Z[ok])
    return False, int(ok.sum())

def experiment(inst, cfac, ntargets, seed=1):
    p, a, b = inst['p'], inst['a'], inst['b']
    s = int(cfac * p ** (1 / 3))
    X, Y, _, H = fb_farey(inst, s); fbx = set(int(x) for x in X)
    I, J = np.triu_indices(len(X), 1)
    sums = set()
    for sg in (1, -1):
        x3, y3, ok = add_arr(X[I], Y[I], X[J], (sg * Y[J]) % p, p)
        sums |= set(int(v) for v in x3[ok])
    rng = random.Random(seed)
    exist = []; tested = 0
    while tested < ntargets:
        x = rng.randrange(p); v = (x ** 3 + a * x + b) % p
        if pow(v, (p - 1) // 2, p) != 1: continue
        tested += 1
        if x in sums: exist.append(x)
    succ = 0; t0 = time.time()
    # false-positive control: non-existing targets
    for x in exist:
        ok, _ = lattice_decompose(x, a, b, p, fbx); succ += ok
    fp = 0; nctrl = 0
    while nctrl < 20:
        x = rng.randrange(p); v = (x ** 3 + a * x + b) % p
        if pow(v, (p - 1) // 2, p) != 1 or x in sums: continue
        nctrl += 1; fp += lattice_decompose(x, a, b, p, fbx)[0]
    return dict(bits=inst['bits'], p=p, cfac=cfac, s=len(X), H=H, targets=ntargets, exist=len(exist),
                lll_success=succ, false_pos=fp, ctrl=nctrl, secs=round(time.time() - t0, 1),
                log2_true_norm=round(4 * math.log2(max(H, 2)), 1), log2_det_root9=round(math.log2(p) / 9, 1))

if __name__ == '__main__':
    insts = load_instances()
    # sanity: Semaev S3 coefficient check
    i0 = [i for i in insts if i['bits'] == 12][0]; E = Curve(i0['a'], i0['b'], i0['p']); P = i0['P']; Q = i0['Q']
    R = E.add(P, Q); assert S3eval(P[0], Q[0], R[0], i0['a'], i0['b'], i0['p']) == 0
    out = open(os.path.join(HERE, 'out_a2.jsonl'), 'w')
    plan = [(16, 1.3, 1500), (20, 1.3, 2500), (24, 1.3, 4000), (20, 0.5, 2500), (20, 2.0, 2500), (12, 1.3, 400)]
    for b, cf, nt in plan:
        inst = [i for i in insts if i['bits'] == b and i['seed'] == 1][0]
        res = experiment(inst, cf, nt); out.write(json.dumps(res) + '\n'); out.flush(); print(res, flush=True)
