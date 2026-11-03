# PROTOCOL — RUN-9fe2318a (round 21, frontier explorer A, idea tournament): Koopman / Prony / DMD on translation orbits

Pre-registered before any data. Toy curves only (academic). Hash of this file in PROTOCOL.sha256.

## Idea under test (A1, the only idea of the tournament that survived the paper gate)
Translation by P is a dynamical system (an irrational-rotation analogue) on E(F_p) = Z/r. Its Koopman operator is diagonal in the
characters e(s*j/r). If some cheap observable f(x,y) had a SPARSE character expansion (K << r frequencies), then the orbit
sequence y_j = f(jP), j = 1..N with N ~ O(K) << sqrt(r), would have Hankel rank K, be linearly predictable (Prony/DMD), and the
orbit started at Q (y'_j = f(Q + jP)) would be a phase-shifted copy giving k from the K phases e(s_i k / r). Wall it must escape:
equidistribution / Weil-type character-sum bounds (every coefficient O(r^-1/2) => no sparsity), Theorem-A/Lange-Winterhof linear
complexity (F_p-valued recurrences). Test asks whether any measurable low-rank structure exists at all in the orbit sequence;
if not, no k-dependent phase exists to decode.

## Instances
Prime-order curves from round12 `find_prime_order_curve(bits, seed)` (lib12.py), bits in {16, 20, 24}, seeds 1,2,3 (9 curves),
P = generator returned. Sequence length N = 400: points jP, j = 1..400 by repeated addition (x_j, y_j).

## Observables (complex or real; centred and scaled to unit variance per sequence)
O1 e(x/p); O2 e(y/p); O3 Legendre symbol of x (+-1, 0->0); O4 x mod 2 as +-1; O5 x/p (real); O6 e(x^2/p) (non-linear phase);
O7 sign-pair: (-1)^(x_j + x_{j+1} mod 2)... NOT used (dropped before data). Total 6 observables.

## Statistics (per sequence)
S1 Hankel participation ratio PR = (sum s_i^2)^2 / sum s_i^4 of the 200 x 201 Hankel matrix (SVD). Rank-K signal gives PR ~ K.
   Control: 30 random shuffles of the SAME observable values (same marginal, no order structure); z = (PR_real - mean_ctrl)/sd_ctrl.
S2 One-step linear prediction: complex least squares AR(m=30) fitted on samples 1..200 (ridge 1e-8), applied one-step to samples 231..400;
   NMSE = mean|err|^2 / mean|y|^2. Control: same on 30 shuffles.
S3 Periodogram peak: max over a 4x-oversampled grid of |DFT|^2 / (N * var) ; control shuffles; reports z in sd of control.
S4 Berlekamp-Massey linear complexity over F_p of the raw sequences x_j and y_j (j=1..400); a theorem-level expectation is
   LC = 200 +- 2 (max); control = uniform random sequences mod p.
Planted control (must be detected): s_j = sum_{i=1..5} c_i e(f_i j) with random frequencies f_i in [0,1) and c_i with |c|=1, plus complex
Gaussian noise sd 0.1; passed through the same S1-S3 pipeline.

## Decision rule
Idea A1 has a SIGNAL iff for some observable, at >= 2 of the 3 sizes and in >= 2 of 3 seeds each: (z_PR < -3) AND (NMSE < 0.9)
(NMSE of shuffles is ~1.0). Otherwise A1 is KILLED (null). A null is accepted only if the planted control is detected
(PR <= 8, NMSE < 0.2) AND S4 LC is within +-3 of 200 on >= 95% of the real sequences. No exponent or cost fits are needed
(no algorithm results). Because A1 yields no algorithm unless a signal exists, a rho control fit (alpha*sqrt(r)+gamma) is NOT run for
A1; if a signal had appeared, an end-to-end decoder vs rho with the alpha*sqrt(r)+gamma fit (never naive log-log) would be
pre-registered in an addendum before being run.

## Ideas killed on paper (not tested; see run report): A2..A8. Each carries the wall it hits.
