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

## Active
- ECDLP-1 — umbrella vertical slice (lifecycle executed; SQLite/event memory, blind-packet
  tooling, C17 harness not implemented — deferred per user priority on research).

## Next candidates (prioritized by significance × falsifiability ÷ cost)
1. Prime-field factor bases (HYP-db508348): extend whatever ECDLP-12 finds; literature check of
   Semaev/Petit–Kosters–Messeng prime-field results (sources not yet verified).
2. Formal/proof: HYP-4bd8d89a sharper trace bound; HYP-f85d20a1 lift uniformity; reviewed proof of
   |Y| ≤ 2 for g = x and the E[2] reduction for g = y (HYP-80158648).
3. Cover-based transfers (B8 genus/dimension trade-off): make the heuristic regime analysis rigorous.
4. Approximate characters (HYP-130de9b1): re-run with pre-registered symmetry-aware null, larger family.
5. Pose better intermediate targets (e.g., O(n log n) *group operations*; amortized/preprocessing
   settings; restricted families) as precise HYPs with known lower bounds attached.
6. Infrastructure blockers (recorded, not pursued): remote task claims need push permission for
   `claims/*`; subagent runtime model identity not exposed; independence only instructed.
