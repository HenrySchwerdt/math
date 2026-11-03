# Round 4 / ECDLP-12 pre-registered protocol (RUN-597fcdfe-7b4f-4a9a-a0be-a9ee84390a34)

Hypothesis H (HYP-db508348): on E(F_p), #E=r prime, factor base V_B={Q != O : x(Q)<B} (symmetric, n=|V_B|, nx=n/2
distinct x-values with points), no (m,B) gives relation-collection cost below sqrt(p) group operations at toy sizes.

Domain: buckets 2^k, k in {12,14,16,18}; per bucket p = random prime in [0.9*2^k, 1.1*2^k]; 3 curves per bucket
(a,b uniform mod p; reject singular, #E not prime, #E==p, r<100). #E by Legendre/square-count table (numpy).
Master seed 20261107; stream per bucket = random.Random(f"20261107-{k}"). P = random affine point (order r).
Configs: m in {2,3}, B = max(2, floor(beta * p^(1/m))), beta in {0.5,1,2}  (6 configs / curve).

Measurement 1 (pi): EXACT enumeration of all m-sums of V_B (m=2: n^2 pairs; m=3: all n^3 triples, built as
(pair-sum set) + V_B; no subsampling expected - sizes are small; if any subsample is used it is reported). pi =
|distinct points reachable|/#E. Heuristics: H1 = n^m/(m! r) (n counts both signs; correct accounting) and H2 = task formula
(2n)^m/(m! r) capped at 1 (double counts signs since V_B already symmetric; reported for comparison only).

Cost model (unit = one group operation OR one hash lookup, 1 each, field ops not weighted; one square-root/root-solve = 1 unit,
which favours the candidate). Relations needed N = nx + 1 + 10. Attempts = N/pi.
 (a1) NAIVE-A: hash table of (m-1)-sums (build cost = #distinct unordered (m-1)-sums, 1 op each); attempt on R tests R-V in table for
      every V in V_B (cost 2 per V: 1 subtraction + 1 lookup, over the nx x-classes => 2*nx, using sign symmetry) +1 to form R.
 (a2) NAIVE-B: hash table of all m-sums (build n^m/m!, memory n^m/m!); attempt = 1 lookup + 1 op.
 (b)  SEMAEV (m=2): per attempt, for each of the nx x1 values solve quadratic in x2 given x(R) (1 unit each) + 1 for R.
 Linear algebra: m*nx^2 (sparse Wiedemann-style count) added to all. Total = build + attempts*cost + LA. Best decomposer = min.
Baselines: sqrt(pi r/2) (rho expectation formula) and sqrt(p); MEASURED: BSGS op count (instrumented, 10 random Q) and
Pollard rho (Brent, 32-way additive walk, DP-free, counts ops) mean over 20 runs, on 1 curve per bucket.
Scaling: for each config, OLS slope of log(mean total cost over curves) vs log(mean p per bucket) over 4 buckets; likewise for sqrt(p).
S_3 oracle: 2000 random triples of curve points (P1,P2,P3 incl. sign choices): S_3(x1,x2,x3)==0 iff +-P1+-P2+-P3 = O for some signs
(checked both: on triples constructed with P3=P1+P2 and on random triples, comparing against the group law result); plus quadratic
coefficient check in x2. Semaev attempt-route consistency: at p~2^12 and 2^14, 300 random R, Semaev loop finds decomposition iff
brute-force pair table says so.
End-to-end: at p~2^12 and p~2^14 (first curve), best config (min total cost by model), full relation collection (random aP+bQ),
sparse relations, incremental Gaussian elimination mod r (unknowns: log of each x-class representative, and k), solve k for random Q,
verify via dlog_bsgs and k*P==Q. Failure recorded with cause.

Decision rule: H FALSIFIED iff some configuration has mean measured/model total cost < 0.5*sqrt(p) in the 2^18 bucket (the cost
model total, per curve, mean over curves) AND its log-log exponent over p is < 0.5. Otherwise H SURVIVES on tested domain only. Exponent
estimates from 4 points are indicative only (no CI claimed beyond the OLS s.e.). Toy results do not establish asymptotics.
Runtime: each script run < 5 min; if exceeded, reduce curves and state so.
