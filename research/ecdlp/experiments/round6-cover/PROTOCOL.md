# Round 6 / ECDLP-18 protocol (pre-registered before any execution)

Task TSK-e90f8650-8b93-4ea0-b9f1-82387f76e4c7, RUN-9e957bce-b882-4389-860f-d3b1fed7ec75,
hypothesis HYP-ad5bc0e3-30cc-4eb8-b823-4df42edd44a6. Toy synthetic curves only.
This file is hashed (PROTOCOL.sha256) before the code is written and before any run.
Any later deviation is recorded in the RUN report under "Deviations".

## Prediction under test
Cover-based index calculus on J_C(F_p) for a genus-2 double cover C -> E, E/F_p of prime order r,
costs of order >= p (not <= sqrt(p)) in counted group/field operations.

## Setup
* Master seed 20261109. Per (bits, curve index) a `random.Random` seeded with the string
  `"20261109/<bits>/<idx>"`. Prime p = largest prime below 2^bits.
* E: y^2 = f(x) = x^3+ax+b, random (a,b) until #E = r is prime (r != p), by brute-force count.
* C: y^2 = F(w) = f(w^2+c), degree 6, monic. c = smallest c >= 1 with f(c) != 0 (so F squarefree)
  and gcd(r, m) = 1, where m = #E'(F_p) is derived from #C(F_p). pi(w,y) = (w^2+c, y).
  Note (pre-registered claim, to be checked in report): since #E is odd, f has no root in F_p, hence
  F has no root in F_p, so NO imaginary (degree-5) model with a rational Weierstrass point exists for any
  such c; the degree-6 "real" model with two rational points at infinity (infty+, infty-) is used.
* Divisor classes: D - K with K = infty+ + infty-, D effective of degree 2 in Mumford form (u monic deg 2,
  v with deg<=1, v^2 = F mod u). Group law = Cantor composition (with gcd) followed by one reduction step
  u' = (F - v^2)/u, v' = -v mod u'. Classes whose representative involves a point at infinity are
  "degenerate" (probability O(1/p)) and are skipped/retried; the identity is represented by None.
  pi^*(Q) = [div(w^2-(x_Q-c), y_Q)] - K; pi^*(O) = identity.
* Index calculus modulus r. Because gcd(r, #J)=r exactly (r || #J), the map phi = multiplication-by-m then
  identification of J[r] with Z/r is a homomorphism J(F_p) -> Z/r; all relations are taken in phi-images.
  Unknowns: x_orbit = phi(g(P)), g(P)=[P - infty+], one per hyperelliptic orbit {(w,y),(w,-y)}
  (g(iota P) = -g(P) - N, N=[infty+ - infty-]), plus n = phi(N) and k (pi^*Q = k pi^*P, phi(pi^*P):=1).

## Checks (before timing runs)
1. #C(F_p) and #C(F_{p^2}) by exhaustive count; L-polynomial gives #J = L(1); require #J = r*m with
   m from the split J ~ E x E' (independent check; p^2 count only for bits <= 14 on a subset).
2. Random associativity (500 triples), commutativity, inverses, pi^* homomorphism
   pi^*(Q1)+pi^*(Q2)=pi^*(Q1+Q2), order of pi^*P divides r, and [#J]D = identity for random D.

## Algorithms
* Variant A (pullback only, exactly as the task statement): relations from alpha pi^*P + beta pi^*Q,
  random (alpha,beta), reduced to Mumford form, kept iff u splits; 3*orbits samples; report rank of the
  relation matrix vs. number of unknowns and whether k is determined.
* Variant B (standard degree-1 factor-base index calculus / Gaudry-type): trial Z = pi^*(alpha P+beta Q)
  + (P_a+P_b-K) with P_a,P_b random factor-base points (one Cantor addition per trial; (alpha,beta)
  advanced by an additive walk in E, EC additions counted separately), keep iff u(Z) splits over F_p
  (all roots in the factor base for restricted bases). Collect (#orbits + 20) relations, then sparse
  Gaussian elimination (Markowitz-style, dense numpy core) mod r; if rank < #unknowns, add 10% relations and
  repeat (all attempts counted). Solve for k.
* Variant B-half: as B with a random half of the orbits as factor base, run at bits 10 and 12 only
  (checks the reduced-factor-base cost trend). Thériault/GTTD large-prime and double-large-prime
  variants are NOT implemented; their cost is stated analytically in the report.

## Counted costs (all "ops" are abstract unit operations, not timings)
cantor = Cantor additions/doublings in J_C (setup + relations); ec = EC additions used for the walk
(and for the secret DL); la = coefficient multiplications in elimination (sparse: row-length per row update;
dense: rows*cols per pivot). total = cantor + ec + la. Wall time recorded separately.
Baseline: toyec.dlog_bsgs group additions (measured) and sqrt(r), sqrt(p), 1.2533*sqrt(r) (rho, analytic).

## Sizes and replication
bits = 8, 10, 12, 14 with 3 curves each (variant B, A on 8/10/12/14), bits = 16 with 1 curve if the run
fits in 5 minutes. Median over curves per size; exponent = least-squares slope of log(total) vs log(p)
over the median totals (also reported for cantor-only and la-only).

## Decision rule (as assigned)
HYP-ad5bc0e3's prediction is FALSIFIED iff, for a variant that recovered k correctly (equal to the secret k
and to dlog_bsgs) on all curves, the median total counted cost at the largest size is < 0.5*sqrt(p)
AND the fitted exponent is < 0.5. Otherwise it SURVIVES on the tested domain. A variant that fails to
determine k (e.g. rank-deficient Variant A) is a negative result about that variant only and neither
falsifies nor confirms the hypothesis by itself. Toy sizes: asymptotics are not established by experiment.
