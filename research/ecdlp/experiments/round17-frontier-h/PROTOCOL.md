# PROTOCOL — Round 17 / frontier H: DLP-procedure search with field arithmetic, scored against a same-DSL rho control
(RUN-885e31b9-573a-4763-a71c-f0d533ac14c2). Pre-registered before any evolutionary search. Toy curves only
(prime order r, 2^10 <= r <= 2^20, prime field, y^2 = x^3 + ax + b).

## Lessons from round 16 that this protocol applies
1. Naive log-log exponents at r <= 2^16 are biased low by setup cost (frontier G: the "exponent 0.33-0.38" of a champion was
   setup amortisation; its cost fit 1.78 sqrt(r)+139 equals hand rho). Therefore NO log-log exponent is used as evidence.
   Evidence is (a) cost ratio to a same-DSL rho control on identical instances and (b) an out-of-sample extrapolation of the
   model cost = alpha*sqrt(r) + gamma.
2. DSL extended with F_p arithmetic (dsl2.py): FCTR/FCONST/FADD/FMUL/FINV/FSQRT/FRHS/FLEG/FRAND/FX, S_3 root (FS3) and
   evaluation (FS3EV), LIFT of a field element to a point (new "factor-base generator" with hidden log), IFOK/IFSMALL
   predicates, RELATE (records A +- B +- C = 0 when S_3 holds; signs read off y in a real implementation), MSOLVE (Gaussian
   elimination mod r on <= 400 relation rows over <= 255 generators). Plus all 19 round-16 generic ops. Cost unit = 1 group op;
   field mult = 1/12, inversion = 1, sqrt/Legendre = 0.125*lg p, FS3 = 0.125*lg p + 0.6, LIFT = 0.125*lg p + 0.25, RELATE 0.5,
   MSOLVE = rows*cols*min(rows,cols)/12 (+ verification 1.5*lg r per candidate k). Run cap 12*sqrt(r); failure counts as cap.
   Changes vs round 16 (declared): points carry coefficients on lifted generators; LOOK/SOLVE act on full-x equality of the
   stored/queried points (as a real hash table with full keys) instead of charging verification for partial-key false hits;
   the relation sign is read from the hidden log (equivalent to comparing y). The same VM runs candidates and controls.
3. Fast curves: curves.py (numpy point counting, table build 3.4 s at 2^20). Curve (tb, seed) deterministic; tables cached.

## Data splits (all curve seeds are new; none used in round 16)
- TRAIN: tb in {10,11,12}, seeds {500,501}; instances resampled each generation (4 per curve).
- VALIDATION (hall-of-fame champion selection only): tb in {10,11,12}, seeds {550,551}, 10 instances/curve.
- FIT sizes (used only to fit the cost model at evaluation): tb in {13,14,15,16}, seeds {600,601,602}, 40 instances/curve.
- HELD-OUT sizes: tb in {17,18,19,20}, seeds {700,701,702}, 40 instances/curve (120 per size), never used by the search.
- Every program (candidates and controls) gets the same (k, seed) instances.

## Search
Evolutionary as in round 16 (population 100, tournament 3, elites 6, 30% crossover, 4 runs): tags r0, r1 random initial
populations (seeds 0,1); s2, s3 seeded (seeds 2,3; initial population contains hand rho_dp, BSGS, index-calculus-with-MSOLVE
(prog_ic_ms) and rho_floyd + 16 mutants) - seeded runs are secondary but evaluated with the same criteria. Generations: up to 120
or 5 time slices of 240 s, whichever first (a run that stops early is reported as such). Fitness (minimised) = mean over training sizes
of cost / (mean cost of hand rho_dp on the same curve, 40 fixed instances) + 1.0*(ratio at 2^12 - ratio at 2^10) + 0.003*length;
unsolved instances count cap cost with shaping credit (0.3 * min(1, relations/5)). I.e. fitness is a ratio to the rho control and
rewards a ratio that falls with size; no log-log exponent. Champion per run = best validation fitness in its hall of fame (top 3/gen).

## Success rule (fixed; a champion "counts" as a sub-sqrt(r) candidate only if ALL hold on the HELD-OUT sizes)
T1: success rate >= 0.9 at every size 13..20.
T2: slope of ln(mean cost_cand / mean cost_rho_dp) against log2 r over sizes 17..20 has a 99% bootstrap upper bound < 0.
T3: for each program fit cost = alpha*sqrt(r)+gamma by OLS on the FIT-size means (13..16) and predict the 2^20 mean cost;
    Q = (observed/predicted)_candidate / (observed/predicted)_rho_dp at 2^20 has 99% bootstrap upper bound < 1.
    (Joint bootstrap, 2000 resamples of instance indices in every size stratum, shared by candidate and control, seed 12345; the
    fit is redone in each resample.) Q also reported for 2^17..2^19.
T4: mean cost at 2^20 is below that of hand rho_dp (a falling ratio that stays above rho is not a speedup).
Controls evaluated with the same code: rho_dp (the reference), rho_dp variants (nb 3; dpbits 3), rho_floyd, BSGS, and the
hand index-calculus program with MSOLVE (prog_ic_ms) under the same 12*sqrt(r) cap. Calibration: a control that is Theta(sqrt r)
by construction (rho variants, BSGS) must NOT satisfy T1-T4; if one does, the criterion is declared non-discriminating.
Honest-negative rule: if no champion passes T1-T4, the outcome is "no sub-sqrt candidate"; constants (c/sqrt r) are reported but are
not evidence of a better exponent. 99% CIs because up to 4 champions + controls are tested (multiplicity not otherwise corrected).
Separate scaling record (not part of the success rule): prog_ic_ms with a 400*sqrt(r) cap at sizes 10-14, to document how an
index-calculus-style decomposition scales in this model.

## Disclosure
Before this file was hashed I ran only DSL smoke tests (dsl2.py main, curves.py main, one fitness evaluation of three hand
programs, one timing of 20 random programs) on training/baseline curves (seed 5, 500, 501). No held-out curve or champion was touched.
Expectation stated in advance (not a result): negative; search rediscovers rho/BSGS-like collision programs; index calculus is
expressible but costs ~p/|FB| decompositions per relation so it will not fit under the cap at these sizes.
