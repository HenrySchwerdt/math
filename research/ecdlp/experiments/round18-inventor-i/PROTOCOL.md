# PROTOCOL round 18 / inventor I (RUN-ef5a03e5-0583-4a71-bfe8-25040636cd62) -- written and hashed BEFORE any measurement

Question: can the decision "R in B+B+B+B, and find the decomposition" (m = 4, base B of size s ~ kappa p^{1/5}) be done in
T_test < p^{1/10}?  PI accounting: total ~ (p/s^3) T_test + LA(s); the method beats sqrt(p) only if T_test < p^{1/10}.

## Instances
- bits in {20,24,28,32,36,40}; p prime, p ~ 2^bits, p = c*d + 1 with d = 2*round(kappa*p^{1/5}/2) (kappa = 1 for T_test), so |B| ~ d.
- curve y^2 = x^3+ax+b random over F_p (not required prime order; targets are uniform random points of E(F_p)).
- Bases: COSET = {x : x^d = c}, x = g*mu_d, points (x, +-y) when x^3+ax+b is a QR (|B| ~ d).
  Also controls RANDOM (same size, random x) for the MITM finder.
- seeds: 3 curves per size (seed 0,1,2), 20 uniformly random targets per curve (T_test timing), plus 5 planted targets per curve
  (sum of 4 random base points) for correctness (every finder must return a verified decomposition).

## Finders (T_test = cost per target, precomputation excluded and reported separately)
- MITM: 2+2 hash. Precompute hash of x-coordinates of all pair sums (s^2/4 classes). Per target, for each pair-sum S compute R+-S
  and look up x. Counted ops: EC additions + lookups (exactly deterministic), plus wall time.
- TOWER (resultant tower / S_3 chaining): R = U + T with U,T in B+B. Precompute A2(X) = prod_j (X - X_j) over pair-sum x-values.
  Per target Q(X') = prod_j S_3(X_j, X', x_R) (degree 2*#X, product tree), g = gcd(Q, A2) over F_p with python-flint 0.9.0
  (nmod_poly). Nontrivial g <=> decomposable (then root lookup + verification by point arithmetic). Wall time per target.
- GB (Groebner basis, sympy 1.14, modulus p, grevlex) on the S_3-tower system {S_3(x1,x2,U), S_3(x3,x4,T), S_3(U,T,x_R), x_i^d=c}
  (S_5 eliminated through U,T), d = 3..(as far as 120 s allows), planted target. Singular/Magma/Sage: checked, not installed.
- Cross-check: MITM and TOWER must give identical found/not-found on every common target (hard failure otherwise).

## Fit and decision rule (fixed in advance)
- Per size, T_test = mean over all random targets (MITM ops; wall time for TOWER). Fit T = alpha*p^beta + gamma by scanning beta in
  [0, 1.5] (step 0.005), alpha,gamma by least squares in relative error; CI for beta by bootstrap over curves (2000 resamples,
  95% percentile). Report also naive log-log slope only as a labelled warning (round-16 lesson).
- Success probability per target lambda(kappa) measured by MITM on random targets for bits in {20,24,28}, kappa in {1,2,3,4}
  (N large enough); compared with the model lambda ~ C(s,4)/#E.
- DECISION: a finder "qualifies" if the 95% bootstrap upper end of beta is < 0.10 AND it is verified correct. If any qualifies:
  build the relation+linear-algebra pipeline and benchmark vs same-implementation rho on the same curves under a new PROTOCOL.
  Otherwise: report the obstacle with measured exponents. No speedup is claimed without measurement.
