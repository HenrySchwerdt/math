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
