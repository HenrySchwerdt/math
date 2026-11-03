# Round 11 / frontier D protocol (RUN-29c93068, ECDLP-37) — pre-registered before any registered run

Owner: frontier-explorer (claude-sonnet-5-5, self-reported). Toy sizes only; nothing here is a complexity claim.
Environment: python-sat 1.9.dev17 (Glucose4, CaDiCaL 1.9.5), pycryptosat 5.17.0 (CryptoMiniSat, native XOR; pip-installed in the sandbox, not a repo dependency), numpy 2.5.3.
Debug/self-tests (tiny n<=6 to check encodings) are excluded from results.

## T1 Structure-aware SAT for [k]P = Q
Instances: Montgomery curves B y^2 = x^3 + A x^2 + x over F_p (B=1), p prime of n+2 bits, #E = 4r with r prime of exactly n bits,
P of prime order r, k uniform in [1, r-1], Q = [k]P (x only; the solver may return k or r-k, both verified by a Python ladder).
n = 5..12, 3 instances per n, rng seed 2111 (instance generator) — instances are identical for every solver/encoding.
Encodings (key bits k unknown, n variables):
 E1 "ladder": x-only Montgomery ladder, projective (X:Z), fixed first bit, each step = conditional swap + differential add + double
    (x(P) a constant, a24 constant), all mod-p arithmetic as bit-level circuits with existential quotient/remainder (as round 10); final constraint X_k = xQ * Z_k mod p and Z_k != 0; plus k < r.
 E1x "ladder+XOR": identical circuit, full-adder sum bits / XOR gates emitted as native XOR clauses for CryptoMiniSat.
Solvers: Glucose4 (conflict budget 4e6 and 240 s wall via interrupt; conflicts and seconds recorded), CaDiCaL 1.9.5 (240 s subprocess timeout; seconds), CryptoMiniSat on E1x (240 s; seconds + conflicts if reported).
Cardinality: no natural cardinality constraint exists for uniform k (only k < r), so Minicard/Gluecard are NOT run; recorded as not applicable.
Comparator: rho group-operation count sqrt(pi r/2) (and the round-10 affine-encoding slope 1.23 as a cited reference, not re-run).
Estimand: exponent a in conflicts (resp. seconds) ~ c * r^a, OLS on log-log pooled over all instances (censored runs counted at their budget value = lower bound, so censoring can only LOWER the fitted exponent), 95% CI by bootstrap over instances (2000 resamples, seed 7).
DECISION RULE (fixed now):
 - PROMISING iff the upper 95% CI bound of the exponent a < 0.5 for the conflicts metric AND for the seconds metric of at least one solver, with fewer than 20% of runs censored.
 - NEGATIVE iff the lower 95% CI bound >= 0.5 (not sub-rho scaling).
 - otherwise INCONCLUSIVE. Wall-seconds also include circuit-size growth (~n^3), so the conflicts metric is primary; the secondary metric is secs.
 - Additional kill criteria: ratio vars(n=12)/vars(n=5) reported; if the solver exponent is >= 1 (brute-force) the encoding is "no better than enumeration".
Per-run time limit < 5 min (240 s cap).

## T2 Hensel-section cocycle
Curves y^2 = x^3 + a x + b over F_p with prime N = #E(F_p) != p (p ~ 1000, 4100, 12000, 30000; two curves each when feasible, seeds 11, 12), lift (A,B) = random lift mod p^3, generator P random.
Set-theoretic lift l(R): x = integer representative in [0,p), y by Hensel. Cocycle c(R) = l(R)+l(P)-l(R+P) in E_1 (kernel of reduction), formal parameter z=-X/Y (additive mod p^3 for short Weierstrass).
Digits: d1(R) = (z(c(R))/p) mod p (the explicit cocycle eta); d2(R) = z(c(R))/p^2 mod p (the p^3 digit); g(R) = z([N] l(R))/p mod p; u2(R) = (x(s(R))-x(R))/p mod p with s(R) = [p m]l(R), m = p^{-1} mod N; u3 analogously at precision p^3 (s3 = [p^2 m']l, m' = p^{-2} mod N).
Exact identities to check (sanity of derivation, must hold or the derivation is wrong): g((k+1)P) = g(kP) + g(P) - N d1(kP); hence g(kP) = k g(P) - N S_k with S_k = sum_{i<k} d1(iP), and S_N = g(P); and u2(R) = lambda * y(R) * g(R) with a constant lambda (to be fitted, expected -2 N^{-1}-type constant) — fitted on one point, verified on all.
Sequences tested along k = 1..N-1: d1, d2, S_k, g, u2, u3. Tests:
 (a) Berlekamp-Massey linear complexity over F_p vs n/2 (random expectation n/2 +- 1, matches a random control and a shuffled-order control of the same multiset);
 (b) P-recursive guessing (order<=4, degree<=4) with out-of-window validation (code from round-10 t3, imported unchanged);
 (c) dependence on k mod m, m in {2,3,4,5,7,8,16}: ANOVA F statistic of each sequence against 400 random-permutation null; reject at 0.001 after Bonferroni over (sequences x m) tests;
 (d) spectral: max |DFT| of exp(2 pi i d/p) over k (Z/N index) vs the same for 40 shuffles (z-score; reject at |z|>4);
 (e) low-degree representability: is d1 (and u2/y) a polynomial of total degree <= D in (x,y) on the whole orbit? Linear solve mod p with D = 4,8,12, held-out validation; positive control: target x^3+y*x (found), negative control random.
Positive controls for BM/holonomic: c*k+d (L=2) and k*g^k. All must fire or the test is void.
Kill criteria for the section idea: all of (a)-(e) null at all sizes (expected).
T2b (multi-lift, the combined idea candidate, defined after seeing T1/T2): see section "Idea 3" appended (additions below are dated and marked post-hoc if added after results).

## Seeds / limits
Instance seeds: T1 2111; T2 11, 12; null permutations seeded 5. No run > 5 min; no web claims used as evidence.

## AMENDMENT 1 (written after a 60 s pilot at n=5,6 on throwaway seed 99 — pilot excluded; BEFORE any registered run)
Pilot: Glucose4 did not finish n=5 or n=6 ladder instances in 60 s / ~1e6 conflicts (22.7k vars, 74k clauses at n=5); CaDiCaL solved n=5 in 9 s, n=6 in 45 s.
Changes: (i) per-run cap 120 s (not 240 s) so the whole battery fits the session budget; (ii) ladder run for n=5..8 (3 instances each: instances_run.jsonl = rows of instances.jsonl with n<=8; shortened further for time) with the pre-stated skip rule: if all 3 instances of an n are censored for a solver, larger n are not run for that solver (and the fit uses only run instances; non-run n are reported as "not run", never imputed);
(iii) ADDED comparator: the round-10 affine Weierstrass encoding (imported unchanged from round10-frontier-b/sat_ecdlp.py) run through the identical harness/solvers/limits on fresh instances (sat_affine_cmp.py, seed 2112, n=5..10, 3 each, glucose4 / cadical195 / cms+xor), so encodings are compared on equal footing. Decision rule unchanged: promising only if upper CI of the exponent < 0.5 with <20% censoring. With so few sizes (<=6) and censoring the fit is descriptive; a verdict of "inconclusive" is allowed and is NOT evidence of promise.
