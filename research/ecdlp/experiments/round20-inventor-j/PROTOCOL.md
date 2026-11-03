# PROTOCOL — RUN-809bfa01 (round 20, inventor J): estimate k precisely, then finish by binary search / kangaroo

Pre-registered before any model is trained. Pilots allowed before freeze: curve generation, `feat.c` speed/correctness check on one 20-bit curve
(output discarded). The hash is of this file; later changes go in PROTOCOL_ADDENDUM.md (hashed separately, written before the affected run).
The coordinator's closeness-detector request (PI message during the run) is included here (section C) before any data exists.

## Curves and sizes
Prime-order curves from round12 `find_prime_order_curve(bits, seed)`, bits in {12,16,20,24,28} (r ~ 2^12 .. 2^27.3), seeds 100..107 = TRAIN curves, 108..111 =
HELD-OUT curves (never trained on). Frozen in `curves.json`. Round-16 curves (seeds 0-5) are not reused.
Held-out k: scalar s -> class h(min(s,r-s)) = ((min*2654435761)>>7)&1; train uses h=0, "held-out k" uses h=1 (+-k pairs always on the same side).

## A. MSB estimator (classification)
Label y = [k > r/2] (k uniform in [1,r-1]; r odd, exactly balanced). Q=kP, P known. Note x(Q)=x(-Q) and y(MSB) flips under Q->-Q: any predictor must use sign of y.
Features (all computed from Q, P with O(1) group ops; raw coordinates from `feat.c`): x,y as floats /p and all bits (<=28 each); parity/threshold of y; x(Q+jP), x(Q-jP), j=1..3:
floats, bits of low 8, differences mod p /p to x(Q), comparisons (x(Q+jP)<x(Q), <p/2), y parities; x(2Q) float/bits/comparison; Legendre symbols of y, x, x+1, x-Px, y-Py;
carries of x(Q)+Px, x(Q)-Px, y(Q)+Py in binary (carry/borrow vector, 28 bits); x(Q) xor x(2Q) low bits.
Models: (M1) HistGradientBoosting (sklearn, max_iter 300, lr 0.1, early stopping on 10% of train), (M2) MLP (128,64), standardized, 100k-sample subset, early stopping,
(M3) logistic regression, (M4) best single feature (picked on train, threshold fit on train).
Training per size: 8 train curves x 20000 samples with k-class 0 (150k..160k). Tests: TEST-A = same 8 curves, k-class 1, 25000/curve; TEST-B = 4 held-out curves, k uniform, 50000/curve.
(Both 200k.) Statistic: accuracy, advantage |acc-1/2|, Wilson 99% CI (per test, per model), reported for all models; headline = M1 and M2 each, no selection on tests.
Positive control (planted leak): extra feature column leak = y xor Bernoulli(0.45) with the Bernoulli determined by hash(x,y,curve) (advantage 0.05 exactly in expectation),
appended to the feature matrix, same pipeline; must be flagged (lower CI bound > 0) at all 5 sizes by M1, else the pipeline is declared unable to detect and no null is claimed.
Decision: "non-vanishing advantage" for a model iff Wilson-99% lower bound of acc > 0.5 in BOTH TEST-A and TEST-B at >= 3 of 5 sizes, with a Bonferroni-corrected
check (99.9%) reported alongside. Detectable advantage (half CI width) reported per size.

## B. Regression of k
Target theta = k/r on the circle; regress (sin 2 pi theta, cos 2 pi theta) with HistGradientBoostingRegressor on the same features (same splits); predicted angle atan2.
Report R^2 of both components, median and 90% quantile circular error |theta_hat-theta| (random guess: median 0.25, 90% 0.45) on TEST-A/TEST-B, and the implied interval width
w_q (in units of r) containing k with probability q (q=0.5, 0.9) = 2*quantile_q, with bootstrap CI over test samples. Planted regression control: extra feature theta + N(0,0.1^2) (circular); must give
median error ~0.067.

