# ECDLP — primary project

Primary mission: `docs/LAB_MISSION.md`. Open target: `HYP-2de84d42-f26b-45c1-ae82-7ffb4a404b61`
(universal classical ECDLP, worst-case O(n log n) bit operations, n = total input length).
Status of the target: **open, unproved; no evidence for or against existence.** Nothing below
improves on known ECDLP complexity.

## Laboratory state (session 2026-11-03, Claude PI, branch claude/exciting-mccarthy-yljzor)

Research cycle executed with real bounded subagents (Claude Code Agent tool; adapters select
claude-sonnet-5-5, independent reviewer claude-opus-5-5; identities are configured +
self-reported, not runtime-verified). PI log: `runs/RUN-62dbda7c-…`. Remote claim refs were
not pushed (session push scope) — see `decisions/DEC-b38432b9-…`.

Lean: `lake build` passes (pinned Lean 4.35.0 / Mathlib 56a00585, no warnings).
`MathResearch/ECDLP/Basic.lean` (exact DLP relation), `Transfer.lean` (transfer barriers;
PRF-af19eaae, REV-16b2db9b accept), `Barriers.lean` (SLP and trace bounds; PRF-613be647,
REV-0971d96d accept). Reviewers are same-provider (Opus): independence is partial.

## Findings by evidence level

Formally verified (Lean + independent correspondence review; all elementary, not novel):
- HYP-caa15771 — homomorphic transfer of a prime-order subgroup is all-or-nothing; nonzero
  image forces r | |target|; coprime target gives zero. Guardrail for all transfer ideas.
- HYP-57d71f43 — addition/subtraction SLP values are n•P with |n| ≤ 2^length; some Q needs
  length ≳ log₂ r (Barriers.lean; PRF-613be647, REV-0971d96d). Black-box model only.
- HYP-eff2cfbb — at most M(M+1) traces t have a prime r > 4√q | q+1−t with embedding degree
  ≤ M (any q ≥ 2; trace-level only, no curve-count weighting).

Refuted / flawed (kept permanently, with corrected variants recorded separately):
- HYP-49fb2746 — "Frobenius-equivariance unifies MOV and anomalous attacks": abstract lemma
  true but trivial; the application is vacuous (pairing functionals with non-rational R are not
  q-Galois-equivariant; toy computations). ECDLP-5.
- HYP-650069e0 — SLP counting barrier: exact-vs-≤ length gap; strictly weaker than the trivial
  coefficient bound (HYP-57d71f43); bit-cost corollary model-dependent.
- HYP-333ce3c5 — "arbitrary lifts carry no information": ill-posed quantifier; exact variant
  HYP-f85d20a1 (uniform on F_p^2 for independent lifts).

Survived falsification (unproved): sharper trace bound HYP-4bd8d89a; prime-field small-x
factor bases do not beat √p at toy sizes 2^12..2^18 (HYP-db508348, ECDLP-12; best 15.7·√p;
end-to-end toy index calculus correct but 40–52·√p).

Reproducible experimental findings (toy sizes, two seeds + PI bit-identical reruns):
- No near-character among 40 low-complexity coordinate functions (HYP-130de9b1; Fourier
  null was mis-specified, post-hoc correction → 0 rejections).
- Legendre predicates χ(x([k]P)), χ(y([k]P)) show no dependence on k mod m, but a
  non-random spectral law (HYP-e1959734 not supported as stated). Explained: twisted sums
  over E(F_p) are Weil-bounded with Sato–Tate-like moments (1, 2, 5) for g = x, x+1, y and
  Gaussian-like for higher-degree g (HYP-242da418 → sharpened HYP-80158648). Equidistribution
  behaviour, **not** a discrete-log leak. Mechanism (ECDLP-11, exact
  toy checks): for g = x the sums are Frobenius traces on the rank-2 Prym piece
  E'': Y² = X³ + aX² + b² of the genus-2 cover w² = x (det = p exactly ⇒ |Y| ≤ 2); for g = y an
  E[2]-Heisenberg reduction gives an effective rank 2 (derivation sketch, unproved step).
  Equidistribution as p → ∞ remains conjectural.

Round 5 (package 2; proof attempts and negative results, unreviewed unless stated):
- Restricted-model lower bounds (HYP-5a550ab6, HYP-eda6732a; proof attempts, PI checked the
  core argument of A; novelty vs Lange–Winterhof unchecked): any rational function f on E with
  f(kP) = k mod p for k ≤ N has pole order ≥ (N−1)/2; algebraic straight-line programs over F_q
  computing k need ≥ log₂((N−1)/12) field operations; x-only polynomial for k² has degree ≥ (r−5)/6.
