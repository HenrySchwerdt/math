"""Post-hoc amendment C1b (registered in PROTOCOL_ADDENDUM.md AFTER the frozen C1 result showed fruitless-cycle
capture growing with walk length): negation-class rho with detection of ALL repeats within a window of W steps."""
from lib12 import R_PARTS, dp_mask_for
from algos import setup_steps

def rho_neg_w(ops, P, Q, n, rng, L, maxfac=20, W=16):
    p, half = ops.p, ops.p >> 1
    S = setup_steps(ops, P, Q, n, rng)
    mask, table, wid = dp_mask_for(L), {}, 0
    cap = maxfac * (mask+1)
    stats = {'cycle2': 0, 'cycle4': 0, 'capped': 0}   # cycle2 := repeats at distance 2, cycle4 := repeats at any other distance
    def canon(R, a, b):
        if R[1] > half: return (R[0], p - R[1]), (-a) % n, (-b) % n
        return R, a, b
    while True:
        wid += 1
        a0, b0 = rng.randrange(n), rng.randrange(n)
        R = ops.add(ops.mul(a0, P), ops.mul(b0, Q))
        if R is None: continue
        R, a, b = canon(R, a0, b0)
        hist = []
        for it in range(cap):
            x = R[0]
            if (x & mask) == 0:
                prev = table.get(x)
                if prev is None: table[x] = (a, b, wid)
                elif prev[2] != wid and prev[1] != b:
                    return (prev[0]-a) * pow(b-prev[1], -1, n) % n, ops.count, (len(table), stats)
                break
            pt, da, db = S[x % R_PARTS]
            if pt[0] == x: break
            hist.append((R, a, b))
            if len(hist) > W: hist.pop(0)
            R = ops.add(R, pt); a = (a+da) % n; b = (b+db) % n
            R, a, b = canon(R, a, b)
            d = 0
            for i in range(len(hist)-1, -1, -1):
                if hist[i][0][0] == R[0]: d = len(hist)-i; break
            if d:
                seg = [(R, a, b)] + hist[len(hist)-d+1:]
                stats['cycle2' if d == 2 else 'cycle4'] += 1
                (M, ma, mb) = min(seg, key=lambda t: t[0][0])
                R = ops.add(M, M); a, b = (2*ma) % n, (2*mb) % n
                if R is None: break
                R, a, b = canon(R, a, b); hist = []
        else:
            stats['capped'] += 1
