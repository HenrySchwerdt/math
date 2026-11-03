# PROTOCOL — RUN-ddba8952 (round 21, tournament explorer B)

Pre-registered before any measurement. Toy curves only. Hash of this file in PROTOCOL.sha256; later changes only in PROTOCOL_ADDENDUM.md.
Only pilot allowed before freeze: a tiny-curve (p<=31) correctness check of the Miller evaluator (output discarded, listed in `check_miller.py`).

## Curves
Prime-order curves y^2=x^3+ax+b over F_p, p ~ 2^12..2^13.6, #E = r prime, p = 1 mod 6 (so characters of order 2 and 3 exist on F_p^*), gcd(r,p-1)=1
(automatic). Deterministic search seeds 0..: first 4 curves meeting the conditions per size class (p in [4096,6000), [6000,9000)). P = first
point found (a generator since r prime). Frozen by the seed rule in `common.py`.

## Experiment A (idea I1, Riemann-Roch L(D) supply law) -- `expA_supply.py`
Claim to test: for D = sum of d base points (multiplicity allowed), the number of projective functions f in L(D - O-balanced)... precisely, the number of
effective Z of degree d with Z ~ D and Z supported in base B equals the number of ordered pairs of d-multisets of B with equal group sum. Prediction
(birthday/supply law, independent of RR): #unordered pairs of distinct d-multisets with equal sum ~ C(M_d,2)/r, M_d = C(s+d-1,d). Measured by exact
enumeration with discrete logs from full enumeration of E(F_p). Random base B of size s (seeds fixed), d in {2,3}, s in {40,80,160} (d=2), {12,24,40} (d=3),
4 curves, 5 base draws each. Statistic: observed/predicted; pass-of-law iff mean ratio in [0.9,1.1] with sd/sqrt(n) CI. Any ratio materially >1 would indicate
excess supply from the L(D) formulation and trigger a follow-up; ratio ~1 kills I1 and I2 (supply law is the group-theoretic collision count).

## Experiment B (idea I4, unreduced-Tate cocycle into F_p^*) -- `expB_tate.py`
Object: Phi(R) = f_{r,P}(R) in F_p^*, f_{r,P} the NORMALISED Miller function (div = r(P)-r(O), leading coefficient 1 in t=x/y at O), R in E(F_p)\{O,P}, evaluated
by the full O(r) product with dual-number regularisation of the 0/0 factors (every R is a multiple of P). Because gcd(r,p-1)=1, Phi is not an r-th power residue
invariant: all information is in the full element. Sequence for the DLP: for Q = kP the solver can compute Phi(Q) in O(log r); the unknown enters through
Phi(kP) = (explicit cocycle product). Leak statistics on s_k = chi_l(Phi(kP)), l in {2,3} (l-th power residue symbol, values in mu_l), k = 1..r-1 excluding k=1 and
the measure-zero set where a line is tangent (reported count):
  B0 correctness: tiny-curve brute-force check of Phi against linear-algebra f_{r,P} (check_miller.py) must pass; else experiment B void.
  B1 balance: z-score of the counts of each value of s_k (|z|>4 flags).
  B2 spectrum: M = max_a |sum_k s_k e(ka/r)| (a=1..r-1) vs the iid-null 99% threshold computed by Monte-Carlo (200 draws of iid uniform mu_l sequences, same r).
  B3 residue dependence: chi-square of contingency (s_k, k mod m), m=2..16; Bonferroni alpha=0.01/15.
  B4 arithmetic structure of k: z-score of correlation of s_k with Liouville lambda(k), with indicator[k is r^{1/3}-smooth] and with k mod 2.
  B5 predictor advantage: best single-feature predictor of [k>r/2] from (s_k, y-sign chi, x of kP parity) via train/test halves on k (accuracy-1/2 with 99% Wilson
     half-width). Decision bar: advantage must exceed the leakage bar C r^{-1/4} with C = 2 (alpha-sqrt(r) control below) to matter.
  B6 planted control: replace s_k by s_k XOR bernoulli(0.45)-style leak on [k>r/2] (advantage 0.05); pipeline B5 must flag it, else null is void.
Pass for idea: any of B1..B5 rejects (Bonferroni 0.01 across all tests) on >=3 of 4 curves AND the effect replicates on the other seeds, AND B5 beats the bar.
Otherwise I4 is recorded as killed (null) at these sizes.

## Rho control (calibration of the cost model, same implementation) -- `rho_control.py`
Pollard rho (r-adding walk, 16 branches, Floyd cycle, restarts) on `toyec.Curve`, counting group additions; 200 random Q per r for r in the I4 curves plus 4 extra
sizes; fit cost = alpha*sqrt(r)+gamma by least squares, report alpha, gamma, R^2. No candidate algorithm exists for I4 (distinguisher only), so the control gives the
break-even leakage bar: advantage eps needed ~ alpha-based C r^{-1/4}, reported as eps_bar(r) = 2*alpha_hat*... (formula in code: eps_bar = sqrt(alpha_hat/ ... ) is
NOT used; we report the round-20 bar C r^{-1/4}, C=2, for reference only).

## Not tested, paper kills only
I2 (weighted coefficients), I3 (torsion lift), I5 (elliptic-surface MW lattice), I6 (multiplicative labels / smoothness), I7 (Heegner/ring structure), I8 (EDS scaling)
are killed on paper against the obstruction map in the report; no numerical claim is made for them except the B4 smoothness probe which touches I6.
