# Round 7 discovery test: minimal degree of [m]-invariant class functions (D1)

RUN-73ace464-1565-479c-9409-6690c560c514 / TSK-90871360-32b5-46df-bd35-f6d2ce60a52b. Pre-registered before execution.

## Question (hypothesis D1)
Let E/F_p be short Weierstrass with N = #E(F_p) odd, X = {x(R): R in E(F_p) affine}, |X| = M = (N-1)/2.
phi_m(x(R)) = x(mR) (m coprime to N) is a permutation of X with c cycles (orbits of <m> on E(F_p)/{+-1}).
d*(sigma) = least degree d >= 1 of a nonconstant polynomial h in F_p[x] with h(sigma(x)) = h(x) for all x in X.
D1: the Lattes structure of phi_m gives NO cheap canonical form for [m]-orbits, i.e. d*(phi_m) behaves like
a random permutation of the same cycle type (null model), and satisfies the proved bound d* >= M/m^2.

## Exact procedure (stdlib Python, toyec.py, seed 7, wall limit 240 s)
1. Stratum A: 20 random curves (p random prime in [61,211], random a,b) with N odd and gcd(N,6)=1.
2. Stratum B: scan 300 further random curves (same ranges, M>=30, gcd(N,6)=1); take the 10 with largest c/M.
3. For each curve and m in {2} (also m=3 for stratum A): compute d*(phi_m) by incremental Gaussian elimination
   over F_p on columns x^i - sigma(x)^i (i = 1,2,...): d* is the first i whose column is dependent on columns 1..i-1
   (constants are the trivial solution; nonconstant invariants <=> first dependency).
4. Null: 3 draws sigma' = pi phi pi^-1 (pi uniform random permutation of X), same cycle type; compute d*(sigma').
5. Record M, c, N, p, d*(phi), d*(null draws), generic prediction M-c+1, bound ceil(M/m^2).

## Pre-registered decision rule
- Sanity (must hold, else bug): d*(phi_m) >= ceil(M/m^2) for every curve.
- Statistic r = d*(phi_2)/(M-c+1).
- D1 SUPPORTED (no hidden structure) if r >= 0.98 for >= 90% of curves and d*(phi) is never below min(null draws) - 0 by more than 2.
- D1 REFUTED / hidden structure if median r <= 0.9, or >= 20% of curves have d*(phi) < min(null draws) - 2.
- Otherwise inconclusive. Finite toy test: supports no statement about large p. No speed-up claim follows from either outcome.
