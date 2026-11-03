# ECDLP backlog

Task keys via `research/ecdlp/TASKS.json`; status via `scripts/research.py task`.

## Completed (2026-11-03)
- ECDLP-2/3/4 — round-1 independent investigations (non-generic information, universal
  transformations, complexity barriers).
- ECDLP-5 — counterexample attempts (H1 refuted application, H2 survived, H3 flawed, H4 ill-posed).
- ECDLP-6 — Lean transfer-barrier lemmas (PRF-af19eaae; REV-16b2db9b accept).
- ECDLP-7 — near-character / predicate-bias experiments (inconclusive; anomaly found).
- ECDLP-8 — character-sum theory of the anomaly.  ECDLP-9 — decisive scaling test.
- ECDLP-10 — Lean SLP/trace bounds (PRF-613be647; REV-0971d96d accept).
- ECDLP-11 — geometric mechanism (Prym / E[2]-Heisenberg).  ECDLP-12 — prime-field factor bases.

- ECDLP-13 — factor-base frontier (PKM 2016 precedence; no m=2 advantage).
- ECDLP-14 — intermediate-target ladder; Theorems A/A′/B (proof attempts).
- ECDLP-15 — cover-transfer regime analysis (negative, with missing ingredient).

- ECDLP-16 — m=3 relation-solving cost (negative).  ECDLP-17 — blind review of A/A′/B.
- ECDLP-18 — genus-2 cover decisive test (negative).  ECDLP-19 — conditional Lean Theorem B.

- ECDLP-20 — unconditional Lean Theorem B.  ECDLP-21 — partial-agreement bounds (proof attempt).
- ECDLP-22 — novelty (A known in kind) and hypotheses D1–D5.

- ECDLP-23 — blind review of partial-agreement bounds (part (2) transcription refuted, corrected).
- ECDLP-24 — weak-family classification + D3 lemma.  ECDLP-25 — Lean Theorem C.

- ECDLP-26 — review of Theorem C (accept).  ECDLP-27 — Lean partial-agreement part (2).

## Active
- ECDLP-1 — umbrella vertical slice (lifecycle executed; SQLite/event memory, blind-packet
  tooling, C17 harness not implemented — deferred per user priority on research).

## Strategic correction (user directive, see latest DEC)
Primary objective: a working algorithm beating generic √r. Allocation 60% algorithm invention and
implementation (algorithm-inventor), 20% falsification/scaling benchmarks vs Pollard rho, 10% directly
relevant proofs, 10% literature/publication. No new interpolation lower-bound variants unless they
unblock an active candidate. The barrier map is used to aim inventions (escape every listed assumption).

## Next candidates (prioritized by significance × falsifiability ÷ cost)
1. Independent review of PartialAgreement.lean (PRF for ECDLP-27). Human/library access needed
   for novelty (Lange–Winterhof LNCS 2387 pp. 137–143, LNCS 2643 pp. 51–60).
2. Research frontier assessment: all investigated routes to sub-√p universal ECDLP are closed or
   negative at toy sizes; consider a reviewed barrier-map write-up (PAP draft, no publication
   without human approval).
3. Unconventional: non-elimination decomposition (lattice / small-root) for structured factor
   bases; quantum-free "representation change" ideas — require a cheap decisive test first.
(Done/negative: prime-field summation polynomials m ≤ 3; genus-2 covers.)
2. Formal/proof: HYP-4bd8d89a sharper trace bound; HYP-f85d20a1 lift uniformity; reviewed proof of
   |Y| ≤ 2 for g = x and the E[2] reduction for g = y (HYP-80158648).
3. Cover-based transfers (B8 genus/dimension trade-off): make the heuristic regime analysis rigorous.
4. Approximate characters (HYP-130de9b1): re-run with pre-registered symmetry-aware null, larger family.
5. Pose better intermediate targets (e.g., O(n log n) *group operations*; amortized/preprocessing
   settings; restricted families) as precise HYPs with known lower bounds attached.
6. Infrastructure blockers (recorded, not pursued): remote task claims need push permission for
   `claims/*`; subagent runtime model identity not exposed; independence only instructed.
