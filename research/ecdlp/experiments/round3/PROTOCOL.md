# Round 3 / ECDLP-9 pre-registered protocol (RUN-df8d0e71-aefa-4f53-8230-78b564b5c043)

Hypothesis H (HYP-242da418): for #E=r prime, full-range X_c = r^-1/2 sum_{k=0}^{r-1} chi(g([k]P)) e(ck/r),
c=1..r-1, satisfy max_c |X_c| <= C(g) sqrt(p/r); periodogram |X_c|^2 bounded and non-Exp(1).

Curves: buckets p in {[1000,2000],[4000,8000],[16000,32000],[64000,128000]}; 12 curves per bucket;
random.Random(master seed), p random prime in bucket, a,b uniform mod p; reject singular, #E not prime,
#E == p (anomalous), r < 100. #E = p+1+sum_x chi(x^3+ax+b) via Legendre table (numpy). P = random
affine point (order r). [k]P by repeated addition with toyec.Curve.add; [0]P=O.
Master seeds: 20261105 (primary), 20261106 (replication, fresh sample entirely).

Predicates s_k (k=0..r-1; value at O is 0): chi(g) for g in x, y, x+1, x^2+x+1, x*y, x^3+2 with
assumed degrees d = 1,1,1,2,2,3 (chi(0):=0); controls: parity(x) -> +-1 ; hash bit 7 of (x*2654435761 mod 2^32)
-> +-1 ; random +-1 sequence of length r (seeded); control value at O is 0 too.
X_c via numpy FFT (positive exponent, conj of fft), c=1..r-1.
Per (curve,predicate): M=max_c|X_c|^2, mean |X_c|^2 over c=1..r-1, Parseval check
sum_{c=0}^{r-1}|X_c|^2 = sum s_k^2, second moment mean|X_c|^4, M/ln r.

Decision rule: SUPPORTED for g iff (A) M <= 4 d^2 p/r for ALL 48 curves, or the OLS slope of M on ln r
(48 curves pooled) has 99% CI (t, df=46, crit 2.687) including <= 0 with the CI not containing ~1
(random control slope), AND (B) pooled second moment differs from 2 (|mean-2| > 3 pooled s.e. across
curves/>=0.2 absolute). REFUTED for g iff M grows like the random control (slope CI contains the control's slope
and excludes 0 ... or violates 4 d^2 p/r bound at large buckets) with second moment ~2 (within 0.2).
Otherwise INCONCLUSIVE. Controls must give second moment ~2 and M ~ ln r growth; otherwise pipeline problem.
Note: Exp(1) maximum over r-1 values expected ~ ln r + 0.577.
Oracle: for 2 curves (smallest bucket + one of 4000-8000), recompute 5 X_c by direct O(r) sum, tolerance 1e-9.
Leak sanity: in bucket 2 (all 12 curves), for each predicate, chi-square statistic of class means of s_k over
k mod 2 and k mod 3 (df 1 and 2) vs chi-square expectation; a leak = stat consistently >> df.
Replication: rerun with 20261106; the finding is reported only if the verdict is reproduced.
Runtime: each run expected < 5 minutes; counts not reduced.
Not a discrete-log leak claim; finite toy sizes only.
