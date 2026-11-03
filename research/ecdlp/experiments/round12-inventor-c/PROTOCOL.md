# Pre-registered benchmark protocol — round12-inventor-c (RUN-aabd43b1, ECDLP-44)

Registered before any benchmark run. Development used a *tuning pilot* (pilot.py, pilot2.py, pilot3.py;
seed namespace `pilot`, curves 'pilot', sizes 28/32 bits, <=30 trials) to choose DP-length constants and
table parameters, and a correctness smoke test (smoke.py, 16-24 bits). Pilots are NOT benchmark data.
A bug found in the pilot (DP table keyed by x only conflated P and -P) was fixed before registration.
Frozen code (sha256 in SHA256_code_frozen.txt): lib12.py, algos.py, bench.py, analyze.py.

## Cost model and metric
- Unit: one affine point addition or doubling = 1 group op (1 field inversion + 3-4 mults + few adds, identical
  for all algorithms). Scalar/tag arithmetic mod n and hashing/dictionary lookups are free (reported separately
  as memory). Start-point scalar multiplications are counted at their true add/double count.
- One-time step-table setup (31 random combinations a_j P + b_j Q, ~93 log2 n ops, polylog) is excluded from
  `ops` and reported as `setup`. Primary metric = `ops` (excl. setup).
- Machine-independent: counts only; wall time is reported but never used for a decision.

## Instances
- Curves: for bits b in the size lists below, `find_prime_order_curve(b, 'c12')`: random prime p of b bits,
  random (a,b), #E = r prime verified by BSGS in the Hasse interval (unique multiple of ord(P) there and prime),
  P a random point (generator since r prime). n = r (about 2^b). One curve per size; "same curves and seeds":
  every algorithm sees identical (curve, P, k_t, walk-seed w_t) with k_t = Random('k-{b}-{t}').randrange(1,n),
  walk rng = Random('w-{b}-{t}').
- Cross-check: for b <= 32, the first 4 trials per size assert lab `dlog_bsgs(E,P,Q,n) == k`. For all other
  runs correctness = recovered k equals the planted k (so kP = Q).

## Algorithms and parameters (frozen)
- ref: Pollard rho, DP variant, 31-partition (x mod 31) r-adding walk, a_j,b_j random mod n, DP iff
  (x & mask)==0 with mask+1 = largest power of 2 <= round(sqrt(n)/16); walk cap 20(mask+1) then restart;
  collision between DP of different walks resolved as k=(a1-a2)/(b2-b1). DP table keyed by the full point.
- C1: same, plus negation classes (y canonicalised to <= p/2, tags negated), detection of 2- and 4-cycles of
  classes, escape by doubling the smallest-x member of the cycle (Bos-Kleinjung-Lenstra / Wiener-Zuccherato style).
  Same L, same walk-seed. Sizes {24,28,32,36,40,44}; trials 16 (b<=36), 12 (b>=40).
- C2: fixed point-only walk f, one table per size: m = int(2 n^(1/3))+1 chains from random s_i P, mean DP
  length L = largest power of 2 <= int(n^(1/3)); queries: walk from Q+tP (t=1,2,...; 1 op per restart) until
  a DP in the table. Sizes {20,24,28,32,36}; 32 queries per size (k_t as above).
- C3: M-instance batch with point-only walks, shared DP set, union-find with potentials; walks started from a
  uniformly random still-unresolved node (incl. base node 0 = P); L = largest power of 2 <= round(sqrt(n/(M+1))/8).
  N-sweep: M = 16, sizes {24,28,32,36} x 12 trials, 40 x 6 trials. M-sweep: 32 bits, M in {1,2,4,8,16,32,64}, 12 trials.
  Reference for C3 per-instance ratio = mean `ops` of ref at the same size (single instance, unpaired).

## Statistics
- Exponent e: OLS slope of log2(mean ops over trials) against log2(n) over the listed sizes; 95% CI by
  nonparametric bootstrap (4000 resamples of trials within each size, seed 12345). Paired ratio CIs (C1) by
  bootstrap over trial index (seed 7); unpaired for C3 (seed 99).
- Sanity gate: ref exponent must lie in [0.45, 0.55] else the harness is flagged as invalid.
- Any incorrect output (recovered k != planted k) is reported and counts as FAILURE of that candidate.
- Runtime limit: each mode run in its own process < 5 min wall; if exceeded, reported as limitation (no
  truncation of results).

## Decision rules (fixed in advance)
- EXPONENT-IMPROVED (domain-limited, same cost accounting as ref): 95% CI upper bound of e_cand < 0.45 AND
  lower-CI of e_ref >= 0.45, with total cost per instance including all preprocessing charged to that one instance.
- CONSTANT-FACTOR GAIN (C1): ratio ref/C1 has 95% CI lower bound > 1.10 at every size >= 28 bits and
  |e_C1 - e_ref| < 0.05 (exponent unchanged); the gain is then labelled constant factor and nothing more.
- C2: (i) "online-exponent improvement in the preprocessing model" iff upper CI of e_on < 0.45 and no incorrect
  output; (ii) single-query total-cost exponent claim iff the rule EXPONENT-IMPROVED holds for pre+online
  (predicted NOT); (iii) "sits on the generic S*T^2 ~ N curve" iff |slope of log2(S T^2/n) vs bits| < 0.10;
  report break-even number of queries = pre / (ref_mean - online_mean).
- C3: (i) "amortised batch gain" iff ref/per-instance ratio at M=16 has CI lower bound > 1.5 at every size >= 28 bits;
  (ii) "square-root-in-M law" iff the fitted per-instance exponent in M (M >= 2) has 95% CI inside [-0.65, -0.35]
  and the n-exponent CI of per-instance cost (M=16) intersects [0.45, 0.55] (no exponent change in n).
- A speedup that satisfies only constant-factor/amortised rules is never reported as an exponent improvement.
  Toy-size advantage is not an asymptotic claim.
