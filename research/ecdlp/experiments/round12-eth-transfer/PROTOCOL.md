# Round 12 / ETH-transfer protocol (RUN-956c1a00, TSK-2c09a4bf) -- pre-registered before registered outputs

Owner: algorithm-inventor (claude-sonnet-5-5, configured, not runtime-verified). Source (external, not peer reviewed,
not verified by us): OpenAI preprint "The Exponential Time Hypothesis is False" (25 Oct 2026). Toy sizes; nothing here
is an asymptotic claim about ECDLP.  E2 and E3 were written after reading the paper; E1 was written after the E2 pilot
printout (E2 itself is a deterministic formula evaluation, no data).

## Questions and decision rules (fixed now)
Q1 DIRECT. E1 builds the CNF of two existing lab encodings (round10 affine double-and-add, round11 x-only ladder) WITHOUT
solving, for ell = bitlength(r) = 5..16 (affine) / 5..14 (ladder), 3 prime-order instances per ell (seed 12121). Fit
log2(vars) = a*log2(ell) + b by OLS, bootstrap 95% CI over instances (2000 resamples, seed 7).
 Crossover statement (exact): the source's headline form gives time 2^{C n / sqrt(ln n)}; Pollard rho is ~2^{ell/2}.
 Crossover iff  C*n/sqrt(ln n) < ell/2  <=>  n/ell < sqrt(ln n)/(2C).  With n(ell) >= ell this forces n/ell < sqrt(ln n)/2C.
 DECISION: route D is "hopeless" iff for the measured/extrapolated n(ell) the inequality fails at every ell>=8 for C=1
 (most favourable constant) AND under the source's own displayed parameters (E2) the algorithm exceeds 2^{n} (no gain
 over exhaustive search) for every n below the E2 threshold.
Q1b E2 evaluates the paper's own displayed parameter choice (Lemma 4.8 / eq. 4.17, beta=1) and cost decomposition (eq. 2.11)
 to find (i) the least log2 n at which the paper's numerical hypotheses hold, (ii) least log2 n with f<1 (beats 2^n), f<1/2.
Q2 TECHNIQUE. E3 measures the sparsity of the algebraic normal form (ANF over F_2 of each output bit; multilinear F_p
 polynomial) of k -> x(kP) on toy prime-order curves, ell = 6..14 (2 instances each, seed 31). The technique needs
 O(n) equations with <= (log n)^c monomials and degree <= k_const. Decision: bit/F_p representations are "dense" iff
 nonzero-coefficient fraction >= 0.25 for every ell; then route (c) in its sparse-polynomial form is killed.
 Analytic part (report): exponents for routes (a),(b),(c) as functions of p from E1/E2 numbers.
Q3 PROTOTYPE. Gate: only built if some route survives Q1/Q2. Otherwise record "not built, reason" (no benchmark vs rho).
 If built it must use toyec.py, same seeds/sizes (>=4) as rho in round12-inventor-a (out_rho.jsonl), fitted exponent + CI.
