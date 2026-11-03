# RUN-6fce1db8-c165-4d1e-abc5-e31a36c4d45e: Round 2 experiments (E-A approximate characters, E-B predicate independence)

Role: experimenter. Task: TSK-76b6d820-82e8-46c6-aea4-e25d7d0e95ba (ECDLP-7). Model self-report: Claude Sonnet 5.5
(claude-sonnet-5-5). Status: complete, uncommitted.

## Inputs
Hypotheses HYP-130de9b1-6713-4602-b1e5-6ef8a7da8486 (E-A: no low-complexity coordinate function on a prime-order subgroup is a
near-character or correlates with a character) and HYP-e1959734-9325-4a54-9d99-d4535c58a11c (E-B: Legendre/parity predicates of
coordinates of [k]P are independent of k mod m, uncorrelated in k, flat in DFT). Oracle: research/ecdlp/experiments/lib/toyec.py
(synthetic toy curves only). No other run files were read. No web lookups. Owned files: research/ecdlp/experiments/round2/*.
## Pre-registered protocol (written 2026-11-03 before any script was written or run)

Common. Oracle: `research/ecdlp/experiments/lib/toyec.py` (`Curve`, `is_prime`, `dlog_bsgs`). Synthetic toy curves
y^2 = x^3 + a x + b over F_p only. Random source: Python `random.Random` seeded per curve index with the string
"<master_seed>-<curve_index>" (deterministic, independent of process scheduling). Curve sampling: draw p, draw (a,b)
uniformly mod p, reject singular, reject #E not prime, reject anomalous (#E = p) and #E < 5. G = E(F_p) (r = #E prime),
P a uniformly random non-identity point (any such point generates). Enumeration j -> jP, j = 0..r-1, by repeated
addition; the enumeration index is the discrete log (cross-checked on 3 random points per curve against `dlog_bsgs`).
Numpy (installed) is used only for array arithmetic/FFT; p-values use stdlib `math` (own chi-square survival function
via regularized incomplete gamma, normal via erfc, own KS). Statistics code self-tested on known values.
Replication rule: each experiment is run once with master seed S1 and once with fresh master seed S2, both
pre-registered below and both reported; any positive result in S1 is only a "candidate" until S2 reproduces it.
Interpretation: finite toy-size evidence only; no statement about cryptographic sizes; no proof.

### E-A (HYP-130de9b1): approximate characters
Curves: 12 curves, p uniform on integers in [500, 5000] (prime), S1 = 20261103, S2 = 20271103.
Family F (|F| = 40): f_{(al,be,ga,de)}(O) = 0, f(x,y) = ((al*x + be*y + ga*x*y + de*x^2) mod p)/p, with
(al,be,ga,de) in {-1,0,1}^4, nonzero, up to overall sign (first nonzero coefficient = +1). This contains x/p, y/p,
(x+y)/p. Values are held as exact integers mod M (M = p) so defects are exact multiples of 1/p.
Statistics per (f, curve): (1) D(f) = max over ALL ordered pairs (a,b) in G x G (a,b = 0..r-1 incl. identity) of
||f(a+b) - f(a) - f(b)||_{R/Z}; (2) average defect over all r^2 pairs; (3) Fourier statistic
F(f) = max_{c = 1..r-1} |(1/r) sum_j e(f(jP)) e(-cj/r)| (c = 0 excluded, since a constant bias gives no DL information).
Positive controls (per curve): exact characters chi_c(jP) = c*j/r (c random in 1..r-1; M = r) -> expect D = 0, F = 1;
the same character rounded to the 1/p grid; character plus uniform noise in [-0.05,0.05]; mixtures "character with
probability w, else uniform random" for w in {0.5, 0.2, 0.1}. These are used only to show the pipeline detects characters
and to give sensitivity (the mixtures show the smallest leaked-correlation strength detectable at the threshold).
Null: random functions G -> R/Z with f(O)=0 and values uniform on the grid of 2^30 points: 10 per curve with full D
and F, plus 300 per curve with F only.
Threshold (Fourier). For a random function, r*|S_c|^2/r^2 ~ Exp(1) approximately independent over c, so
P(F > t) <= (r-1) exp(-r t^2) (union bound). Family-wise alpha = 0.01 Bonferroni over |F| x (#curves) = 40 x 12 = 480
tests gives per-test alpha' = 0.01/480 = 2.08e-5 and per-curve threshold T_F(r) = sqrt(ln((r-1)/alpha')/r).
f is "flagged (Fourier)" iff F(f) > T_F(r). Consistency check against the empirical null: none of the null draws should
exceed T_F more often than allowed (expected exceedance <= 310 * 12 * alpha').
Threshold (defect). f is "flagged (near-character)" iff D(f) < 0.25 on some curve (a character-like function has D near 0;
a random function has D close to 0.5 because it needs ALL ~r^2/2 distinct pair constraints to be small; the empirical null
minimum D is reported to confirm the gap). Average-defect flag: mean defect < 0.20 (null mean is 0.25).
Hypothesis predicts: no f flagged by either criterion on any curve. Also report p_F = 1-(1-exp(-r F^2))^(r-1) for each
(f,curve) with min p_F x 480 (Bonferroni-adjusted) and the distribution of the p_F (KS vs uniform, informative only).

### E-B (HYP-e1959734): coordinate-predicate independence
Curves: 120 curves, p log-uniform in [10^3, 10^5] (draw ln p uniformly, take integer part, reject composites),
S1 = 20261104, S2 = 20271104. Sequence P_k = [k]P, k = 1..h with h = (r-1)/2 (HALF RANGE: one representative of each
{k, r-k} pair; this removes the exact symmetries x(-Q)=x(Q), y(-Q)=-y(Q), which would otherwise make full-period
sequences palindromic/anti-palindromic and invalidate the i.i.d. null).
Predicates (binary; recorded as +/-1): A = [x(P_k) is a quadratic residue mod p] (x = 0 counted as residue, <= 2 points),
B = [y(P_k) is a quadratic residue mod p] (y != 0 since #E odd), C = [x(P_k) is even] (x as integer in [0,p)).
Tests per predicate (7): chi-square independence test of the 2 x m contingency table (predicate vs k mod m), for each
m in {2,3,4,5,8} (df = m-1; expected counts from the table margins, so the known small population bias of
O(1/sqrt(p)) in the predicate frequency, which is a real property of the curve, is NOT counted against the hypothesis);
lag-1 autocorrelation of the mean-centred +/-1 sequence, z = r1*sqrt(N), two-sided normal p-value;
maximum over c = 1..floor((N-1)/2) of |S_c|^2/(N*sigma^2) (S_c the DFT of the centred sequence, sigma^2 its empirical
variance), p = 1-(1-exp(-t))^M with M = floor((N-1)/2) (Exp(1) null).
Total 3 x 7 = 21 tests per curve, 21 x 120 = 2520 tests. Bonferroni: family-wise alpha = 0.01, per-test
alpha' = 0.01/2520 = 3.97e-6. Rejection iff p < alpha'. Distribution check: KS test of the 120 p-values of each of the 21
test types, and of all 2520 pooled, against U(0,1); the 22 KS tests are themselves Bonferroni-corrected (reject at
0.01/22). Also report the fraction of p-values below 0.05 / 0.01 (expected 5% / 1%), the minimum p, decile histogram.
Calibration controls (same pipeline): (N) iid fair random +/-1 sequences of the same length h (3 per curve) for the
KS-calibration of the pipeline; (P) injected-bias sequences (3 per curve): period-3 bias P(+1)=0.6 if k mod 3 = 0 else
0.45; lag-1 persistence (repeat previous value w.p. 0.55); weak sinusoid P(+1) = 0.5+0.05 cos(2 pi * 0.1237 k). These
report the detection rate (fraction rejected at the Bonferroni level) so that a null on real predicates can be read
with its power.
Hypothesis predicts: no rejection and p-values consistent with uniform.

### Run budget
Each script < 5 minutes. Scripts: round2/stats.py, round2/ea.py, round2/eb.py; outputs round2/ea_S1.json etc.
Deviations from this protocol, if any, will be listed explicitly in the report.

## Environment
Python 3.13.18 (CPython), numpy 2.5.3 (pre-installed; used for array arithmetic and FFT only; no scipy), Linux 6.18 x86_64
container, Intel Xeon @ 2.30 GHz, 4 vCPU, 15 GiB RAM, no GPU. Single-process for E-A (~1 min per seed); 4-process pool for E-B
(8 s and 13 s). Starting commit 9091112dbed98568882fd2fc755829a5d1bde4ae; nothing committed. Script/protocol/output hashes:
`research/ecdlp/experiments/round2/SHA256SUMS.txt`. Protocol file SHA-256 (taken before any script existed):
296eddcb185753439a72297bba117ecb8a87875f0e291ba2e9044d4a1125d032 (the "Pre-registered protocol" section above is the file verbatim).
Timeline (UTC, from `date -u`): protocol written ~09:17; stats.py self-test 09:17:50; ea S1 09:18; ea S2 09:19:41; eb S1 09:22:25;
eb S2 09:23:17. Post-hoc scripts after that. Toolchain not used: no Lean (empirical task, proof status not-applicable).

## Commands executed (all from /home/user/math/research/ecdlp/experiments/round2, all exit 0)
Run directly (not through `scripts/research.py exec`; outputs were inspected from the terminal and the JSON files; this is a manual record):
1. `python3 -I stats.py`  -> `stats selftest True`
2. `python3 -I ea.py 20261103 ea_S1.json`   (E-A seed S1; pre-registered)
3. `python3 -I ea.py 20271103 ea_S2.json`   (E-A seed S2; pre-registered replication)
4. `python3 -I eb.py 20261104 eb_S1.json`   (E-B seed S1; pre-registered)
5. `python3 -I eb.py 20271104 eb_S2.json > eb_S2.out`   (E-B seed S2; pre-registered replication)
6. POST-HOC, NOT pre-registered: `python3 -I ea_posthoc.py` (symmetry-aware Fourier recalibration; -> ea_posthoc.json; this
   script was run twice: the first version had a counting error for odd functions (it used (r-1)/2 distinct frequencies, correct is r-1),
   found because its own matched-null calibration check failed (KS p ~ 1e-100); corrected and rerun, the reported numbers are from the
   corrected version).
7. POST-HOC, NOT pre-registered: `python3 -I eb_diag.py` (run twice: the second run adds the order-shuffled control and removes a
   degenerate predicate; reported numbers from the second run; -> eb_diag.json).
8. Small ad-hoc numpy snippets (not saved) used while debugging the post-hoc odd-function null (checked marginal chi2_1 tail and the
   median of the maximum). `sha256sum` for SHA256SUMS.txt.
Outputs: ea_S1.json, ea_S2.json (per-curve parameters (p,a,b,r,P), every f's D, average defect, F, argmax c, p_F, flags, controls, null
summaries), eb_S1.json, eb_S2.json (per-curve parameters and all 21 p-values + controls), ea_posthoc.json, eb_diag.json.
Reproduce: re-run commands 2-5 (deterministic given the seed; Python `random.Random` string seeds, numpy generators seeded from them).

## Results E-A (HYP-130de9b1): approximate characters
Pre-registered quantities, seed S1 = 20261103 / replicate seed S2 = 20271103; 12 curves each, 40 functions each (480 tests/seed),
p in 1483..4481 (S1) and 547..4129 (S2); curves (p,a,b,#E) are in the JSON.

Defect (pre-registered flag D<0.25, avg<0.20): 0 flags in both seeds.
- Smallest D(f) over all f and curves: 0.4997 (S1), 0.4991 (S2). Smallest average defect 0.2493 / 0.2475 (null mean 0.25).
- Null (random functions): D in [0.49999, 0.5]. So every family function has the defect of a random function (~1/2, the max possible).
- Positive controls (all 12 curves per seed): exact characters D = 0, F = 1.000 (flagged 12/12 by both criteria); rounded-to-1/p
  characters D = 2e-4..1.8e-3, F = 1.000 (12/12); character+noise(+-0.05) D = 0.148..0.150, F = 0.983 (12/12); mixtures D = 0.5
  (not flagged by D, as expected) with F = 0.48-0.53 (w=0.5), 0.17-0.24 (w=0.2), 0.07-0.115 (w=0.1); Fourier-flagged 12/12, 12/12,
  and 9/12 (S1) or 10/12 (S2) respectively. Sensitivity: the pipeline detects a character that explains >= ~10-20% of the amplitude.
  (Positive control used discrete-log indexing from the oracle; indices cross-checked against `dlog_bsgs` on 3 points per curve.)

Fourier statistic, PRE-REGISTERED analysis (threshold T_F(r) = sqrt(ln((r-1)/2.08e-5)/r), 0.066..0.18 depending on r):
- S1: 4 flagged of 480: (curve 2, coef (0,0,1,0) = x*y/p, F=0.0688 vs T=0.0680), (curve 7, (0,1,-1,0), 0.0817 vs 0.0791),
  (curve 7, (0,1,1,0), 0.0795 vs 0.0791), (curve 10, (0,1,1,0), 0.0900 vs 0.0831). max F/T = 1.084.
- S2: 1 flagged of 480: (curve 5, (0,0,1,0), 0.0692 vs 0.0683). max F/T = 1.013.
- Null draws (3720 per seed): max F/T = 0.977 (S1), 0.945 (S2); 0 exceedances of T_F.
- KS of the 480 p_F against uniform: p = 1.5e-6 (S1), 9.7e-6 (S2): the pre-registered null was MISCALIBRATED for these functions.
By the pre-registered rules this is a positive result in S1 and (weakly) in S2 -> "candidate", and it was re-tested with the fresh seed
as required. The replication did not reproduce the same (f, curve) pairs, c* values (argmax frequencies) are scattered (e.g. 1406,
2608, 629, 3555, 373, 861, 1779, 1019 out of r~3000-4000), but ALL flagged functions are of the form containing y (odd under
Q -> -Q: be,ga != 0 and al=de=0 for xy, y+xy, y-xy).

Cause (found post-hoc; this is a flaw in my pre-registered null, not a finding about the curves). f(-Q) = -f(Q) for odd f (y, xy, ...,
and for combos with al=de=0), so e(f(jP)) is conjugate-symmetric in j and every Fourier coefficient is REAL, i.e. |S_c|^2/r ~ chi2_1
(tail ~ e^{-t/2}), not Exp(1) (tail e^{-t}); even f (x, x^2, x+x^2 combos) have c<->-c symmetry, i.e. (r-1)/2 distinct frequencies
(pre-registered threshold conservative); generic f satisfy the pre-registered null. I did not anticipate the symmetries x(-Q)=x(Q),
y(-Q)=-y(Q) in E-A, although I had in E-B.
POST-HOC symmetry-aware recalibration (ea_posthoc.py; deviation, not pre-registered): matched Bonferroni over the same 480 tests
(per-test alpha' = 2.08e-5): 0 rejections in both seeds. Smallest symmetry-aware p: 0.0069 (S1; Bonferroni-adjusted 1.0), 0.000196
(S2; Bonferroni-adjusted 0.094). KS of the symmetry-aware p-values vs U(0,1): even f p=0.23/0.06, odd f p=0.25/0.026, generic f
p=0.053/0.159, all f pooled p=0.45 (S1) and 0.058 (S2); empirical matched-null calibration of the corrected p-values (1800 random
functions per class per seed): KS p between 0.18 and 0.94 (all classes, both seeds), fraction below 0.01 about 0.6-1.3%. The
S2 odd-f KS p of 0.026 is not significant after correcting for 3 classes x 2 seeds.
Summary E-A: no function in the family is near-character (all defects ~1/2 = random level) and no function correlates with a
character beyond the symmetry-corrected null. By the pre-registered letter the Fourier criterion flagged 4 + 1 candidates, which I
attribute to the null miscalibration for odd functions (explained and verified post hoc, but the correction was chosen after seeing
the data, so it is a deviation).

## Results E-B (HYP-e1959734): predicate independence
120 curves per seed, p in 1039..97499 (S1), 1039..99277 (S2); h=(r-1)/2 values of k per curve; 21 tests x 120 = 2520 tests/seed;
Bonferroni per-test threshold 3.97e-6. Curve parameters (p,a,b,#E,P) are in eb_S1.json / eb_S2.json.

Pre-registered primary criterion (any p < 3.97e-6): 0 rejections in both seeds. Smallest p: 5.8e-4 (S1; C_x_even:chi2_m5, p=1723),
8.8e-4 (S2; C_x_even:chi2_m3, p=21557); both Bonferroni-adjusted 1.0. Fraction of p below 0.05: 2.6% (S1), 2.9% (S2) (expected 5%);
below 0.01: 0.60% / 0.24% (expected 1%).
All 15 chi-square tests (3 predicates x m in {2,3,4,5,8}) and the C_x_even lag1/dft are individually consistent with U(0,1) in
both seeds except where noted below (per-test KS p: chi-square tests 0.012..0.87 in S1, 0.012..0.63 in S2; only the smallest, A:chi2_m8
S2 p=0.0119 and C:chi2_m5 S1 p=0.025, are above the Bonferroni level 0.01/22 = 4.5e-4).

Pre-registered distribution check (KS) FAILS and replicates: 
- S1: pooled KS p = 3.2e-13; 5 of 22 KS tests reject at 4.5e-4. S2: pooled KS p = 9.9e-13; 4 of 22 reject.
- The rejecting tests, in both seeds: A_x_QR:dft (KS p < 1e-70), B_y_QR:dft (< 1e-70), B_y_QR:lag1 (1e-4 S1; 1e-6 S2), and A_x_QR:lag1
  (4e-4 S1, 0.012 S2). Decile histogram of the 120 p-values for the DFT tests: ~107-109 of 120 fall in the top decile (p>0.9), 0 in the
  lower half. The same tests on iid null sequences are calibrated (pooled KS p = 0.045 S1, 0.97 S2; 0 Bonferroni rejections; frac<0.05
  4.8% / 5.1%).
- Direction: the Legendre-predicate sequences have a FLATTER spectrum than random (maximum DFT power smaller than that of random
  sequences, lag-1 autocorrelation z of smaller variance), i.e. they are more equidistributed than random sequences, not biased
  towards a leakage-type pattern; the upper-tail tests used for the Bonferroni criterion cannot reject on this.
- Controls (power): at the Bonferroni level the pipeline detects the injected period-3 bias in 70-75% of curves (chi2_m3) and 53-63%
  (DFT), the injected lag-1 persistence in 55-68% (lag1), the injected weak sinusoid in 29-30% (DFT) (smaller curves lack power: these
  injected effects have fixed size while N = h varies over 500..50000).
POST-HOC diagnostic (eb_diag.py, 40 curves of seed S1, NOT pre-registered). Variance of the normalised periodogram ordinates
(Exp(1) null: 1): chi(x) 0.661 (sd across curves 0.037), chi(y) 0.665, chi(x+1) 0.661, chi(2x) 0.661, but chi(x^2+x+1) 1.010,
chi(x*y) 1.011, parity(x) 1.012, parity(y) 0.997, [x<p/2] 1.008, a SHA-256 bit of x 1.009, iid 0.995, and chi(x) with the order of k
randomly shuffled 1.013. So the flatness is (a) specific to Legendre symbols of linear functions of x and of y, (b) carried by the
ORDER in k (not by the fixed set of x-values), (c) of a stable size (~2/3) across curves and across p in 1e3..1e5. I did not establish
the cause. It could be an arithmetic property of the Legendre symbol of the x-coordinates / y-coordinates under the group law, or a
property of my half-range window (the 2/3 value is suspiciously constant), and I did not check against an independent
implementation of the group law (the oracle was only cross-checked by its own test-suite). Treat it as an unexplained,
twice-reproduced (two seeds, S1 and S2) departure from the i.i.d. model, a candidate for follow-up (e.g. test whether the same
flatness appears for other prime-order curves family, other half-ranges, and compute the exact second moments).

## Interpretation and limitations
- E-A: on the tested domain (12+12 random prime-order toy curves, p in 547..4481, 40 low-degree coordinate functions), every function
  has near-maximal defect (~0.4991-0.5; average ~0.25), i.e. none is close to a homomorphism; and after a symmetry correction (post hoc)
  no function has a significant Fourier correlation with a character. The pre-registered Fourier rule produced 5 flags that I trace to
  an error in my null (odd functions have real coefficients), so strictly: pre-registered criterion violated in S1 and S2 (marginal,
  max F/T = 1.08, 1.01), not reproduced as a specific (f, curve); the post-hoc corrected criterion is satisfied. Prediction "no f
  exceeds threshold": supported only after the post-hoc correction and only on this toy domain; the threshold was derived assuming
  symmetries I did not model, which weakens the pre-registration value of the corrected result. Positive controls show the pipeline
  has power for characters and for a character component of amplitude >= ~0.1-0.2.
  The family is small and structured: it covers only polynomials of degree <= 2 in x,y with coefficients in {-1,0,1}; nothing is
  implied about other families, larger coefficients, composition with non-linear maps, or other group elements than the full group.
- E-B: no individual predicate/test combination is significant at the Bonferroni level, in either seed (supports H-B on the tested
  domain for the pre-registered primary criterion), BUT the pre-registered p-value-distribution check rejects uniformity in both seeds,
  because Legendre predicates of x and y give sequences whose DFT maximum and lag-1 autocorrelation are systematically too small. That
  contradicts "behaves like an independent random sequence" in the second-moment sense, though not in the direction that would leak
  information through k mod m (chi-square tests are fine). The mechanism is unexplained; it must not be reported as a finding until
  confirmed by an independent implementation and an exact derivation. (An implementation or analysis artifact of the shared pipeline
  was not excluded; iid, parity and hash-bit controls are fine, which argues against a pipeline bug but not against a bug in the shared
  curve oracle/half-range construction.)
- Common limitations: finite toy sizes only (p <= ~1e5), no statement about cryptographic sizes; no proof (proof_status
  not-applicable); the tests used asymptotic nulls (chi-square, normal, Exp(1)) validated against iid controls but not against exact
  finite-population distributions; Bonferroni with p-values near the asymptotic tail is approximate; null calibrations for E-A were
  wrong for symmetric functions as described. Seeds, curve parameters and all p-values are stored. No git operations were done, no web
  lookups, no sub-agents. Runtime for each script < 1.5 minutes.
- Next actions (for PI): (1) decide whether the E-A post-hoc symmetry-aware null counts; if the pre-registration is to be honoured a
  third fresh seed with the corrected, pre-registered symmetric null would be the clean test; (2) investigate the Legendre-predicate
  spectral flatness (exact variance of the periodogram for chi(x+c) sequences; independent group-law implementation; compare with
  x-only predicate in the multiplicative group and random-point models); (3) extend E-B to full-period sequences with the symmetry
  built into the null.
