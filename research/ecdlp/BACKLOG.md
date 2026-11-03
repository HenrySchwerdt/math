# ECDLP backlog

Task keys via `research/ecdlp/TASKS.json`; status via `scripts/research.py task`.

## Completed (2026-11-03)
- ECDLP-2/3/4 — round-1 independent investigations (non-generic information, universal
  transformations, complexity barriers).
- ECDLP-5 — counterexample attempts (H1 refuted application, H2 survived, H3 flawed, H4 ill-posed).
- ECDLP-6 — Lean transfer-barrier lemmas (PRF-af19eaae; REV-16b2db9b accept).
- ECDLP-7 — near-character / predicate-bias experiments (inconclusive; anomaly found).
- ECDLP-8 — character-sum theory of the anomaly.  ECDLP-9 — decisive scaling test.

## Active
- ECDLP-1 — umbrella vertical slice (lifecycle executed; SQLite/event memory, blind-packet
  tooling, C17 harness not implemented — deferred per user priority on research).
- ECDLP-10/11/12 — round 4 (see STATUS.md).

## Next candidates (prioritized by significance × falsifiability ÷ cost)
1. Prime-field factor bases (HYP-db508348): extend whatever ECDLP-12 finds; literature check of
   Semaev/Petit–Kosters–Messeng prime-field results (sources not yet verified).
2. Formal: HYP-eff2cfbb / HYP-4bd8d89a trace bounds; HYP-57d71f43 SLP bound; prove HYP-f85d20a1.
3. Cover-based transfers (B8 genus/dimension trade-off): make the heuristic regime analysis rigorous.
4. Approximate characters (HYP-130de9b1): re-run with pre-registered symmetry-aware null, larger family.
5. Pose better intermediate targets (e.g., O(n log n) *group operations*; amortized/preprocessing
   settings; restricted families) as precise HYPs with known lower bounds attached.
6. Infrastructure blockers (recorded, not pursued): remote task claims need push permission for
   `claims/*`; subagent runtime model identity not exposed; independence only instructed.