- Cover transfers (HYP-ad5bc0e3): with known Jacobian index-calculus algorithms no genus regime
  beats √p for prime-field E (fixed-g part proved from cited theorems; large-g part conditional;
  intermediate regime heuristic). Missing ingredient: a √p-small factor base adapted to π*E(F_p).
- Prime-field factor bases (HYP-db508348): Petit–Kosters–Messeng 2016 already proposes
  structured (multiplicative-coset, isogeny-coset) bases; at m = 2 they give no yield advantage
  on toy curves; the open quantity is the relation-system solving cost at m ≥ 3.
- Target statement needs a fixed output convention (least k vs any k) — noted on HYP-2de84d42.

Round 6 (package 3):
- Theorem A (HYP-5a550ab6): blind adversarial review found a proof gap (p | r, e.g. p = 5, r = 10;
  PI-verified); bounds survive with corrected proof via pole-set invariance — HYP-adb581ff (reviewed).
- Theorem B (HYP-eda6732a): reviewed correct; CONDITIONAL Lean proof (Interpolation.lean,
  PRF-a6cf1e66, REV-08014e33 accept): r ≤ 6·deg g + 5 given the x-addition identities and
  injectivity as hypotheses (not yet derived from Mathlib's curve group law).
- Prime-field summation-polynomial index calculus at m = 3 (ECDLP-16): per-relation cost
  T < p^{1/6} not achieved; linear algebra 3p^{2/3} already exceeds √p for |V| = p^{1/3}.
  Small-x, PKM-coset and random bases indistinguishable. Route deprioritized (toy evidence).
- Genus-2 cover index calculus (ECDLP-18): implemented end to end (12/12 correct) but costs
  ~p^{2.5} total (~p Cantor operations), far above √p; pullback-only relations carry no
  information. HYP-ad5bc0e3 survives on p ≤ 2^14.

Round 7 (package 4):
- Theorem B is now UNCONDITIONALLY formally verified (CurveX.lean, PRF-34538f75, REV-1f44f52b accept):
  for a short Weierstrass curve over a field with 2, 3 ≠ 0 and P of odd order r, any g with
  g(x(kP)) = k² for 1 ≤ k ≤ (r−1)/2 has r ≤ 6·deg g + 5. Elementary; novelty unsettled.
- Theorem A is known in kind (Lange–Winterhof COCOON 2002; Satoh WCC 2005) — not claimed new.
- Partial-agreement bounds (HYP-5da6025e, proof attempt): agreement on a δ-fraction of k ≤ N
  forces deg f ≥ δ²N/4 (rational f); unreviewed.
- New speculative hypotheses D1–D5 (RUN-73ace464); D1 (no low-degree x-orbit invariants) null.

Round 8 (package 5):
- Theorem C (formally verified, LinearInterp.lean): x-only g with g(x(kP)) = k for 1 ≤ k ≤ N,
  2N < r, has N ≤ 3·deg g + 2. Independent review pending; not claimed novel.
- Partial-agreement bounds: blind review found the PI's transcription of part (2) false
  (dropped N ≤ (r−1)/2; counterexample y² = x³ + 5 over F₇, PI-verified). Original kept as refuted;
  corrected statement HYP (reviewed). PI process error recorded.
- Weak-family map (ECDLP-24): sourced classification; residual hard class = prime-order,
  non-anomalous, large-embedding-degree curves over prime fields (no known o(√p) algorithm).
  D3 lemma: non-scalar elements of Z[π] have norm ≥ |t²−4p|/4.

Round 9 (package 6):
- Theorem C independently reviewed (REV-6c9bfbc1 accept); probably not novel.
- Partial-agreement part (2) formally verified (PartialAgreement.lean): S_j ≤ 3·deg g for g with
  g(x(kP)) = k² on A ⊆ [1, N], 2N < r (extra hypothesis deg g ≥ 1 or char ∤ j over general
  fields; automatic over F_p). Independent review pending.

Formal layer summary (MathResearch/ECDLP, lake build 3165 jobs, standard axioms only):
Basic (DLP relation), Transfer (transfer barriers), Barriers (SLP, trace bounds),
Interpolation + CurveX (Theorem B), LinearInterp (Theorem C), PartialAgreement.

Barrier context (literature-level, agents' reports RUN-9eae1ad9, RUN-fec2442f, RUN-b0ccd1bd):
O(n log n) is below the best-known cost O(n² log n) of verifying a candidate by scalar
multiplication (not a lower bound). Generic bounds (Shoup/Maurer/Nechaev) constrain only
encoding-blind algorithms; every known non-generic transfer needs a family-specific arithmetic
coincidence (embedding degree, #E = p, extension-field descent).

Rounds 11–12 (package 8, algorithms-first allocation per strategic-correction DEC):
- Algorithm inventors, all benchmarked against rho with pre-registered protocols, all NEGATIVE
  (no exponent below 1/2; PI reproduced every analysis via exec):
  A (ECDLP-42) Farey-height index calculus 29–43× slower than rho at 24 bits; LLL decomposition
  0 hits; Mordell lift coverage ≤ 1e-3. B (ECDLP-43) automorphism-orbit rho and 2-isogeny volcano
  ascent: constant factors only (known). C (ECDLP-44) negation rho, precomputation tables
  (S·T² ≈ N) and multi-instance batching (√M): known generic tradeoffs reproduced.
- ETH-refutation technique (external openai/math family 378, ECDLP-46): cannot beat rho via CNF
  (n ≥ ~ℓ^2.4 variables) or sparse-polynomial routes (x(kP) bits have ANF density ~0.5).
- Frontier E (ECDLP-41): integer-structure distinguishers (carries, bits, sorted neighbours) null;
  unreviewed remarks that order/bit access is free in Shoup's model and that decision-tree
  arithmetic length is vacuous without size accounting (bears on HYP-dbe79a50 interpretation).
- Theorem E (ECDLP-38): cusp degeneration + Schwartz–Zippel gives mindeg(N) = N−1 off |Z| ≤ w_N p²
  valid triples (w_N ~ N⁴/3); blind review REV-3b9427bd: bound holds, statement corrected
  (HYP-a4caa1de, reviewed, not formalized).

Round 13 (package 9):
- Inventor D (ECDLP-47): algebraic relation finding (S_3 decomposition over a PKM multiplicative-coset
  factor base, Gröbner cross-check) is correct (65/65) but total cost ~p (exponent 0.99), 633× rho at
  24 bits. Obstacle: finder cost ≥ p^{1/2−1/(2m)} per relation vs required < p^{1/2−1/m}.
- E0/E3 review (ECDLP-48, REV): both remarks hold only in narrower form; Theorem DT (equality-only,
  charged constants) unaffected; with order comparisons only size/depth matter; E0 corollary is a
  restatement of non-genericity.
- Framework: `research.py render-md` fills template reports from JSON (also run by `finish`);
  `start` expands short IDs.

Round 14 (package 10):
- Inventor E (ECDLP-49): for m=2 index calculus the relation supply alone forces cost ≥ 1.22√p even
  with a free finder (closed S_3 triples in a base of size s ≈ 2s³/(3p), measured within 2%); the
  decomposition curve is genus 1 (the group law itself); parametrised bases of size √p have genus
  ~3p–4p; isogeny/CM orbits give no useful relations. Only m ≥ 3 (S_4) remains in this family.
- Technical report v2 (PAP-ef6e2010, internal, NOT submitted): 14 pages; re-review decision revise
  (wording only), all fixes applied; stale Theorem E N=3 evidence regenerated (0 violations).

Round 15 (package 11):
- Inventor F (ECDLP-52): m=3 index calculus: supply floor s ≥ (3r)^{1/3} (observed/predicted
  closure 0.99–1.01 on six structured and random base families: x-structure gives no excess closure);
  best finder total ≈ 1.5 r^{2/3} (exponent 0.651), 36× rho at 30 bits.
- Frontier F (ECDLP-53): ambient groups (base change, cover Jacobians, Frey–Kani gluing, generalized
  Jacobians) only lose relations on push-down; they can at most make finding cheaper.
- Checkpoint DEC: index calculus closed on generic prime-order prime-field curves at toy scale;
  further constructive rounds only for mechanisms passing the supply/finder accounting on paper.

Round 16 (package 12, user directive "give everything"):
- Frontier G (ECDLP-54): automated evolutionary discovery (19-op DSL with comparisons, bits, hash
  table) rediscovers rho; the champion fits 1.77√r + 136, identical to hand rho; its apparent
  exponent 0.32–0.38 is setup amortisation. Lesson: fit α√r + γ, never naive log-log at r ≤ 2^16.
- Inventor G (ECDLP-55): excess group closure exists only for unions of lines (rank ≈ s/6, PI
  derivation) and log-space progressions (need logs).
- Inventor H (ECDLP-56): fixed-curve precomputation with sorted tables, comparison trees or tuned
  walks stays on S·T² ≈ r; comparison features predict k at chance level (planted leak detected).

## Next

Every generic-model route tested reproduces √r. Remaining levers are non-generic structure
(CM/automorphism families, isogeny distance to structured curves) and reviewing the E0/E3
remarks. See BACKLOG.md. Factorization remains a separate preserved project.
