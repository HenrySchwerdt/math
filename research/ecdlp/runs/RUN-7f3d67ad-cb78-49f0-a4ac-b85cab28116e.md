# RUN-7f3d67ad — Round 15 / algorithm inventor F: m=3 (S_4) index calculus, supply and finder cost

Role: algorithm-inventor. Model: configured claude-sonnet-5-5 (self-reported, not runtime-verified). No commits. Same-provider self-review only (no independent review).
Code, data, protocol: `research/ecdlp/experiments/round15-inventor-f/` (`PROTOCOL.md` sha256 `10c14b98512616d777ce4d7c66f14357ee5cacbfe9edd56c30d2a40eecfb340d`, written and hashed before any benchmark; `sha256sum -c PROTOCOL.sha256` OK; `SHA256SUMS` covers code and outputs). Round-13 `d2lib.py` and round-12 `common.py` are imported unedited.
**Headline: NEGATIVE.** m=3 has a supply floor s >= (3r)^{1/3} (measured constant 1.00 +- 0.02 on six base families, structured or not) and the best finder I could build, a hash finder on the 2+1 split, solves every instance (24/24) at total cost ~1.5 r^{2/3} (fitted exponent 0.651 [0.642, 0.661]), 8.6x rho at 16 bits growing to 36x at 30 bits (ratio exponent 0.151, theory 1/6). One per-relation finder cost is ~r^{1/3}, not the required < r^{1/6}. Independently of any finder, sparse linear algebra on s >= (3r)^{1/3} unknowns already costs ~4 s^2 > sqrt(r). No candidate with total cost below sqrt(r) exists, so no speedup is claimed. PROTOCOL decision rule (mechanical): NO-ADVANTAGE.

## 1. Question, inputs, sources
Question as assigned: for m=3 (target = sum of 3 factor-base points, relation polynomial S_4), (1) re-derive and measure the supply constant, (2) measure the cost of finding existing S_4 decompositions as a function of p on structured bases (multiplicative coset, x = phi(t), kernel cosets), (3) give the exact obstacle or a candidate with total cost < sqrt(r).
Read in this session: docs/roles/algorithm-inventor.md; STATUS.md rounds 13-14; reports RUN-22ed50a6 (D) and RUN-b5e8c157 (E) in full; D's `d2lib.py`, `run_d2.py`, `PROTOCOL.md`; E's `e3_supply.py`; round6-rel PROTOCOL.md and `out_summary.txt` (the earlier ECDLP-16 m=3 table-finder study); hypotheses HYP-32e353ac, HYP-db508348, HYP-3c665e7b.
**External sources: none retrieved by me.** Everything I use about PKM (Petit-Kosters-Messeng 2016), Semaev 2004, Diem, Gaudry is second-hand through D's and E's reports (PKM cost formula P + m! p/(deg L)^{m-1} T + (deg L)^omega; D read PKM in full, E did not). Nothing below depends on those papers beyond the "required T < p^{1/2-1/m}" accounting as quoted by D.