## C. Closeness detector (PI request)
For a residual R = dP, question: does any computable feature of R depend on |d|? Compare (a) |d| <= w, d = +-U[1,w], w in {2^4,2^8,2^12} (only w <= r/16), vs (b) d uniform in [1,r-1],
balanced classes. Same features (R plays the role of Q), same M1/M2/M3, same splits (class (a) d and class (b) d in k-classes; train curves / held-out), 99% Wilson CI, planted
control (extra feature = [|d|<=w] xor Bernoulli(0.45)). Table exclusion: a table of S0=16 entries {jP: |j|<=16} (cost 1 lookup per query, S0 stored points, group cost 0 online) recognises
|d|<=16 with probability 1; so the "beyond-table" statistic is the accuracy on a re-balanced test set with class (a) restricted to |d| > 16 (w=2^4 is entirely table-recognised and is reported
as "table-trivial" only). A feature counts only if the beyond-table 99% lower CI bound > 0.5 at >= 3 of the eligible sizes; per-unit-of-work comparison is in the cost model D.

## D. End-to-end pipelines on the planted-leak control and cost model (all in Python, counted group ops, affine add/double = 1 op, same `Ops` class as rho control)
Planted oracle family F(eps): Omsb(Q') returns [k'>r/2] flipped with probability 1/2-eps, flip bit = splitmix(x,y,seed) (deterministic function of the point; simulator knows k' = scalar of the
point, which is equivalent to the planted curve family being defined by the dlog table). Planted regression oracle G(rho): returns k' + Gaussian noise with sd rho*scale (scale given in call).
Pipelines (success = output verified kP=Q):
- P0 naive noisy binary search with additive shifts Q+aP (one oracle call per threshold, cannot be repeated): measured success vs (1/2+eps)^(log r) prediction.
- P1 stride-ML iterative refinement (multiplicative self-reduction with structured multipliers): round i holds window |d|<=W_i around current estimate g (residual R=(k-g)P); queries
  c_j = j*m, m = ceil(r/(2 W_i)), points c_j R via 1 op (add mR) per query after one scalar mult; bit b_j = Omsb; ML over grid of 4N candidates d in [-W_i,W_i]; new g, W_{i+1} = max-error bound
  chosen as r-scaled resolution * 3; N from calibrated nu: N = ceil(nu * ln(grid)/eps^2) with nu fixed by the P1 calibration run (smallest nu in {0.5,1,2,4} with >=95% round-success on 20-bit control); stop when
  W <= W_f then finish by kangaroo (P2) on the window or brute force BSGS if W <= 2^10. Reported: window width per round, queries, ops, success.
- P2 interval + kangaroo: interval [a,a+w] known (width from regression-oracle control G, or from P1), Pollard kangaroo with distinguished points, jumps ~ sqrt(w)/2 mean, restarts counted.
  Cost fit: kangaroo ops vs w: alpha_k sqrt(w)+gamma_k (least squares, bootstrap 95% CI) from a standalone run (sizes w=2^8..2^24, 100 reps).
- Rho control: same implementation Ops, Teske-style 20-partition additive walk with DPs (r-walk), ops vs r fit alpha sqrt(r)+gamma over r in 2^12..2^28 (30 instances per size); NO log-log fits.
Bar: e(r) = minimal advantage such that predicted P1 cost (rounds * N(e) * (1 + m_q) with m_q = 7 feature ops, nu calibrated, rho-fit comparison) < rho fit, and the same for
closeness-detector scan: needed delta(w, W) such that (W/(2w)) * c_d * nu_d/delta^2 + alpha_k sqrt(w) < alpha_k' sqrt(W) (c_d = 8 ops per test).

## E. Verdict rules
Real-curve estimator has relevant out-of-sample advantage iff (A decision rule met) AND the 99% lower CI bound >= e(r) at that size. The expected outcome (equidistribution, HYP-130de9b1/80158648;
round 10 learned-bit-predictor null) is no leak; a null is accepted as such only because the planted controls are detected at each size. Nothing here asserts a speedup unless measured end-to-end.
