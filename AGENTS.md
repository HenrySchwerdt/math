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

## Current mission and Claude handoff

The primary project is ECDLP. Read docs/CLAUDE_START.md, docs/LAB_MISSION.md
(the full current user mission) and docs/LAB_PROTOCOL.md before choosing work.
Preserve research/integer-factorization as a separate project. Bootstrap is
complete enough for handoff; the full laboratory remains to be implemented.
Use all current scientific roles from docs/ROLES.md with bounded native agents
when available, otherwise explicitly record sequential fallback and missing
independence. Never infer live integration, proof or approval from config files.

## CLI-driven task reporting

Task keys are persisted per project (e.g. ECDLP-1); canonical UUIDs remain unchanged.
Use `scripts/research.py task PROJECT KEY --run RUN-ID --status STATUS --reason REASON`
for progress updates and `exec` for recorded command steps. These feed the public
board and task history directly. Do not maintain a second status list in website
files. Commits to main automatically regenerate and deploy the public notebook.
Task status and outcomes never change mathematical proof status automatically.
