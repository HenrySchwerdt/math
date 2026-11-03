# PROTOCOL — RUN-b16fc67e (round 16, algorithm inventor H): preprocessing beyond S*T^2 ~ r on fixed toy curves

Pre-registered before any benchmark data exists. Only tiny debugging pilots (<= 20-bit, no analysis, outputs discarded) may precede the freeze.

## Question
For ONE fixed curve (prime order r, generator P), advice A of size S built once. Online: given Q = kP (k uniform in [1,r)), output k
using T counted group operations (point add/double = 1 op; verification kP == Q counted; table probes, comparisons, hashing, bit
access free in T but reported separately as "probes"). Quantity: rho = S*T^2/r. Success = rho falls with r, with CI, out of sample.
Reference point: inventor C (RUN-aabd43b1) fixed-walk DP table, rho ~ 4, slope of log2 rho vs bits 0.027. Trivial full table: S=(r-1)/2, T=1, rho=1/2.

## Sizes and curves
bits(p) in {16,20,24,28,32}; r ~ p ~ 2^bits. Curves from round12 `find_prime_order_curve(bits, seed)`, seeds 0,1,2 (15 curves), prime order certified.
Curves generated once (`curves.json`) and frozen.

## Mechanisms
- E1 (sorted x-table + interpolation search): BSGS-style table of x(jP), j<=S sorted; giant steps Q + c*(S P). Measure group ops, probes
  (interpolation search vs binary), rho with T = ops (and T = ops + probes as a sensitivity). S = r^{a}, a in {1/3,1/2,2/3}; plus full
  table (S=(r-1)/2) at bits <= 24. Descriptive only; no success rule (cannot beat BSGS S*T = r by construction; reported as obstacle check).
- E2 (comparison decision tree, greedy, with T=2 online ops: features of Q, Q+P, Q-P: 32 bits of x, 15 quantile thresholds each).
  Train N=min(2^17,r/4) distinct k' = min(k,r-k) (distinct via affine stride), test N held-out disjoint k'. Labels: L1 = top 4 bits of
  k' (16 classes), L2 = k' mod 16. Best-first information-gain tree, node budgets S_nodes in {15, 255, 4095}.
  Positive control: planted leak (low 2 bits of x replaced by top 2 bits of k') must be detected.
  Success for "x-comparison leaks k": held-out accuracy Wilson 99% lower bound > 1/16 + 0.005 at >= 3 of 5 sizes for the real curves, for
  L1 or L2 (and control must pass). Otherwise recorded as null. Even success would not imply S*T^2 < r without a further construction.
- E3 (walk tables, fixed-curve tuning). Algorithm C2-style: m walks from s_i P, step R <- R + a_{h(x(R))} P, DP iff (hash2(x) & (L-1)) == 0,
  walk cap 20L; table DP point (x,y)->scalar. Online: trial t=0,1,...: R=Q+tP, walk to DP (cap 20L), lookup; hit gives k = u - t - sum(a) mod r;
  verify kP==Q. Query fails after 400 trials. T = total ops including failed trials and verification.
  Generic grid G: L=2^d, d in {d0-1,d0,d0+1} with d0=round(bits/3); m = mult*r^{1/3}, mult in {0.5,1,2,4}; step family F0 (31 parts by x mod 31,
  a_j uniform [1,r)). Variant "B0" = best-of-G by training rho (generic tuning, 12 candidates).
  Curve-tuned "H": candidates = G x step families {F0, F1 small steps a_j in [1,w], w=2^6 and 2^12 (kangaroo-like), F2 multiplicative-hash
  partition with R in {16,64,256} parts and hash seed, F3 bit-dependent a_j = +/- structured} x 3 step seeds x 3 table seeds; 48 randomly drawn candidates
  (draw seed fixed) evaluated on TRAIN queries (150 queries, seed 'train'); winner = lowest training rho among those with train success rate >= 0.98.
  Evaluation, out of sample: EVAL-A same table, 400 fresh queries (seed 'evalA'); EVAL-B same step function and parameters, 3 freshly built tables
  (new table seeds), 150 fresh queries each. Same eval for B0 winner.
  S = number of stored distinct DP entries. T = mean ops per query over queries (rho uses (mean T)^2). Preprocessing ops reported separately.
  95% CI: bootstrap (2000) over queries within curve, then over curves (3 per size). Slope of log2 rho on bits: bootstrap CI of OLS slope.
  Success for E3: out-of-sample slope upper CI bound < 0 for H (EVAL-A and EVAL-B) AND H beats B0 by ratio CI excluding 1 at >= 3 sizes.
  Constant-factor gain only (no slope fall) is reported as such. Success rate must be >= 0.99 on eval or the size is flagged.

## Decision rules (all)
Falling ratio claim requires: slope CI upper < 0, out of sample, with success rate >= 0.99, preprocessing reported. Toy sizes are not asymptotic.
Failures and nulls are reported. No result is a statement about proof status. Deviations after freeze are recorded in PROTOCOL_ADDENDUM.md.
Literature (Shoup, Corrigan-Gibbs-Kogan, Coretti-Dodis-Guo, Bernstein-Lange, Hellman) cited from memory, 0 web lookups, not re-verified.
