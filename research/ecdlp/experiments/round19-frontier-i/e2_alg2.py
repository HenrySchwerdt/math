"""E2: per-pass success of Mahalanobis-Mallick Algorithm 1+2 (real linear algebra over F_q) vs
the claimed 0.6*(log p)^2/p, and the exhaustive Problem-L solver (all C(N,l) supports, via the
validated dlog-equivalent zero-sum test) on the SAME passes (small cases only)."""
import sys, random, itertools, json, time
from ecL import *

def alg2(K, l):
    """Paper's Algorithm 2 on l x N basis K (N = 2l). returns list of rows with >= l zeros (checked at each stage)."""
    N = len(K[0]); q = QMOD
    hits = []
    cand = 0
    def check(rows):
        nonlocal cand
        for v in rows:
            cand += 1
            if sum(1 for x in v if x == 0) >= l: hits.append(v)
    for blk in range(2):
        cols = list(range(blk * l, blk * l + l))
        A = [r[:] for r in K]
        # forward elimination -> lower triangular in block (rows combos)
        ok = True
        for t, c in enumerate(cols):
            piv = next((i for i in range(t, l) if A[i][c]), None)
            if piv is None: ok = False; break
            A[t], A[piv] = A[piv], A[t]
            inv = pow(A[t][c], -1, q)
            A[t] = [x * inv % q for x in A[t]]
            for i in range(t + 1, l):
                if A[i][c]:
                    f = A[i][c]; A[i] = [(a - f * b) % q for a, b in zip(A[i], A[t])]
        if not ok: continue
        check(A)
        for t in range(l - 1, -1, -1):
            c = cols[t]
            for i in range(t):
                if A[i][c]:
                    f = A[i][c]; A[i] = [(a - f * b) % q for a, b in zip(A[i], A[t])]
        check(A)
    return hits, cand

if __name__ == '__main__':
    n = int(sys.argv[1]); qlo, qhi = int(sys.argv[2]), int(sys.argv[3]); passes = int(sys.argv[4]); seed = int(sys.argv[5])
    do_ex = len(sys.argv) > 6 and sys.argv[6] == 'ex'
    rng = random.Random(seed)
    l = 3 * n; N = 6 * n; mons = monomials(n)
    E, r, pts = gen_curve(qlo, qhi, rng); QMOD = E.p
    P, Q, m = random_instance(E, r, pts, rng)
    Cn = comb(N, l)
    succ = useful = 0; ex_succ = 0; cands = 0; t0 = time.time(); wrong = 0
    for ps in range(passes):
        I = rng.sample(range(1, r), 3 * n - 1); J = rng.sample(range(1, r), l + 1)
        Pp = [E.mul(s, P) for s in I]; Qp = [E.neg(E.mul(s, Q)) for s in J]
        allp = Pp + Qp
        if len(set(allp)) < N or None in allp: continue
        M = [row(pt, mons, QMOD) for pt in allp]
        K, rk = nullspace_left(M, QMOD)
        if len(K) != l: continue
        hits, c = alg2(K, l); cands += c
        if hits: succ += 1
        for v in hits:
            mm = kernel_vector_to_dlog(v, I, J, r)
            if mm is not None:
                if E.mul(mm, P) == Q: useful += 1; break
                else: wrong += 1
        if do_ex:
            # exhaustive: any 3n'-subset with zero sum using known logs (validated equivalent in E1)
            logs = [s % r for s in I] + [(-m * s) % r for s in J]
            f = False
            for S in itertools.combinations(range(N), l):
                if sum(logs[i] for i in S) % r == 0: f = True; break
            ex_succ += f
    rec = dict(n_prime=n, l=l, N=N, q=E.p, r=r, C=Cn, passes=passes, alg2_hit_passes=succ, alg2_useful=useful,
               wrong=wrong, exhaustive_hit_passes=ex_succ if do_ex else None, candidates_per_pass=cands / max(passes, 1),
               seed=seed, secs=round(time.time() - t0, 1))
    print(json.dumps(rec))
