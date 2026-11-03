# Round 10 frontier-B pre-registered protocol (RUN-071d1da9, ECDLP-29)

Written before any scaling/learning result was produced. Code: sat_ecdlp.py, learn_k.py (sha256 in HASHES.txt).
Selftests (m = 6..8, ~10 instances, to debug the encoding) were run first; they are NOT part of the registered data.
Debug finding recorded: the first encoding wrongly demanded x(R_i) != x(C_i) even on 0-bits; fixed by selecting
instances with no exceptional step along the true path (selection effect on k, negligible; sound encoding, may be
incomplete only on exceptional k).

## T1 (F-B1): CNF/SAT encoding of [k]P = Q, bits of k as variables
Encoding: double-and-add from a random offset S; constants C_i = 2^i P; each step computes R_i + C_i with
modular multiplier/adder circuits mod p (3 modmul + 4 modsub per bit) and a MUX on the key bit; final R_n = Q + S.
Solver: pysat Glucose4 (pip python-sat 1.9.dev17), conflict budget 1.2e6, no restarts tuning, no preprocessing tweaks.
Curves: random prime-order, p in [2^(m-1), 2^m), m = 6..10, 3 instances per m (seed 11), random P, k.
Metric: conflicts (machine independent) and wall seconds, vs Pollard-rho cost model sqrt(pi*r/2) group operations.
Hypotheses (prediction before run):
  H1a: solver conflicts grow at least like r^1 (slope in log-log vs r >= 1, i.e. no better than brute force;
       gate: median conflicts ratio per extra bit >= 2).
  H1b: it never undercuts rho: rho_ops << conflicts for every m.
  Kill (of the idea "plain SAT is a sub-sqrt route"): H1a and H1b hold. Support would be: slope < 0.5 over m=6..10
  with no censoring. Statistic: least-squares slope of log2(median conflicts) on n = bitlength(r) (growth factor per bit).
T1b (hints / interval DLP): m = 10 instance family (seed 12), top n-t bits of k asserted known, t = 4, 6, 8, 3 instances each;
  compare growth per unknown bit with kangaroo cost 2^(t/2).

## T2 (F-B2): learning null test
Fixed curve/P, entire group enumerated: x,y of kP for all k in [1,r). Random 70/30 split by k (seeded permutation).
Features: bits of x,y plus 8 Fourier harmonics of x/p, y/p (cos, sin). Models: logistic regression, 1-hidden-layer tanh MLP (64).
Labels: each bit of k; [k < r/2]; [k mod 3 = 0]; sign-invariant label [min(k, r-k) < r/4] (determined by x alone; an
information-theoretic positive "in principle" label but a DL-hard function).
Setups: m = 10 and 13, seeds 1,2,3 (each seed own curve). Controls: identity encoding (coordinates are k itself; must reach ~1.0) and
x-parity label (must reach ~1.0) show test power.
Decision rule: flag a label if test accuracy - majority baseline > 4*sqrt(0.25/n_test) (z=4, ~170 tests per m => family
false-positive rate < 1%). Prediction: no flags for the ecdlp setup, all controls flagged. A flag would be re-run on fresh seeds
before being believed.
Scope: toy sizes only; a null says nothing about asymptotic structure.