## 2. Item 1 — mechanism, and the exact m=3 accounting
Setting: E(F_p) of prime order r ~ p, base V of s points (x-set, one y each, negation-closed), unknown logs l_i. A relation is a signed sum. Two kinds:
- target relation T = aP+bQ = e1 u1 + e2 u2 + e3 u3 (gives a + b k = sum e_i l_i); 8 C(s,3)/r ~ 4 s^3/(3r) distinct decompositions per random T;
- closed relation e1 u1 + ... + e4 u4 = 0 among base points (S_4(x1..x4)=0); 8 C(s,4)/r ~ s^4/(3r) distinct 4-sets (8 sign classes mod global sign, each hit with probability 1/r). By the 2+2 split each appears as exactly 3 disjoint collisions x(u_a +- u_b) = x(u_c +- u_d) in the pair-sum table, so N4 = collisions/3.
Supply: need s-1 independent relations among s unknowns. Closed relations alone: s^4/(3r) >= s gives s >= (3r)^{1/3} = 1.44 r^{1/3} (E's m=2 constant 1.22 sqrt(r) came the same way).
Finder family measured: 2+1 split with a hash table of all pair sums (s^2/2 paired additions, built once) and s paired additions T -+ u_i per target. Per target yield 4 s^3/(3r) (found 3x each, deduplicated), per relation cost 3r/(4 s^2). With a partial table of M pair sums the cost is M + r s/M, minimum 2 sqrt(r s) = 2 r^{2/3} at s = r^{1/3} (analytic; same exponent as inventor A's birthday-join measurement of sqrt(p s)). Total: s^2/2 + 3r/(4s) + LA, optimum s ~ 0.75 r^{1/3}, total ~ 1.5 r^{2/3}.
Structured bases tried (T2): PKM multiplicative coset g mu_d, d | p-1 (d need not be a power of 2 for the hash finder), smallest-x, x = phi(t) with phi a random monic polynomial of degree 2 or 3 on t = 0,1,2,..., x = g t^3 on t = 1,2,..., random x (control), kernel cosets {x(P_i + jK)}.

## 3. Item 2 — pseudocode / prototype
`f_lib.py` (`Finder3`, `solve_k`), `f2_run.py`.
```
inst:  p prime, d | p-1, d ~ 1.6 p^{1/3}; E: y^2=x^3+ax+b with #E = r prime (BSGS), P, Q = kP
FB:    V = {g zeta^i : x^3+ax+b square}, one y each         (s ~ 0.8 p^{1/3})
table: for i<=j, sg=+-1: z = x(u_i + sg u_j); sort                        # s^2/2 paired additions
loop:  T = aP+bQ by a 32-entry branching walk                             # 1 addition per new target
       for sg=+-1: W = T - sg u_i  (all i, vectorised, s paired additions); look up x(W) in table
         hit (i,j,sj): resolve sign of W vs u_i + sj u_j with the group law; relation
         a + b k = eps*l_i + eps*sj*l_j + sg*l_i   (rows deduplicated by coefficient set)
       incremental sparse-aware elimination mod r over columns (l_1..l_s, k, rhs); stop when a pivot row contains only k
output: k, verified kP = Q
```
Closed-quadruple counter (supply): sort the pair-sum table, count equal x between pairs with 4 distinct indices.

## 4. Item 3 — correctness
Each emitted decomposition is re-verified with the group law (`t_smoke.py`, evidence 213aa0d3: 633 decompositions, bad = 0, plus one end-to-end solve). The pair-table/closed-quadruple counter agrees with the heuristic count to 0.2% pooled (below). End-to-end: k recovered and kP = Q checked on 24/24 COS instances (16-30 bits) and 12/12 control instances; rho_dp recovered 24/24 on the same instances. A relation is a true group identity; the algorithm fails only by running out of relations (it continues). Probability of success 1 up to termination (no failure observed).

## 5. Item 4 — complexity model
s = |V|, units = point additions (a paired addition giving x(P+Q) and x(P-Q) with one inversion is charged ONE, which favours the candidate).
- Preprocessing: s^2/2 additions for the pair table (memory s^2 words), d sqrt-extractions for the base (~2 d log2 p mults).
- Per relation: finder additions ~ 3r/(4 s^2) (measured per relation incl. dedup: 37 at 16 bits to 920 at 30 bits, exponent ~0.33 = r^{1/3}; required < r^{1/6} = 6.1 ... 30.7).
- Relations needed ~ s + O(1) (measured 34 for s=33 ... 759 for s=816).
- Linear algebra: rows have <= 4 nonzeros over F_r. Dense incremental elimination measured; the headline uses the candidate-favourable Wiedemann-type model 4 s^2 mults (/10 per addition-equivalent). No subquadratic algorithm for random sparse systems of this shape is known to me (not a proved lower bound; not searched in the literature this session).
- Total ~ 0.5 s^2 + 0.75 r/s + 0.4 s^2 -> 1.5 r^{2/3}. Measured total / r^{2/3} = 1.75 (16 bits) ... 1.48 (30 bits).
- Memory s^2 ~ 0.6 r^{2/3} words (partial table trades memory for the same exponent).
- Success probability: 100% in 36/36 runs.

## 6. Item 5 — measured scaling vs rho (E2, `analysis.txt`; geometric means over 3 seeds; 8 sizes, 24 COS instances)
| bits | s (avg) | s/p^{1/3} | targets | relations | finder adds/relation | p^{1/6} | total (model) | total/r^{2/3} | rho analytic sqrt(pi r/2) | ratio | rho_dp measured |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16 | 33 | 0.87 | 38 | 34 | 37 | 6.1 | 2.48e3 | 1.75 | 290 | 8.6 | 2.7e3 |
| 20 | 81 | 0.84 | 97 | 75 | 106 | 9.8 | 1.46e4 | 1.58 | 1.18e3 | 12.4 | 4.2e3 |
| 24 | 205 | 0.82 | 263 | 187 | 285 | 15.8 | 9.36e4 | 1.50 | 4.95e3 | 18.9 | 9.8e3 |
| 28 | 517 | 0.85 | 564 | 477 | 610 | 24.7 | 5.39e5 | 1.45 | 1.88e4 | 28.6 | 2.8e4 |
| 30 | 816 | 0.87 | 855 | 759 | 920 | 30.7 | 1.31e6 | 1.48 | 3.62e4 | 36.2 | 4.9e4 |
(rows 18, 22, 26 in `analysis.txt`.) Fits (log2 total vs log2 r, 95% CI, n = 24): model total alpha = 0.651 [0.642, 0.661]; measured dense-elimination total 0.651 [0.641, 0.661]; finder-only 0.663 [0.653, 0.673]; rho analytic 0.5 (exact by construction); measured rho_dp 0.287 [0.222, 0.353] (setup-dominated at small r, as noted in rounds 12-13); ratio to analytic rho exponent 0.151 [0.142, 0.161] vs theory 1/6.
Controls (same size, 2 seeds, bits 20/24/28): random-x and smallest-x bases give total within 0.91-1.06 of the coset base, all correct.
Decision rule (PROTOCOL): success 100%, alpha_hi95 = 0.661 > 0.5, ratio 36.2 > 1 at 30 bits -> NO-ADVANTAGE. Predictions 3 (alpha in [0.60,0.72], total/r^{2/3} in 1-3, ratio 15-60 at 30 bits (36.2), controls within 20%) held.

### Supply (E1, T1/T2)
Ratio N4_obs / (8 C(s,4)/r), s = 2.5 p^{1/3}, bits 18/21/24/27, 3 seeds each (12 per base; `out_supply_*.jsonl`):
| base | pooled ratio | per-bits (18,21,24,27) | min / max single |
|---|---|---|---|
| COS (coset) | 0.999 | 0.975, 0.989, 1.001, 1.006 | 0.96 / 1.01 |
| RND | 1.005 | 0.982, 0.997, 1.006, 1.011 | 0.95 / 1.04 |
| SX (small x) | 1.005 | 1.008, 0.998, 1.011, 1.003 | 0.98 / 1.04 |
| PHI2 (random quadratic, interval) | 1.002 | 1.005, 0.999, 1.016, 0.993 | 0.97 / 1.03 |
| PHI3 (random cubic, interval) | 1.001 | 0.996, 1.000, 1.003, 1.002 | 0.97 / 1.04 |
| POW3 (g t^3, interval) | 0.991 | 1.013, 1.000, 0.974, 0.995 | 0.97 / 1.04 |
So the supply constant is s^4/(3r) (8 C(s,4)/r) with no excess closure for ANY of the structured bases (prediction 1 held). Combined with the end-to-end yield (4 s^3/(3r) per target), the constants are not just orders of magnitude: they predict the end-to-end 1.5 r^{2/3} to within a few percent.
Kernel cosets (E1b, ell = 5, composite-order curves with a rational 5-torsion point, NOT the prime-order setting; 6 curves at 20/24 bits). Pre-registered prediction 2 as written (raw ratio ~1) FAILED: raw closed quadruples are 40-114x the generic count, because V contains full cosets P_i + <K> and u_{i,a} - u_{i,b} = u_{i',c} - u_{i',d} = (a-b)K is a trivial identity with known logs. The post-hoc refinement (new field `raw_N4_four_distinct_cosets`, `out_kernel_v2_posthoc.jsonl`, labelled post-hoc) restricts to quadruples on 4 distinct cosets: 1125, 1000, 1375, 3375, 2125, 3875 observed vs 1218, 1316, 1060, 2861, 2726, 3080 predicted by 8 C(s,4)/N (pooled 1.05); every count is a multiple of 125 = ell^3 and equals ell^3 times the number of closed quadruples of the quotient base (9, 8, 11, 27, 17, 31 observed vs 8.8, 9.6, 7.5, 21.9, 20.8, 23.6 predicted by the quotient count 8 C(n,4)/(N/ell)). Hence kernel-coset closure = trivial known-log identities + lifts (ell^3 shifted copies) of the quotient relations: no independent information beyond the quotient. For a prime-order group there is no rational kernel at all (a rational isogeny of degree != r is an isomorphism on F_p-points, E's lemma HYP-caa15771), so the construction is empty exactly where ECDLP lives; where it exists it is Pohlig-Hellman.

### Gröbner (E3, task 2 finder candidates)
sympy grevlex over GF(p) of {S_4(x1,x2,x3,xT)=0, x_i^D = c}, p ~ D^3, target a true sum of 3 base points (`out_gb2_*.jsonl`): D = 6 (s = 4, p = 229): 29.3 s; D = 8 (s = 4, p = 1049): 216 s; D = 10, 12: timeout at 250 s. The GB's solution count was not compared in the timeouts; for D = 6, 8 the brute-force enumeration (s^3 = 64 evaluations) found 6 ordered solutions (the GB itself only returned a basis of 3 polynomials of degree <= 3, I did not extract its solution set; so the check "GB solution set = enumeration" was NOT done here, unlike D's m=2 check). Time grew 7.4x for D 6 -> 8, worse than D's m=2 d^3 trend, and is >10^6 times the wall time of the 64-evaluation enumeration. Earlier launches (`out_gb_a/b.jsonl`) crashed because s < 3 at D = 4 etc.; fixed (base resampled until s >= 4); superseded. Sage/Magma/Singular unavailable; sympy is far weaker than Magma, so this says nothing about Gröbner asymptotics, only that it is no candidate here. The analytic reason it cannot win: the system has one degree-4-in-each-variable equation plus three degree-D equations; its variety has ~ D^3/r solutions in a space of 4 D^3 candidates, and elimination yields univariate polynomials of degree Theta(D) per fixed variable, i.e. enumeration with larger constants (round 6 M3, D's F2).
Resultants: not implemented separately (same solution set as the 2+1 enumeration; per x1 elimination leaves degree ~4D in x2, cost Otilde(D) per (target, x1) = D^2 per target, worse than the s-per-target hash finder).

## 7. Item 6 — exact obstacle
1. Supply floor, finder-independent: closed S_4 relations in a base of size s number 8 C(s,4)/r (measured 1.00 +- 0.02, six base types, bits 18-27), so s >= (3r)^{1/3}. Structure on x (subgroup coset, polynomial image, interval, small x) gives no excess closure: x-structure is not group structure (x(P+Q) is not compatible with x -> zeta x), and the only structure compatible with the group law (kernel cosets, CM orbits per E) gives either nothing in prime order or only known-log identities.
2. Linear algebra, finder-independent: s >= (3r)^{1/3} unknowns with weight-4 rows cost ~4 s^2 mults with Wiedemann/Lanczos, ratio to sqrt(r) = 26 (r = 2^10), 84 (2^20), 845 (2^40), 8.6e4 (2^80) and growing as r^{1/6}. So even a free finder (T = 0) cannot make m=3 beat rho unless sparse solving of such systems is subquadratic (not known to me). The task's per-relation bound T < r^{1/2}/s ~ r^{1/6} omits this term; with it the requirement is unsatisfiable. (m = 4 would tie LA with rho at s = r^{1/4}; m >= 5 is required for LA < sqrt(r), as D noted.)
3. Finder: for every hash/collision finder, total >= min_s (s^2 + r/s) ~ r^{2/3} (full table) or 2 sqrt(r s) (partial table); measured per-relation cost 37 -> 920 additions across 16 -> 30 bits (r^{0.33}), against the needed r^{1/6} (6 -> 31). An algebraic finder would have to find a point on the abelian surface {u1+u2+u3 = T} (birational to E x E per E, derived there, not verified here) lying in V^3 in time below sqrt(|V|) per solution while the equation has ~1 solution among s^3 candidates: Gröbner/resultant elimination degrades to enumeration (E3) and I know no rational parametrisation compatible with a small base (E's genus table: base x = phi(t) of degree e has genus >= (3e-1)(e-1), >= 3p at s = sqrt(p); for s = p^{1/3} the genus is larger, e ~ p^{2/3}).
4. Information-theoretic remark: closed relations with KNOWN (a_i, b_i) representations (points a_i P + b_i Q) need no linear algebra: one 4-sum zero gives k directly, and the 2+2 collision search costs s^2 with s^4/(3r) >= 1, i.e. s = (3r)^{1/4}, cost ~ 1.3 sqrt(r) = a plain birthday/rho tie. Making the base elements structured in x forces their logs to be unknown, which is what creates the unknowns and the r^{2/3}.

## Limitations (honest)
Toy sizes (p < 2^31, int64 numpy; 16-30 bits), Python; scaling extrapolates 14 doublings of r. Exponent of the finder is a fit over 8 sizes x 3 seeds. Supply constants measured on 12 curves per base (3 curves x 4 sizes), exact constants for larger sizes are not proved (heuristic equidistribution; the structured families are tested, not all structure). Rho comparison: analytic walk cost plus measured rho_dp (setup-dominated). The LA headline is a model (4 s^2), measured dense elimination mults are also reported and give the same exponent; measured LA is small at these sizes so exponent is finder-dominated; at larger r the LA term (also ~ r^{2/3}) is the same order. Charging a paired addition as one addition and ignoring hash costs favours the candidate; the verdict does not change. Kernel prediction failed as pre-registered and the post-hoc refinement is labelled. Gröbner: sympy only, two completed points, two timeouts, solution-set check not performed, small s. No external papers retrieved. Not tested: m >= 4 with the same finder, CM/endomorphism bases beyond E's j = 0 analysis, GLV/automorphism constant-factor savings, projective/x-only addition counts, any subquadratic sparse solver.

## Next step
m=3 is closed in this family: supply (s >= 1.44 r^{1/3}), LA (>= 4 s^2) and finder (>= r^{2/3} for hash finders) all give exponent >= 2/3 > 1/2. Remaining levers: (i) a theory-level question whether sparse random-like linear systems over F_r with s columns can be solved in s^{2-delta} (would be a general LA result, not ECDLP-specific); (ii) a base closed under group-compatible structure that survives in prime order (none known; kernel/CM structures act as scalars); (iii) non-generic curve families (CM with large class group, isogeny distance to a structured curve). Suggested ledger update: HYP for "m=3 S_4 route: supply constant 8C(s,4)/r, LA and finder floors give total ~ 1.5 r^{2/3}; refuted as an exponent improvement", evidence = the experiment directory above.
