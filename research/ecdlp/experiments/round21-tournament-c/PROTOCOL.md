# PROTOCOL — RUN-79eebc14-c6da-4878-92ec-d407755cee65 (round 21, tournament explorer C)

Pre-registered before any experiment script was run (no pilots). Academic toy curves only. Curves: `find_prime_order_curve(bits, seed)`
from round12-inventor-c/lib12.py (prime order r > 4 sqrt p, P a generator), counted ops via the same `Ops` class. Code: run_c.py (this directory).
Hash of this file in PROTOCOL.sha256; later changes only in PROTOCOL_ADDENDUM.md (separately hashed, written before the affected run).

## E1 (idea C1, Hankel/Toeplitz: linear complexity of the whole sequence)
Sequence s_k = x(kP) in F_p, k = 0..2r+9 (period r). Berlekamp–Massey over F_p gives linear complexity LC. bits in {10,12,14}, seeds 1..3.
Also y(kP). Controls: (a) random r-periodic sequence over F_p (same p, r): expected LC = r; (b) planted: r-periodic sequence produced by a random
linear recurrence of order L=r//4 (LC must come back as r//4, else BM pipeline invalid). Prediction (null): LC(x) >= r-2 on all 9 curves.
Survival rule: LC <= 0.9 r on >= 1 curve of every size. Otherwise killed.

## E2 (idea C2, Pollard–Strassen compressibility: P-recursive / holonomic in the index)
Sequences u1_k = x(kP), u2_k = y(kP), u3_m = prod_{j<=m}(X0 - x(jP)) with X0 = x(Q) random, k,m = 1..n. Guess recurrence
sum_{i=0}^{d} c_i(k) u_{k+i} = 0 with deg c_i <= e, 1<=d<=6, 0<=e<=6, equations n = (d+1)(e+1)+60 (>= 60 spare), nullspace over F_p by Gaussian elimination.
bits in {14,18} seeds 1..2. Positive controls: u = k! mod p (needs d=1,e=1) and u = Catalan/central binomial mod p (d=1,e=1); both must be found. Prediction: no
nonzero solution for any real sequence. Survival rule: any nullspace with spare >= 60 equations for a real sequence (not a control).

## E3 (ideas C3, C4: structural checks, exact algebra)
(a) toy p in {211, 1009}: matrix N_{AB} = x(A+B)+x(A-B) over all pairs A,B of non-infinity points with x_A != x_B; D_{AB} = (x_A-x_B)^2; report rank_Fp(D∘N). Claim: <=3.
(b) State sum_{a<2^n}|a>|aP>, n = ceil(log2 r), r in {~2^8,~2^10}: for each cut j (low j bits | high bits and target) compute singular values of the 0/1 matrix.
Claim: all singular values equal 1 (flat), rank = min(2^j, 2^(n-j)); lossy truncation to bond chi has fidelity chi/rank. (Exact linear algebra; no cost ratio.)

## E4 (idea C5, CRT in the unit group Z/r^*: multiplicative-character leak; self-reduction by known multipliers)
For q in {2,3,5} with q | r-1 (curves chosen with r = 1 mod 30), class c_q(k) = ind_g(k) mod q (g a generator of (Z/r)^*, or equivalently the q-th power residue class of k).
Q = kP for ALL k = 1..r-1 (full enumeration, so no sampling error). Feature set F (frozen, 160+ functions of Q and neighbours): low 8 bits of x, y; x mod m, y mod m (m=3,5,7,9,11);
Legendre of x, y, x+1, x-1, x-Px, y-Py, x*y; parity and threshold [x<p/2],[y<p/2]; same functions for x(Q+jP), j=+-1,+-2; for x(2Q), x(3Q), x(5Q); relative features
(x(Q+P)-x(Q)) mod 2, mod 3, Legendre of difference, carry bit of x(Q)+Px. Test: chi-square independence of each feature (alphabet <= 256) against c_q(k), full-enumeration counts;
statistic: Cramer's V and the "advantage" adv = max over alphabet values of |P(c=q-class|f)-1/q| aggregated by the Bayes-accuracy gain acc-1/q (in-sample, so reported with the
chi-square null expectation of the optimism (alphabet*q)/(2 n)). Bonferroni at 0.01 over (features x q). Bits 16,18,20, curves seeds with r=1 mod 30 (first 2 found). Positive control: planted
feature = c_2(k) flipped with probability 0.45 (adv 0.05; hash of the point), must be flagged at all sizes else no null is claimed.
Bar to matter (derivation in the report): adv >= C (log r)^(1/2) r^(-1/4); at 2^20 about 0.03*C. Survival: Bonferroni-significant AND adv above bar at >= 2 sizes in both curves of that size. Else null.
Cost model uses the same-implementation rho control of section E6.

## E5 (idea C6, Reed–Solomon list decoding of the DLP codeword: excess low-degree alignment)
Points (x(jP), j) and (x(jP), j^2 mod p), j=1..N, N=1200 (<= (r-1)/2), bits in {16,18}, seeds 1..3. d=1: for each j the largest multiplicity of equal slopes to all others (largest set
of points collinear with it); null = same statistic with a uniformly random permutation of the labels j (50 permutations). Positive control: planted 30% of labels replaced by a*x+b.
Survival rule: observed max multiplicity exceeds the null 99.9% quantile for both targets on >= 4 of 6 curves. (d=2 not tested; stated as a limit.)

## E6 (same-implementation rho control)
rho (DP walk with 20-partition additive steps as in round20 pipelines.rho, same `Ops`), sizes bits in {12,14,16,18,20,22,24}, 10 instances each (curve seeds 700..), counted ops; fit
ops = alpha sqrt(r) + gamma by least squares with bootstrap 95% CI. No log-log exponents. Used only for the cost bar of E4 (and any other surviving idea).

## Verdict rules
An idea is "survives" only if its pre-registered survival rule fires AND the cost model/same-implementation control says it can beat rho. Nothing here claims a speedup unless measured end to end.
