"""Round-20 inventor J: end-to-end pipelines on planted-leak controls + same-implementation rho / kangaroo controls. Counted group ops
(affine add/double = 1 op). Oracle simulators know the scalar of each queried point (planted curve family); decoders never read k."""
import sys, os, json, math, random
import numpy as np
sys.path.insert(0, '/home/user/math/research/ecdlp/experiments/round12-inventor-c')
sys.path.insert(0, '/home/user/math/research/ecdlp/experiments/lib')
from lib12 import find_prime_order_curve, Ops
from toyec import Curve

def mask64(x): return x & 0xFFFFFFFFFFFFFFFF
def smix(x, y, seed):
    z = mask64(x * 0x9E3779B97F4A7C15 + y * 0xBF58476D1CE4E5B9 + seed * 0x94D049BB133111EB + 0x1234567)
    z = mask64((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9); z = mask64((z ^ (z >> 27)) * 0x94D049BB133111EB); return z ^ (z >> 31)

class Inst:
    def __init__(self, bits, seed, curve_seed0=500):
        E, P, r = find_prime_order_curve(bits, curve_seed0 + seed)
        self.E, self.P, self.r, self.p = E, P, r, E.p
        self.ops = Ops(E.p, E.a); self.rng = random.Random(f'inst-{bits}-{seed}')
        self.k = self.rng.randrange(1, r); self.Q = self.ops.mul(self.k, P); self.ops.count = 0
        self.seed = seed; self.oracle_calls = 0
    def omsb(self, pt, scalar, eps):
        """planted MSB oracle of advantage eps: [scalar > r/2] flipped w.p. 1/2-eps, flip = hash(point)."""
        self.oracle_calls += 1
        b = 1 if scalar % self.r > self.r // 2 else 0
        if pt is None: return b
        flip = (smix(pt[0], pt[1], self.seed) % 1000000) < (0.5 - eps) * 1000000
        return b ^ int(flip)

# ---------------- rho control (same Ops) ----------------
def rho(inst, rng):
    r, ops, P, Q = inst.r, inst.ops, inst.P, inst.Q
    nj = 20; steps = []
    for _ in range(nj):
        u, v = rng.randrange(r), rng.randrange(r)
        steps.append((u, v, ops.add(ops.mul(u, P), ops.mul(v, Q))))
    dpbits = max(1, int(math.log2(max(2, math.isqrt(r))) / 2) - 1); mask = (1 << dpbits) - 1
    c0 = ops.count; table = {}
    while True:
        a, b = rng.randrange(r), rng.randrange(r); R = ops.add(ops.mul(a, P), ops.mul(b, Q))
        for _ in range(40 * (mask + 1)):
            if R is None: break
            if (R[0] & mask) == 0:
                if R in table and table[R] != (a, b):
                    a2, b2 = table[R]; db = (b - b2) % r
                    if db:
                        k = (a2 - a) * pow(db, -1, r) % r
                        if ops.mul(k, P) == Q: return k, ops.count - c0
                    break
                table[R] = (a, b); 
            u, v, S = steps[R[0] % nj]; R = ops.add(R, S); a = (a + u) % r; b = (b + v) % r

# ---------------- kangaroo: k in [lo, lo+w] ----------------
def kangaroo(ops, P, Q, lo, w, rng, r, cap_factor=40):
    """returns (k or None, ops). Distinguished-point tame/wild with one tame + one wild herd member (restarts counted)."""
    c0 = ops.count
    Q1 = ops.add(Q, ops.mul((-lo) % r, P)) if lo else Q      # k' = k-lo in [0,w]
    for attempt in range(8):
        sw = max(1, math.isqrt(w)); L = max(2, int(math.log2(max(2, sw))) + 1)
        jumps = [rng.randrange(1, max(2, sw)) for _ in range(L)]
        # mean jump ~ sqrt(w)/2
        sc = max(1, int(sw / 2 / max(1, sum(jumps) / L)))
        jumps = [max(1, j * sc) for j in jumps]
        pts = [ops.mul(j, P) for j in jumps]
        dpmask = (1 << max(0, int(math.log2(max(2, sw))) - 2)) - 1
        T = ops.mul(w, P); dT = w                  # tame at scalar w
        W = Q1; dW = 0
        tab = {}; cap = cap_factor * sw + 100
        for step in range(cap):
            for who in (0, 1):
                if who == 0:
                    if T is None: continue
                    j = T[0] % L; T = ops.add(T, pts[j]); dT += jumps[j]; Rr, d = T, dT
                else:
                    if W is None: continue
                    j = W[0] % L; W = ops.add(W, pts[j]); dW += jumps[j]; Rr, d = W, dW
                if Rr is not None and (Rr[0] & dpmask) == 0:
                    key = Rr
                    if key in tab and tab[key][0] != who:
                        dTame, dWild = (d, tab[key][1]) if who == 0 else (tab[key][1], d)
                        # tame scalar = dT ; wild scalar = k' + dW  => k' = dT - dW
                        kk = (dTame - dWild + lo) % r
                        if ops.mul(kk, P) == Q: return kk, ops.count - c0
                    tab[key] = (who, d)
            if dW > dT + w + 4 * sw * 20: break
    return None, ops.count - c0

# ---------------- P0 naive additive-shift binary search ----------------
def p0_binary(inst, eps):
    r, k = inst.r, inst.k; lo, hi = 0, r; q = 0
    while hi - lo > 1:
        mid = (lo + hi) // 2; a = (r // 2 - mid) % r; q += 1
        pt = inst.ops.add(inst.Q, inst.ops.mul(a, inst.P))     # costs counted
        b = inst.omsb(pt, (k + a) % r, eps)
        if b == 0: hi = mid   # k+a below r/2 => k < mid
        else: lo = mid
    return lo, q

# ---------------- P1 stride-ML iterative refinement ----------------
def ml_round(inst, R, d_true_scalar_of_R, W, N, eps, kappa, rng):
    """R = dP with |d|<=W. queries c_j = j*m, point c_j R. returns (dhat, newW)."""
    r, ops = inst.r, inst.ops
    m = max(1, r // (2 * W)) if W > 0 else 1
    mR = ops.mul(m, R); pt = None; bits = np.zeros(N, dtype=np.int8)
    for j in range(1, N + 1):
        pt = mR if j == 1 else ops.add(pt, mR)
        bits[j - 1] = inst.omsb(pt, (j * m * d_true_scalar_of_R) % r, eps)
    G = 4 * N
    cand = np.round(np.linspace(-W, W, G)).astype(np.int64)
    best, bd = -1e18, 0
    sgn = np.where(bits == 1, 1, -1).astype(np.int32)
    js = (np.arange(1, N + 1, dtype=np.int64) * m)
    for s in range(0, G, 2000):
        cd = cand[s:s + 2000]
        pred = (((js[None, :] * cd[:, None]) % r) > r // 2)
        sc = (np.where(pred, 1, -1).astype(np.int32) * sgn[None, :]).sum(1)
        i = int(np.argmax(sc))
        if sc[i] > best: best, bd = sc[i], int(cd[i])
    newW = max(1, int(math.ceil(kappa * 2 * W / N)))
    return bd, newW

def p1_run(inst, eps, nu, kappa, rng, mq=7, final=3):
    r, ops, P, Q, k = inst.r, inst.ops, inst.P, inst.Q, inst.k
    c0 = ops.count; g = (r // 2) % r; W = r // 2 + 1; widths = [W]; nq_total = 0
    for it in range(40):
        R = ops.add(Q, ops.mul((-g) % r, P)) if g else Q
        d_true = (k - g) % r
        if d_true > r // 2: d_true -= r
        if abs(d_true) > W: return dict(ok=False, ops=ops.count - c0, widths=widths, fail='window_lost', q=nq_total)
        if W <= final: break
        N = 200
        for _ in range(5): N = int(math.ceil(nu * math.log(4 * N) / eps ** 2))
        dhat, newW = ml_round(inst, R, d_true, W, N, eps, kappa, rng)
        nq_total += N; g = (g + dhat) % r; W = newW; widths.append(W)
    # finish: enumerate residual window (<= 2*final+1 candidates), verify
    for d in range(-W, W + 1):
        if ops.mul((g + d) % r, P) == Q: kk = (g + d) % r; break
    else: return dict(ok=False, ops=ops.count - c0, widths=widths, fail='enum', q=nq_total)
    c = ops.count - c0
    return dict(ok=(kk == k), ops=c, ops_feat=c + mq * nq_total, widths=widths, q=nq_total)

if __name__ == '__main__':
    pass

# ---------------- P2/P3: regression-oracle planted control ----------------
def gauss_est(inst, sd, tag):
    rg = random.Random(f'reg-{inst.seed}-{tag}')
    return inst.k + rg.gauss(0, sd)

def p2_interval_kangaroo(inst, rho_rel, rng, z=2.0, rho_fit=None):
    """one regression query: khat = k + N(0,(rho r)^2); interval khat +- z*rho*r; kangaroo; fallback rho."""
    r, ops = inst.r, inst.ops; c0 = ops.count
    khat = gauss_est(inst, rho_rel * r, 'p2'); half = z * rho_rel * r
    lo = max(0, int(khat - half)); hi = min(r - 1, int(khat + half)); w = hi - lo
    k, c = kangaroo(ops, inst.P, inst.Q, lo, max(w, 4), rng, r)
    fb = 0
    if k is None:
        kk, fb = rho(inst, rng); k = kk
    return dict(ok=(k == inst.k), ops=ops.count - c0, w=w, fallback=fb > 0, ops_kang=c)

def p3_iterative(inst, rho_rel, scale_aware, rng, z=2.0, mq=7, stop=3):
    """estimate, subtract gP, re-estimate on residual. scale_aware: noise sd = rho*W (oracle told the scale); else fixed rho*r."""
    r, ops, k = inst.r, inst.ops, inst.k; c0 = ops.count
    g = r // 2; W = r // 2 + 1; widths = [W]; calls = 0
    for it in range(60):
        d = (k - g) % r
        if d > r // 2: d -= r
        if abs(d) > W: return dict(ok=False, widths=widths, fail='lost', ops=ops.count - c0)
        if W <= stop: break
        sd = rho_rel * (W if scale_aware else r); calls += 1
        rg = random.Random(f'p3-{inst.seed}-{it}-{scale_aware}')
        dhat = d + rg.gauss(0, sd); dhat = max(-W, min(W, dhat))
        newW = int(math.ceil(z * sd)) + 1
        ops.count += 0
        gnew = (g + int(round(dhat))) % r
        ops.mul((-gnew) % r, inst.P)     # cost of forming residual R=Q-gP (counted)
        if newW >= W:     # no progress: stop estimating
            widths.append(W); break
        g, W = gnew, newW; widths.append(W)
    ops_est = ops.count - c0 + mq * calls
    # finish
    if W <= stop:
        for dd in range(-W, W + 1):
            if ops.mul((g + dd) % r, inst.P) == inst.Q: return dict(ok=((g + dd) % r == k), widths=widths, ops=ops.count - c0, ops_feat=ops.count - c0 + mq * calls, calls=calls)
        return dict(ok=False, widths=widths, fail='enum', ops=ops.count - c0)
    lo = (g - W) % r
    kk, c = kangaroo(ops, inst.P, inst.Q, lo, 2 * W, rng, r)
    return dict(ok=(kk == k), widths=widths, ops=ops.count - c0, ops_feat=ops.count - c0 + mq * calls, calls=calls, kang=c)

# ---------------- P4: closeness-detector scan (planted detector) ----------------
def close_oracle(inst, pt, dscal, w, delta):
    inst.oracle_calls += 1
    d = dscal % inst.r
    if d > inst.r // 2: d -= inst.r
    b = 1 if abs(d) <= w else 0
    if pt is None: return b
    return b ^ int((smix(pt[0], pt[1], inst.seed + 77) % 1000000) < (0.5 - delta) * 1000000)

def p4_close_scan(inst, delta, nu, rng, nc=32, mq=7, stop=300):
    r, ops, P, Q, k = inst.r, inst.ops, inst.P, inst.Q, inst.k; c0 = ops.count
    g = r // 2; W = r // 2 + 1; widths = [W]; nq = 0
    for it in range(40):
        d = (k - g) % r
        if d > r // 2: d -= r
        if abs(d) > W: return dict(ok=False, widths=widths, fail='lost', ops=ops.count - c0)
        if W <= stop: break
        wc = max(1.0, 2 * W / nc); T = int(math.ceil(nu * math.log(8 * nc) / max(delta, 1e-3) ** 2 / 4)) ; T = max(T, 1)
        R0 = ops.add(Q, ops.mul((-g) % r, P)) if g else Q
        us = [int(round((i + 0.5) / T * wc - wc / 2)) for i in range(T)]
        uP = [ops.mul(u % r, P) for u in us]
        step = ops.mul(int(round(wc)) % r, P)
        # residual points R(c,u) = R0 - (c - u) P with c = -W + (t+.5)wc ; scalar of resid = d - c + u
        c_first = int(round(-W + 0.5 * wc)); cur = ops.add(R0, ops.mul((-c_first) % r, P))
        obs = []
        for t in range(nc):
            c = c_first + t * int(round(wc))
            for i in range(T):
                pt = ops.add(cur, uP[i]); nq += 1
                obs.append((c, us[i], close_oracle(inst, pt, d - c + us[i], wc, delta)))
            cur = ops.add(cur, ops.mul((-int(round(wc))) % r, P)) if False else ops.add(cur, neg_pt(ops, step))
        cs = np.array([o[0] for o in obs]); ui = np.array([o[1] for o in obs]); bb = np.array([o[2] for o in obs])
        sgn = np.where(bb == 1, 1, -1)
        grid = np.linspace(-W, W, 8 * nc + 1)
        best = None
        for dc in grid:
            pred = (np.abs(dc - cs + ui) <= wc)
            sc = int((np.where(pred, 1, -1) * sgn).sum())
            if best is None or sc > best[0]: best = (sc, dc)
        g = (g + int(round(best[1]))) % r; W = int(math.ceil(wc)) ; widths.append(W)
    for dd in range(-W, W + 1):
        if ops.mul((g + dd) % r, P) == Q: return dict(ok=((g + dd) % r == k), widths=widths, ops=ops.count - c0, ops_feat=ops.count - c0 + mq * nq, q=nq)
    return dict(ok=False, widths=widths, ops=ops.count - c0, fail='enum', q=nq)

def neg_pt(ops, pt): return None if pt is None else (pt[0], (-pt[1]) % ops.p)
