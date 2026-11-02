# Shared research instructions

Read `docs/METHODOLOGY.md`, `docs/HANDOFF.md`, and `docs/ROLES.md` before work.
Select a project under `research/`; read its STATUS.md, BACKLOG.md, latest runs,
reviews, decisions and unresolved hypotheses. Repository files are the source of truth.
Use `docs/BOOTSTRAP.md` for the first session with either provider.

The PI uses GPT-6.1 Sol in Codex or Claude Opus 5.5 in Claude Code. Workers,
implementers, experimenters and adversarial critics use GPT-6 Luna or Claude
Sonnet 5.5 respectively. Final integration review uses the PI model.
Verify actual model identity from runtime metadata; do not silently substitute.

Do not launch research workers during bootstrap. Later delegation requires a stable
TSK identifier, RUN record, remote claim, bounded budget and isolated worktree or
explicit non-overlapping file ownership. You are not alone in the repository:
do not revert others' edits. Workers never edit shared status or final results.

Use Lean 4 for formal mathematics; read docs/LEAN.md and build the pinned project.
Formal correctness and bit-complexity require distinct exact statements and evidence.

Capture meaningful activities with `scripts/research.py`, preserve evidence,
record failures and distinguish empirical evidence, proof attempts and formal proof.
Run validation and independent integration review before publishing final claims.
Never fabricate execution, review, source, timestamp or proof evidence. Mark
unavailable information with null plus an explanation, not an invented value.
Do not commit credentials, personal paths or unbounded transcripts.

Finish with an actionable handoff and ledger updates. Commit and push when
explicitly authorized; the initial bootstrap request authorizes its own push.
No public forum posting is part of research task execution unless separately requested.
