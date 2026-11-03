# Round 11 / Frontier E (ECDLP-41, RUN-7112aed9): pre-registered protocol

Written and hashed (PROTOCOL.sha256) BEFORE any script in this directory was executed.
Owner: RUN-7112aed9 (frontier-explorer). Exploratory; tests supports only the tested domain.

## Common setup
Curve: y^2 = x^3 + a x + b over F_p, p prime in [2^19, 2^19+5000) chosen by seeded search (python random.Random(seed),
seeds 1 and 2), #E = r PRIME, r != p, r > 1000. P = a non-identity point (order r). x_k = x(kP) as the integer
representative in [0,p), k = 1..r-1. Symmetry x_k = x_{r-k}: the *primitive* data is vals[k]=x_k, k=1..M, M=(r-1)/2
(all distinct). Full sequence is the even fold of vals.
Null model (all tests): vals randomly permuted among the indices 1..M (marginals preserved EXACTLY, even symmetry
preserved, all index structure destroyed). n_null draws, seeded.
Standardised statistic: z = (stat - null_mean)/null_sd; two-sided MC p = (1 + #{|z_null| >= |z_obs|})/(n_null+1).
A (statistic, parameter) is a DETECTION only if p = minimum attainable (obs |z| above ALL null draws) in BOTH seeds.
Positive control must be detected (else the test is invalid for the stated sensitivity); negative control (iid uniform
vals, same pipeline) should not be flagged.
Tools: Python 3, numpy; research/ecdlp/experiments/lib/toyec.py Curve for group law; seeds fixed in scripts.

## E1: local integer structure of (x(Q), x(Q+jP)) -- carries, bits, order, differences  [script e1_local.py]
Mechanism exploited: integer representatives of x(Q) and x(Q+jP) being locally correlated (bit/carry/order/difference).
Shifts j in {1,2,3,5}. Pairs (x_k, x_{k+j}), k=1..r-1-j. Statistics per j:
 (G) independence chi-square of the 16x16 grid of top-4-bit pairs (empirical marginals);
 (B) max over the 19x19 bit pairs (bit i of x_k, bit i' of x_{k+j}) of |phi|*sqrt(N) (empirical marginals);
 (D) chi-square of the histogram of d=(x_{k+j}-x_k) mod p in 4096 equal bins (vs uniform);
 (S) count of pairs with min(d, p-d) < p/1024 (small-difference / carry-free proximity).
n_null = 150 (min attainable p ~0.0066). 16 (stat,j) cells; replication in both seeds is the multiplicity guard.
Positive control (planted): for a random 2% of k in [1,M-1], vals[k+1] := (vals[k] + u) mod p, u uniform [0,p/1024).
Negative control: iid uniform vals.
KILL CONDITION H_E1 (some local integer correlation exists): no cell detected in both seeds, or control failure.

## E2: sorted-neighbour index-difference leak ("sorting-network / closest-pair" mechanism)  [script e2_sorted.py]
Mechanism: sort vals; if integer-adjacent x-values had index differences concentrated on some D (or D-set), then
x(Q) near x(Q+D P) would give a comparison-based locator. For w in {1,2,4}: take all pairs at sorted distance w,
indices (k,k'); record BOTH folded differences d1=|k-k'| and d2=min(k+k', r-k-k') (sign ambiguity). Statistics:
 (C) collision sum sum_d m_d^2 over the multiset of recorded d values; (X) max multiplicity max_d m_d.
n_null = 100 random permutations of indices. Positive control: for a random 0.2% of k in [1,M-D0] (D0=12345)
vals[k+D0] := vals[k] + u, u uniform [1,16]. Negative control: iid uniform vals.
KILL CONDITION H_E2: no (stat,w) cell detected in both seeds, or control failure.

## E5: smoothness-over-Z / Miller height arithmetic (counting table, no sampling)  [script e5_height_table.py]
Heuristic: #{P in E(Q) of rank rho with canonical height <= T} ~ T^{rho/2}. To cover E(F_p) (~p classes) with lifts
need T >= p^{2/rho}; naive numerator size ~ T/ln2 bits. Table for rho in {1,2,5,10,18,29}, p in {2^64,2^160,2^256}.
No pass/fail: it quantifies the Miller obstruction.

## Not run (theory/literature only, see report): E3 comparison-tree model; E4 HNP/hard-core-bit lattice route.
