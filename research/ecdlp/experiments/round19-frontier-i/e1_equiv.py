"""E1: exact check of the Problem L equivalence on toy curves:
for every 3n'-subset S of N random points, rank(M_S) < 3n'  <=>  sum_S = O (all points distinct)."""
import sys, random, itertools, json
from ecL import *
seed = int(sys.argv[1]); rng = random.Random(seed)
out = []
for n, l, qlo, qhi in [(1, 3, 50, 120), (2, 6, 300, 700), (2, 6, 1500, 2500), (3, 9, 3000, 6000)]:
    E, r, pts = gen_curve(qlo, qhi, rng)
    q = E.p; mons = monomials(n); N = 3 * n + l
    P, Q, m = random_instance(E, r, pts, rng)
    sc = rng.sample(range(1, r), N)
    Ppts = [E.mul(s, P) for s in sc]
    # all distinct points required
    if len(set(Ppts)) < N: continue
    M = [row(pt, mons, q) for pt in Ppts]
    K, rk = nullspace_left(M, q)
    agree = dis = zs = 0
    for S in itertools.combinations(range(N), 3 * n):
        tot = None
        for i in S: tot = E.add(tot, Ppts[i])
        sub = [M[i] for i in S]
        deficient = rank_mod(sub, q) < 3 * n
        zero = tot is None
        zs += zero
        if deficient == zero: agree += 1
        else: dis += 1
    rec = dict(seed=seed, n_prime=n, l=l, N=N, q=q, r=r, D=len(mons), rank_M=rk, kernel_dim=len(K),
               subsets=comb(N, 3 * n), agree=agree, disagree=dis, zero_sum_subsets=zs)
    print(json.dumps(rec)); out.append(rec)
