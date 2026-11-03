# Round 15 inventor F — pre-registered protocol (RUN-7f3d67ad-cb78-49f0-a4ac-b85cab28116e)

Written and hashed BEFORE any benchmark run. Code (f_lib.py, f1_supply.py, f1b_kernel.py, f2_run.py, f3_groebner.py) is drafted;
only a 16-bit correctness smoke test (t_smoke.py: every emitted decomposition re-verified with the group law; one end-to-end solve) was run.

## Question
m=3 (S_4) index calculus on prime-field, prime-order curves, factor base of size s ~ p^{1/3}. (T1) relation-supply constant; (T2) best finder
cost as a function of p on structured bases; (T3) is there a total cost below sqrt(r)?

## Heuristic model fixed in advance (N ~ r = group order)
- closed quadruples sum eps_i u_i = 0 among 4 distinct base points: N4 = 8*C(s,4)/r ~ s^4/(3r)  (8 sign classes up to global sign)
- decompositions of a fixed target T = eps1 u1+eps2 u2+eps3 u3: 8*C(s,3)/r ~ 4 s^3/(3r) distinct per target (found 3x each by the 2+1 finder)
- generic bounds: s >= (3r)^{1/3}~1.44 r^{1/3} for N4 >= s; hash finder with pair table (s^2/2 paired additions) and s paired additions
  per target: per relation 3r/(4 s^2); total = s^2/2 + 3r/(4 s) + LA. With LA = 4 s^2 mults (Wiedemann model, 4 nonzeros/row) charged /10:
  optimum s = 0.75 r^{1/3}, total ~1.5 r^{2/3}.  Partial table of size M: cost M + r s/M, min 2 sqrt(r s) = r^{2/3} at s=r^{1/3}.

## Experiments
E1 supply (f1_supply.py BITS SEED): bits in {18,21,24,27}, seeds 1,2,3; prime-order instances with d = round(5 p^{1/3}) (even) | p-1; bases of EQUAL
 size s=|coset|: COS (mu_d coset), RND, SX (smallest x), PHI2, PHI3 (random monic degree 2/3 polynomial on t=0,1,2,..), POW3 (g t^3, t=1,2,..).
 Statistic: ratio = N4_obs / (8 C(s,4)/r) via disjoint pair-sum collisions (N4 = collisions/3).
E1b kernel cosets (f1b_kernel.py BITS ELL SEED): bits 20 and 24, ell=5, seeds 1,2,3: composite-order curves with rational ell-torsion (NOT prime order), base {x(P_i + jK)}.
 Statistic: raw ratio to 8 C(s,4)/N; and distinct coset-quadruples (should be ~ N4/ell^3 if every closure lifts ell^3 times, i.e. no independent information).
E2 end-to-end (f2_run.py BITS SEED BASE): BASE=COS with d = round(1.6 p^{1/3}) (s ~ 0.8 p^{1/3}); bits 16,18,20,22,24,26,28,30, seeds 1,2,3 (24 instances);
 controls RND and SX of equal size at bits 20,24,28, seeds 1,2. Same instances for rho_dp (round 12, counted additions incl. setup) on COS runs.
 Units: addition-equivalents: pair-table paired additions (1 each) + finder paired additions (s per target) + target-walk additions
 + (FB mults + LA mults)/10, LA headline = Wiedemann model 4 s^2 (candidate-favourable; measured dense elimination mults also reported); a paired addition
 (x(P+Q),x(P-Q) sharing one inversion) is charged ONE addition (candidate-favourable). Wall time never used.
 Baseline: analytic sqrt(pi r/2) (rho walk) and measured rho_dp counts.
E3 Groebner (f3_groebner.py D SEED): sympy grevlex over GF(p) of {S_4(x1,x2,x3,xT)=0, x_i^D = c}, p ~ D^3, target a true sum of 3 base points; D in {4,6,8,10,12,16,...} as far as 280 s
 per command allows; compared with brute enumeration s^3 of the same solution set.

## Fit and decision rule (mechanical)
OLS of log2(total_model) on log2(r) over all COS instances, 95% CI (Student t). WINS iff success 100% AND alpha_hi95 < 0.5 AND geometric-mean total/rho_analytic < 1 at bits 30.
CONSTANT-ONLY if the ratio < 1 at some size but the exponent criterion fails; NO-ADVANTAGE otherwise. Toy advantage is never an asymptotic claim.

## Pre-registered predictions
1. E1: ratio in [0.85, 1.15] pooled over sizes for every base (structured bases give no excess closure); exceptions would be reported as findings.
2. E1b: raw ratio in [0.85,1.15] with N = #E; distinct coset-quadruples ~ N4/125 (lifts), i.e. all kernel-coset closure is shifted copies of quotient relations (known kernel logs).
3. E2: 100% success; alpha(model) in [0.60, 0.72] (theory 2/3); total/r^{2/3} roughly constant in 1.0-3.0; total/rho_analytic grows ~ r^{1/6}, i.e. ~ 15-60 at 30 bits; NO-ADVANTAGE.
   Per-relation finder additions ~ 3r/(4 s^2) ~ r^{1/3} >> r^{1/6}.  Controls RND/SX within 20% of COS.
4. E3: sympy Groebner time grows at least ~D^3 and is never below brute-force enumeration cost s^3 in the measured range.
5. Dense linear algebra alone (4 s^2 model) exceeds sqrt(r) for every r > ~2^10 once s >= (3r)^{1/3}: stated analytically.
