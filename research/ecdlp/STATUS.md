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
`MathResearch/ECDLP/Basic.lean` (exact DLP relation) and `Transfer.lean` (transfer-barrier
lemmas) — PRF-af19eaae, independently reviewed (REV-16b2db9b: accept). Elementary, not novel.

## Findings by evidence level

Formally verified (Lean + independent correspondence review):
- HYP-caa15771 — homomorphic transfer of a prime-order subgroup is all-or-nothing; nonzero
  image forces r | |target|; coprime target gives zero. Guardrail for all transfer ideas.

Refuted / flawed (kept permanently, with corrected variants recorded separately):
- HYP-49fb2746 — "Frobenius-equivariance unifies MOV and anomalous attacks": abstract lemma
  true but trivial; the application is vacuous (pairing functionals with non-rational R are not
  q-Galois-equivariant; toy computations). ECDLP-5.
- HYP-650069e0 — SLP counting barrier: exact-vs-≤ length gap; strictly weaker than the trivial
  coefficient bound (HYP-57d71f43); bit-cost corollary model-dependent.
- HYP-333ce3c5 — "arbitrary lifts carry no information": ill-posed quantifier; exact variant
  HYP-f85d20a1 (uniform on F_p^2 for independent lifts).

Survived falsification (proof checked informally, not yet formal/reviewed):
- HYP-eff2cfbb — at most M(M+1) traces with a prime r > 4√q of embedding degree ≤ M
  (all prime powers q ≤ 150000, M ≤ 12). Sharper variant HYP-4bd8d89a unproved.

Reproducible experimental findings (toy sizes, two seeds + PI bit-identical reruns):
- No near-character among 40 low-complexity coordinate functions (HYP-130de9b1; Fourier
  null was mis-specified, post-hoc correction → 0 rejections).
- Legendre predicates χ(x([k]P)), χ(y([k]P)) show no dependence on k mod m, but a
  non-random spectral law (HYP-e1959734 not supported as stated). Explained: twisted sums
  over E(F_p) are Weil-bounded with Sato–Tate-like moments (1, 2, 5) for g = x, x+1, y and
  Gaussian-like for higher-degree g (HYP-242da418 → sharpened HYP-80158648). Equidistribution
  behaviour, **not** a discrete-log leak. Open puzzle: g = y (ramified support 4) is SU(2)-like.

Barrier context (literature-level, agents' reports RUN-9eae1ad9, RUN-fec2442f, RUN-b0ccd1bd):
O(n log n) is below the best-known cost O(n² log n) of verifying a candidate by scalar
multiplication (not a lower bound). Generic bounds (Shoup/Maurer/Nechaev) constrain only
encoding-blind algorithms; every known non-generic transfer needs a family-specific arithmetic
coincidence (embedding degree, #E = p, extension-field descent).

## In progress / next

Round 4: ECDLP-10 (Lean: SLP coefficient bound, trace bound), ECDLP-11 (geometry of the
Sato–Tate law), ECDLP-12 (prime-field small-x factor-base relation yield, HYP-db508348).
See BACKLOG.md. Factorization remains a separate preserved project.
