# Round 12 inventor A — pre-registered benchmark protocol (RUN-ff67c875, ECDLP-42)

Written and hashed BEFORE any benchmark was executed. Hash in PROTOCOL.sha256.

## Instances (shared by every candidate and by the rho baseline)
- bits b in {12,14,16,18,20,22,24}; seeds 1..10 for b<=20, seeds 1..8 for b in {22,24}.
- p: random prime, p = 3 mod 4, in (0.75*2^b, 2^b); curve y^2=x^3+ax+b0 with random (a,b0) until
  #E(F_p)=r is prime (so every nonzero point has order r). P random point, k uniform in [1,r-1], Q=kP.
  Seeds determine (p,a,b0,P,k) via python random.Random(1000*b+seed). Instances stored in instances.jsonl.
- Correctness: every recovered k is checked kP==Q; for all sizes also against toyec.dlog_bsgs.

## Cost units
- U1 = number of elliptic-curve point additions (doubling counts 1), including setup tables,
  scalar multiplications aP+bQ (counted as the additions actually performed), joins/sums, lookups of
  a candidate point cost 0 extra. Reported separately: factor-base construction field multiplications,
  linear-algebra modular multiplications (analytic count of the elimination actually run), table memory
  (entries). Wall time is recorded but never used in the decision.

## Baseline: Pollard rho
- Distinguished-point rho, 32-branch additive walk on x mod 32, DP when x mod 2^d == 0 with
  2^d ~ sqrt(r)/16, restart with fresh random (a,b) after each DP (start costs counted), steps capped,
  U1 counted for precomputation of 32 branch points, starts, and every step. Success = collision with
  distinct (a,b) yielding verified k. One run per instance; failed collision (equal b) -> continue.

## Fit and statistics
- For every method and instance: y = log2(U1). Regression y = alpha*log2(r) + c over all instances of all
  sizes (OLS); report alpha, standard error, 95% CI with Student t (df=n-2). Also per-size geometric mean
  and the ratio candidate/rho per size.
- Rho exponent alpha_rho is measured on the same instances, not assumed.

## Decision rule (applied mechanically)
- BEATS-RHO-SCALING iff: success rate >= 90% at every size AND alpha_cand_hi95 < alpha_rho_lo95 AND the
  per-size geometric-mean ratio cand/rho at the largest size is < 1.
- CONSTANT-ONLY iff ratio < 1 at some size but the scaling criterion fails.
- NO-ADVANTAGE otherwise.
- A toy win is never an asymptotic claim; the verdict is about the tested domain only.

## Candidates and pre-registered model predictions
- A1 (Farey-height factor base index calculus with meet-in-the-middle relation search):
  variants l=2 (4-term relations), l=3 (6-term). Model: U1 ~ sqrt(p*s), s = number of factor-base
  unknowns, s ~ p^{1/(2l-1)} => alpha_model = l/(2l-1): 0.667 (l=2), 0.600 (l=3); control m=3-term
  join (alpha=1.0, sizes b<=20 only). Prediction: all NO-ADVANTAGE (alpha > alpha_rho ~ 0.5).
- A2 (lattice / Coppersmith-style decomposition of a target as a sum of two Farey-height points via
  the 9-dim Veronese-tensor lattice): sizes b in {16,20,24}, 200 random targets each, H = Farey
  height giving factor base ~ 1.3*p^{1/3}. Metrics: E = fraction of targets with a decomposition
  (exhaustive), S = fraction where LLL (own implementation, delta=0.99) plus all coefficient vectors
  in {-1,0,1}^9 over the reduced basis recovers a valid decomposition. A2 "viable" iff S/E >= 0.5 at
  >= 3 of 3 sizes. Prediction: S/E ~ 0 (not viable).
- A3 (E(Q)/small-coefficient lift, Miller-height coverage): treated analytically + coverage count
  (see report); no scaling claim.
