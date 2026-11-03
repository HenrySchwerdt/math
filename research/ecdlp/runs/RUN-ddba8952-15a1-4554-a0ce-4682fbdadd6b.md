# RUN-ddba8952-15a1-4554-a0ce-4682fbdadd6b — round 21 tournament, frontier explorer B (algebraic geometry / number theory)

Toy curves only. Model: Claude Sonnet 5.5 (self-reported, not runtime-verified). No ledger claim is changed; nothing here improves on rho.

## Question, inputs, ownership
Invent at least 5 new ECDLP mechanisms from AG/NT beyond classical index calculus, gate each on paper against the obstruction map, test survivors with a
pre-registered protocol against a same-implementation rho control. Inputs read: docs/roles/frontier-explorer.md, research/ecdlp/STATUS.md (rounds 1-20),
the obstruction-map section of PAP-ef6e2010 main.tex (line 377 ff, skimmed to the extent of its first paragraph; the STATUS rounds were the primary closed-direction list),
HYP-80158648 / HYP-242da418 / HYP-e1959734 (Sato-Tate spectral law). Files written: `research/ecdlp/experiments/round21-tournament-b/*` and this report.
No sibling submissions read. Walls used: W1 supply s^{m+1}/p; W2 finder cost; W3 leakage bar eps >~ C r^{-1/4}; W4 isogeny invariance; W5 transfer
(embedding degree / anomalous / HYP-caa15771 all-or-nothing); W6 push-down only loses.

## Ideas and paper gates
**I1 — Riemann-Roch relations with poles in the base.** Take D supported on base points, f in L(D); div f = Z - D with Z effective of degree d. Hope: a linear system
(p^d functions) gives relations at a different rate than point decomposition. Gate: Pic^0(E) = E, so "Z ~ D" is literally "sum Z = sum D" in the group; the number of
f with Z inside the base is the number of ordered pairs of d-multisets of the base with equal sum: supply = C(M_d,2)/r with M_d = C(s+d-1,d), i.e. s^{2d}/p up to
constants = the m+1 = 2d law. Wall W1 (identical supply, RR only re-parametrises the divisor). Test A: observed/predicted 0.90/0.94/0.97 (d=2, s=40/80/160) and
0.90/0.95/1.00 (d=3, s=12/24/40), never above 1 (4 curves x 5 draws, `expA_results.json`). **Killed, W1.**

**I2 — Weighted divisors / multiplicity supply.** Allow D = sum a_i P_i with |a_i| <= c to get (2c)^{m+1} more relations per base size with the same number s of
linear-algebra columns. Gate: the relation count is that of the enlarged base {jP_i}, size 2cs, so supply (2cs)^{m+1}/p; but each relation costs a table-collision
search over the 2cs enlarged set (finder cost = table size), exactly the m=1 collision accounting (ECDLP-47/52: finder p^{1/2-1/(2m)} vs required p^{1/2-1/m}); LA columns s
shrink only by a factor c. Wall W2 (and it is a rediscovery of multiplicative coset bases of PKM 2016, already in the lab). **Killed paper, W2.**

**I3 — Canonical (torsion) p-adic lift cocycle.** Ordinary E has a canonical lift to Z_p; E(F_p)[r] lifts uniquely to r-torsion of E~(Z_p). The torsion section
differs from a naive coordinate lift by an explicit 2-cocycle, so delta(Q) = -(1/r) log(r Q-hat) mod p is computable in O(log r) and satisfies
delta(Q1+Q2) = delta(Q1)+delta(Q2)+c(Q1,Q2) with c low degree. Hope: a "pairing into F_p" that is a coboundary-twisted homomorphism. Gate: the log kills torsion; delta(kP)=k delta(P)+eps_k
where eps_k is the second p-adic digit of the naive lift of kP, a function with no algebraic dependence on k because k lives in Z/r and the target in F_p with r != p
(Smart's attack needs r = p). Reduction mod p^2 restricted to r-torsion is an isomorphism, so this is a re-coordinatisation of the same group. Walls W5 (all-or-nothing,
HYP-caa15771) and "arbitrary lifts carry no information" (HYP-f85d20a1). **Killed paper, W5.**

