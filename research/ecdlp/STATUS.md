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

Barrier context (literature-level, agents' reports RUN-9eae1ad9, RUN-fec2442f, RUN-b0ccd1bd):
O(n log n) is below the best-known cost O(n² log n) of verifying a candidate by scalar
multiplication (not a lower bound). Generic bounds (Shoup/Maurer/Nechaev) constrain only
encoding-blind algorithms; every known non-generic transfer needs a family-specific arithmetic
coincidence (embedding degree, #E = p, extension-field descent).

## Next

See BACKLOG.md. Factorization remains a separate preserved project.
