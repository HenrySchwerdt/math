# Round 13 inventor D — pre-registered protocol (RUN-22ed50a6, TSK-6788709a)

Written and hashed BEFORE any benchmark run (code is drafted but not yet executed on any benchmark instance).
Question: can an algebraic relation finder (Groebner / resultant / Semaev S_3,S_4 on an algebraically defined factor base)
make total index-calculus cost (relation search + linear algebra) < sqrt(r) on prime-field, prime-order curves?

## Prototype under test (the single most promising finder that can be implemented here: "D2")
m = 2 Semaev finder. Factor base V_x = {x in g*H : x^3+ax+b is a square}, H = mu_d, d = 2^n | p-1 (PKM 2016 multiplicative-coset
base with L(x) = x^d - c). For a target T = aP+bQ the system S_3(x1,x2,x_T)=0, x1^d=c, x2^d=c is reduced by elimination
to a univariate condition; the finder enumerates the algebraic solution set by evaluating the reduced condition on all of
V (exhaustive univariate root test, d additions per target; Groebner/resultant+gcd costs the same Otilde(d), see report).
Relations a + b k = e1 l1 + e2 l2 (mod r); sparse-incremental Gaussian elimination over F_r decides k.
Controls: D2s = same finder with V = smallest-x base of equal size.
Sympy Groebner (lex, GF(p)) of the PKM system is run only on tiny p (257..17921) as a correctness and scaling cross-check of the algebraic
formulation; it is NOT used in the decision (Sage/Magma/Singular not installed).

## Instances
Prime p = 1 mod 2^n, p in (0.75*2^b, 2^b); E: y^2 = x^3+ax+b0 random with #E(F_p) = r PRIME (order found by BSGS on a random point,
uniqueness from r > 4 sqrt p); P random, k uniform in [1,r-1], Q = kP. Seeds: random.Random(1000*b + seed + 7*gamma_index).
Settings: D2a: d = 2^round(log2(p)/2) (|V| ~ sqrt p, expected hit probability pi ~ d^2/(2p)).
          D2b: d = 2^round(log2(p)/3) (|V| ~ p^{1/3}, pi ~ p^{-1/3}); sizes 16..22 only.
Full pipeline (relations until k determined, k verified by kP=Q): D2a bits 16,18,20,22,24 (seeds 1..4; 24: seeds 1..3); D2b bits 16,18,20,22 (seeds 1..3).
Per-relation-only (no linear algebra run): D2a bits 26,28 (seeds 1..3, 40 targets each): measures pi and additions/relation; the total
at these sizes is a MODEL extrapolation (labelled), never a measurement.
Baseline: round12 distinguished-point rho (research/ecdlp/experiments/round12-inventor-a/common.py rho_dp, seeds = instance seed) on the same instances,
addition counts U1 including setup; additionally the analytic walk cost sqrt(pi r/2) is reported. Every recovered k is checked kP=Q.

## Cost units
U1 = elliptic-curve point additions (doubling counts 1): target generation (1 addition per target by a 32-entry branching walk, setup counted),
finder additions (d per target), plus factor-base construction square roots (reported separately in field mults ~ 1.5*log2 p each... counted as 2*log2(p) mults, TS loop excluded)
and LA modular multiplications (exact count of the sparse-aware elimination actually run: nonzeros of each pivot row used).
Headline total = U1_adds + (FB_mults + LA_mults)/10 addition-equivalents (1 affine addition ~ 10 mults); sensitivity: /3.
Wall time recorded, never used in the decision.

## Fit and decision rule (mechanical)
OLS of log2(total) on log2(r) over all full-pipeline instances of a setting, 95% CI (Student t). Rho exponent measured on the same instances.
WINS iff success 100% at all sizes AND alpha_hi95(D2) < alpha_lo95(rho) AND geometric-mean ratio D2/rho < 1 at the largest full-pipeline size.
CONSTANT-ONLY if ratio < 1 at some size but exponent criterion fails; NO-ADVANTAGE otherwise.
Toy advantage is never an asymptotic claim. rho pooled exponent is known to be depressed by setup (round12 A); a post-hoc walk-only fit may be added and is labelled post-hoc.

## Pre-registered predictions
1. D2a and D2b both succeed (100%) and are NO-ADVANTAGE; total ~ c*p (alpha ~ 1.0 +- 0.15) independent of d because cost/relation ~ p/d... per relation = d/pi = 2p/d additions and d/2 relations are needed.
2. Control D2s yields the same pi within 20% (no structural yield difference between coset and small-x bases).
3. Sympy Groebner time grows ~ d^3 or worse (PKM Table 4 trend, Magma) and its solution set equals the exhaustive one.
4. LA is not the bottleneck at m=2 (s^2 << relation search) but would be at m>=3.
