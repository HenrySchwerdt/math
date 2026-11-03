# Round 16 inventor G — pre-registered protocol (RUN-a4b19f9f-a083-4fc6-8134-a325a2660537)

Written and hashed BEFORE any benchmark run. Only 12-14-bit smoke tests of g1_coord.py, g2_lattice.py, g3_search.py (crash/consistency checks) were run before this file.
Libraries reused unedited: round13 `d2lib.is_prime`. New code: g_lib.py, g1_coord.py, g2_lattice.py, g3_search.py (this directory).

## Question
Is there an efficiently describable AND log-free testable set V in E(F_p) (prime order N, p = 3 mod 4) whose closure ratio rho = observed/predicted
(predicted for a uniformly random s-subset) GROWS with p? Only growth beats the supply bound s >= (3r)^{1/3} (m=3) / 1.22 sqrt(p) (m=2).

## Statistics (all on the same set V, s ~ 1.5 sqrt(p) unless stated)
 tri  = #{(u,v) ordered, u != v, u+v != O, u+v in V};  pred s(s-1)(s-2)/(N-2)           [m=2 closed relations]
 quad = #{ {u,v} != {w,t} unordered pairs with u+v = w+t };  pred C(M,2)/(N-1), M=C(s,2)  [m=3 closed 4-relations u+v-w-t=0]
 cov  = |V+V|/N  vs random 1-exp(-M/N)                                                    [fraction of targets decomposable with m=2]
Lattice (E2) additionally splits tri = trivial (coefficient vectors add in Z^d) + nontrivial (wrap-around mod N; only these can carry information).

## Experiments
E1 coordinate families (g1_coord.py BITS SEED REPS): families rand(control), xwin (x-interval), ywin (ybar=min(y,p-y) interval), box (joint x-interval x ybar-window),
 lowbits (joint bit pattern of x and ybar), popcount (low joint Hamming weight), xyl (window of a random integer form alpha x + beta y, symmetrised),
 xap (x in a random arithmetic progression of F_p), xy (window of x*y), ordmin (local minima of ybar along x-order, x-window of them), ordgap (x with largest successor gaps).
 bits 14,16,18,20,22 x seeds 1,2,3 x REPS=3 (main); bits 14,16 x seeds 1,2 x REPS=40 (best-of-many-descriptions check).
E2 lattice images (g2_lattice.py BITS D BFAC NK SEED): V = {sum a_i G_i, |a_i|<=B}, B = round(BFAC N^{1/2d}); d=2 (BFAC 0.5, 1.0), d=3 (BFAC 0.5); bits 14,16,18,20 (22 if time);
 NK random generator-log choices per curve (NK=40, seed 1,2).
E3 local search (g3_search.py BITS SEED ITERS): annealed hill-climb of T3 in log space, s = 2 sqrt(N), bits 10,12,14,16, seeds 1,2,3, ITERS=30000; compare with the AP baseline {1..s},
 AP-ness of the found set (smallest cyclic arc holding 90% of d^{-1}V for the 5 most frequent differences d, divided by s; random baseline reported) and coordinate uniformity (KS of x and ybar).

## Decision rules (mechanical)
GROWTH(candidate) iff, for the per-size mean of log2(rho) at >= 4 sizes, the OLS slope vs bits has 95% CI (Student t) lower bound > 0 AND rho at the largest size >= 2.
USABLE iff all of: U1 membership of an arbitrary point decidable in poly(log p) from its coordinates alone (no log, no O(s) table), U2 nontrivial (wrap-around) closure ratio
 > 1.5 at largest size and not decreasing, U3 cov >= 0.5 * cov_random (the m=2 target decomposition rate does not collapse).
A candidate is PROTOTYPED end-to-end against rho only if GROWTH and USABLE; otherwise the exact obstacle is reported and nothing is claimed.

## Pre-registered predictions
1. E1: every coordinate family has pooled rho_tri and rho_quad within [0.9,1.1] at each size (relative to the random control, to remove the finite-N offset of the quad prediction); no GROWTH;
   best-of-40 descriptions max rho_tri <= 1 + 4/sqrt(pred) (Poisson-ish extreme value).
2. E2: total tri ratio is huge and grows like N/s (GROWTH yes) but is ~100% trivial; nontrivial ratio averaged over k ~ 1 (heavy-tailed: zero for most k, large for rare k with a short
   kernel-lattice vector); cov ~ box_sums/N << cov_random (fails U3); membership needs a 2-D DLP (fails U1). Verdict: not usable.
3. E3: found sets have rho_final >= AP baseline, growing with N; they are AP-like (arc/s ~ 1-3 vs random >> 10), coordinates uniform (KS within 2x expectation); the description (d, start) is a log.
4. No candidate prototyped; the exact obstacle is an energy-versus-coverage and trivial-versus-wrap-around decomposition (see report).
