"""E3: greedy/annealed local search for a size-s set V of E(F_p) (cyclic of prime order N) maximising closure T3 = #{(u,v) ordered, u!=v : u+v in V}.
The search is run IN LOG SPACE (V subset of Z_N, requires the full discrete-log table = O(N) preprocessing, i.e. it is NOT an efficient method; it only
answers: what do maximal-closure sets look like, and do they have a short coordinate description?)
usage: g3_search.py BITS SEED ITERS"""
import sys, json, math, random
import numpy as np
from g_lib import *

def run(bits, seed, iters):
    C = gen_curve(bits, seed); p, a, b, N = C['p'], C['a'], C['b'], C['N']
    X, Y, _ = all_points(p, a, b)
    G = (int(X[0]), int(Y[0]))
    # table of x,y of i*G, i = 1..N-1
    px = np.zeros(N, dtype=np.int64); py = np.zeros(N, dtype=np.int64)
    cx, cy = G
    for i in range(1, N):
        px[i], py[i] = cx, cy
        if i == N - 1: break
        if cx == G[0]:
            l = (3 * cx * cx + a) * pow(2 * cy, -1, p) % p if i == 1 else None
        if i == 1: l = (3 * cx * cx + a) * pow(2 * cy, -1, p) % p; x = (l * l - 2 * cx) % p; y = (l * (cx - x) - cy) % p
        else:
            l = (cy - G[1]) * pow(cx - G[0], -1, p) % p; x = (l * l - cx - G[0]) % p; y = (l * (cx - x) - cy) % p
        cx, cy = x, y
    rng = random.Random(31 * bits + seed); s = int(round(2 * math.sqrt(N)))
    V = rng.sample(range(1, N), s); inV = np.zeros(N, bool); inV[V] = True; V = np.array(V)
    r2 = np.zeros(N, dtype=np.int64)
    def addpt(v, Vc):
        r2[(v + Vc) % N] += 2
    # initial r2
    for i in range(s):
        for j in range(s):
            if i != j: r2[(V[i] + V[j]) % N] += 1
    def T(): return int(r2[V].sum())
    T0 = T(); cur = T0; pred = predicted_closure(s, N); hist = [(0, cur)]
    for it in range(1, iters + 1):
        k = rng.randrange(s); u = int(V[k]); Vo = np.delete(V, k)
        # proposal: v = a+b or a-b of random elements (structure-seeking) half the time, else uniform
        if rng.random() < 0.5:
            x1, x2 = int(V[rng.randrange(s)]), int(V[rng.randrange(s)]); v = (x1 + x2) % N if rng.random() < 0.5 else (x1 - x2) % N
        else: v = rng.randrange(1, N)
        if v == 0 or inV[v]: continue
        r2[(u + Vo) % N] -= 2; r2[(v + Vo) % N] += 2
        V2 = V.copy(); V2[k] = v
        new = int(r2[V2].sum())
        if new >= cur:
            V = V2; inV[u] = False; inV[v] = True; cur = new
        else:
            r2[(u + Vo) % N] += 2; r2[(v + Vo) % N] -= 2
        if it % max(1, iters // 10) == 0: hist.append((it, cur))
    # description tests
    diffs = {}
    Vs = np.sort(V)
    cnt = np.zeros(N, dtype=np.int64)
    for v in Vs: cnt[(Vs - v) % N] += 1
    cnt[0] = 0; top = np.argsort(-cnt)[:5]
    best_arc = 1.0
    for d in top:
        if d == 0: continue
        W = np.sort(V * pow(int(d), -1, N) % N); gaps = np.diff(np.concatenate([W, [W[0] + N]])); m = int(0.9 * s)
        ext = np.concatenate([W, W + N]); arc = min(ext[i + m - 1] - ext[i] for i in range(s)); best_arc = min(best_arc, arc / s)
    Wr = np.sort(np.array(rng.sample(range(1, N), s))); ext = np.concatenate([Wr, Wr + N]); m = int(0.9 * s); rnd_arc = min(ext[i + m - 1] - ext[i] for i in range(s)) / s
    xs = np.sort(px[V]) / p; ys = np.sort(np.minimum(py[V], p - py[V])) / (p / 2); grid = (np.arange(1, s + 1)) / s
    ksx = float(np.abs(xs - grid).max()); ksy = float(np.abs(ys - grid).max())
    # AP baseline: V = {1..s}
    AP = np.arange(1, s + 1); r2a = np.zeros(N, dtype=np.int64)
    for v in AP: r2a[(v + AP) % N] += 1
    r2a[(2 * AP) % N] -= 1; Tap = int(r2a[AP].sum())
    return dict(bits=bits, seed=seed, N=N, p=p, s=s, iters=iters, T_init=T0, T_final=cur, T_pred=pred, ratio_init=T0 / pred, ratio_final=cur / pred, T_AP=Tap, ratio_AP=Tap / pred,
                best_arc90_over_s=best_arc, random_arc90_over_s=rnd_arc, ks_x=ksx, ks_ybar=ksy, ks_expected=0.87 / math.sqrt(s), hist=hist)

if __name__ == '__main__':
    print(json.dumps(run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))), flush=True)