**I4 — Unreduced Tate/Miller cocycle into F_p^* (where subexponential DLP exists).** When r does not divide p-1 the reduced Tate pairing is trivial, but the normalised
Miller function Phi(R) = f_{r,P}(R) in F_p^* is a well-defined, non-trivial element (every R is a multiple of P; evaluated with dual-number regularisation). It is a
quasi-character Phi(R1+R2) = Phi(R1)Phi(R2) u(R1,R2) r-th powers, trivialised by psi = Phi^{1/r} (gcd(r,p-1)=1). Hope: log_g psi gives an additive F_p^*-index calculus handle
on k. Gate: not a homomorphism, so HYP-caa15771 does not apply literally; W3 applies (a function of the point). Paper analysis after the test (see Test B3): for every l | p-1
with l not dividing r, the class of Phi modulo l-th powers equals that of a function g_{rho,l} of degree rho+l (div = rho(P)+l(Q')-(rho+l)(O), rho = r mod l, lQ' = -rho P),
because the divisor r(P)-r(O) equals rho(P)-rho(O)+l*D'' with D'' ~ (Q')-(O). So all l-power-residue information is a LOW-DEGREE twisted character, i.e. the Weil/Sato-Tate
objects already in HYP-80158648; the rest of the information is l-th powers, carrying nothing about E(F_p). **Survived the paper gate as ill-posed (no wall named it), killed by test B.**
Tests (`expB_tate.py`, 4 curves p in 4519..7993, l=2,3): correctness check against brute-force linear-algebra f_{r,P} on 10 tiny curves 0 mismatches
(`check_miller.py`); balance, dependence on k mod m (m=2..16), Liouville, smoothness, k parity, best-cell predictor of [k>r/2]: no Bonferroni rejection in any of 8
(curve,l) cells; B5 |advantage| <= 0.019 (99% half-width 0.020-0.027 vs bar 2 r^{-1/4} ~ 0.21-0.24); planted 0.05 leak is detected (accuracy 0.54-0.56 on the
anti-correlation cell). Unplanned finding: max |F_a|^2/n ~ 3.9-4.1, far below the iid null median ~7.7-8 (flat Sato-Tate spectrum, variance ~1, edge 4). Post-hoc B3
(derived on paper after seeing it): chi_2(Phi(R)) = c * chi_2(tangent line at ((r-1)/2)P)(R), agreement 1.0 on 4564, 5554, 6314 and 8014 points (4 curves). So the "new" object
is, modulo squares, a degree-3 Legendre predicate (explained already). **Killed, W3 (reduces to known low-degree Weil law). Not a leak.**

**I5 — Elliptic-surface / Mordell-Weil lattice lift (height pairing as "size").** Embed E = E_{t0} in an elliptic surface over P^1 (rank up to 8, E8 lattice). Section
combinations n = sum n_i s_i vanish at t0 iff R_n(t0)=0, R_n a polynomial of degree q(n) (height); a relation is a short vector in the lattice of vanishing combinations,
an index-r sublattice, shortest vector ~ r^{1/rank}. Gate: the lattice is defined by the unknown logs x_i of the specialisations g_i = s_i(t0) = x_i P: finding it is a
multi-dimensional DLP (cost r^{1/2} by MITM, no lattice structure over F_p to search); at fixed t0 a vector hits with probability 1/p regardless of height (no metric on
F_p), and root-finding on R_n gives roots t0 for fixed n, not n for fixed t0. W2 + W3 (+ W5: specialisation is a homomorphism Z^rank -> Z/r). **Killed paper, W2/W5.**

**I6 — Z/r as a ring: units action and smoothness of labels (NFS-style).** End = Z[pi] acts on E(F_p) = O/(pi-1) = Z/r as a ring; units (Z/r)^* act simply transitively on
non-identity points; index calculus over "smooth labels" [q]P would need detecting smoothness of n from [n]P. Gate: needs a smoothness/size oracle on points (ECDLP-41 null,
confirmed again here by B4: z-scores of chi_l(Phi(kP)) with Liouville and with r^{1/3}-smooth indicators, max |z| 2.75 over 36 tests, no Bonferroni rejection); the multiplicative
structure helps only given a DH oracle (Maurer-Wolf type reductions, unverified recollection). Wall W3 + known-reduction. **Killed, W3.**

**I7 — Heegner/CM class-group link (ideals of O acting on the isogeny class).** Cl(O) acts on curves with End = O; hope to move (E,P,Q) to a nicer curve. Gate: the
action preserves #E, order, embedding degree, and k (isogeny invariance, `phi(Q) = k phi(P)`); round 19 measured reachability of j=0/1728 at ~2.5/sqrt(p) with gain <= sqrt 6.
W4. **Killed paper, W4.**

**I8 — Elliptic divisibility sequences / elliptic nets (theta "sizes").** psi_j(kP) = psi_{jk}(P)/psi_k(P)^{j^2}; rank-2 net W(a,b)=0 iff aP+bQ=O. Gate: forward
evaluation O(log index); inversion in the index is the DLP (recollection: Shipsey, Stange show EDS-DLP equivalent to ECDLP; unverified); values over F_p carry no metric, a
sequence W(a,.) is an explicit algebraic function of aP so any leakage is bounded by the same Weil sums. W3. **Killed paper, W3.**

**I9 — Weil restriction / trace descent to E(F_{p^n}) with subfield factor base.** Gate: E(F_p^n) contains E(F_p) as a direct summand up to small index, relations among
subfield points split componentwise; push-down only loses (Frontier F, ECDLP-53; Diem/Gaudry supply is for DLP in the larger group). W6. **Killed paper, W6.**

## Rho control
Same implementation (`rho_control.py`, r-adding walk, 16 branches, Floyd, counted group additions with 3 per step, 120 random Q per curve, 6 curves r = 911..12893):
cost ~ alpha sqrt(r) + gamma with alpha = 3.09, gamma = 1.88, R^2 = 0.985. Not an unbiased estimate of constants (Floyd, counted differently from earlier rounds) and no
I1-I9 algorithm exists to put against it; the comparison that matters here is the leakage bar. Bar at these sizes: advantage >~ 2 r^{-1/4} = 0.21-0.24; measured advantages <= 0.018.

## Ranked table (all ideas)
| # | Idea | Wall hit / survival | Test result |
|---|------|---------------------|-------------|
| 1 | I4 unreduced Tate/Miller cocycle into F_p^* (subexp-DLP target) | Survived paper gate (non-homomorphic); then W3: mod l-th powers collapses to a degree rho+l function | Null on all leak statistics (8 cells); unplanned flat Sato-Tate spectrum explained exactly (chi_2 Phi = c chi_2(line) on 100% of 4 curves); the one idea that ran fully |
| 2 | I6 smooth-label / ring-of-units NFS analogy | W3 (smoothness oracle), known DH-oracle reduction | B4 correlations with Liouville and r^{1/3}-smoothness null (|z| <= 2.75 of 36) |
| 3 | I1 RR / L(D) with poles in base | W1 identical supply (Pic^0 = E) | obs/pred 0.90-1.00, never excess (24 cells) |
| 4 | I2 weighted divisors | W2 finder = table over enlarged base (PKM coset bases) | paper only |
| 5 | I5 MW lattice / height pairing | W2 (lattice defined by unknown logs) + W5 | paper only |
| 6 | I3 canonical p-adic lift cocycle | W5 (isomorphism on r-torsion; r != p) | paper only |
| 7 | I8 EDS / elliptic nets | W3, equivalent to ECDLP (recollection unverified) | paper only |
| 8 | I7 Heegner / CM class group | W4 isogeny invariance | paper only |
| 9 | I9 Weil restriction subfield base | W6 | paper only |

## Claims, limits, verification
Experiment-level only. I4 test was a distinguisher test: it found no k-leak at r ~ 4.5e3..8e3 (small sizes, 4 curves; bar 0.2 means these sizes cannot see leaks below ~0.02 per 99% CI,
which is the lab's convention: the bar to beat rho at 2^28 is ~0.055). The l=2 line reduction is checked numerically; the general-l statement is a paper derivation, not
numerically checked for l=3 and not reviewed. Protocol hash c52f4679da1c70144ef09ae5735b3a8de398c57f87b85e1032aad0723194d2cc (registered 2026-11-03T18:18:25Z, before any measurement except check_miller.py,
which ran after the freeze as a correctness check and passed on the first run; the protocol permitted it as a pilot). Process deviations: the protocol's rho paragraph was left unfinished (formula sentence abandoned);
the addendum (hash 6c943ec8...) was written after expB2_diag and expB3 ran, labelled post-hoc. Rho Floyd cost units differ from earlier rounds.
No independent review; same-provider only.

## Outcome and next action
All nine ideas are closed. The only new fact worth recording: modulo l-th powers (l | p-1, l not dividing r) the unreduced Tate/Miller function is a low-degree twisted character, so
"unreduced pairing into F_p^*" cannot supply more than the Sato-Tate/Weil objects already ledgered. Suggested ledger note for the PI: attach the line-reduction to HYP-80158648 as an
explanation of why chi_2 of the degree-r Miller function shows the same flat spectrum. Next action if anyone continues: nothing from this list needs further test; the nine mechanisms
all route into walls W1-W6.
