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

## Next

See BACKLOG.md. Factorization remains a separate preserved project.
