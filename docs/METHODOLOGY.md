# Shared mathematical research protocol

## Durable state

All projects use `research/<slug>/`. STATUS.md gives current conclusions and
next-session instructions; BACKLOG.md indexes stable TSK records. JSON metadata
is authoritative for identifiers and links; adjacent Markdown explains reasoning.
Artifact names use TYPE-UUID4 (globally unique across projects and worktrees).
Never rename/reuse an ID. Types: TSK, HYP, EXP, ALG, PRF, REV, RUN, DEC, PAP.
Use explicit `refs` for the hypothesis-centered graph. No unrecorded conversation,
auto-memory or provider session is necessary to resume work.

## Session and task execution

Follow HANDOFF.md at both boundaries. Create a RUN before meaningful work;
record actual UTC times and runtime provider/model/role. Create a TSK with exact
question, rationale, inputs, assumptions, sources, scope and success criteria.
Claim it remotely before execution; use CONCURRENCY.md. Never treat an old
claim as expired merely because it is quiet. Assign each worker its own RUN.

Every result records claims, assumptions, evidence, proof status, limitations,
outcome and next action. Link sources by title, URL/DOI, retrieval date and
relevant section; attach small redistributable supporting artifacts when lawful.
Unknown provenance is null with an explanation in `notes`. A completed run must
record commands actually executed, files changed, tests, commits, machine and
benchmark methodology (or explicit not-applicable rationale), reviews and outcome.
Bootstrap commands before the logger existed must be identified as retrospective;
never claim complete raw capture for them.

Use `python scripts/research.py exec <project> <RUN-id> -- <argv...>` for bounded,
non-secret reproducible commands. It preserves argv, UTC times, exit code and
bounded sanitized output. It is not a sandbox or a universal secret detector:
inspect evidence before committing. Avoid tokens in arguments and never capture
unbounded interactive transcripts. Record manual/tool observations as such.

## Evidence and proof

States: not-applicable, unproved, experimental, proof-attempt, reviewed,
formally-verified, refuted. Finite experiments support only their tested domain.
State quantifiers and assumptions explicitly. Complexity arguments require a
cost model and derivation independent of timing. Benchmarks require machine,
OS, tool versions, inputs/seeds, baseline, repeats, statistic and resource limits.
No benchmark occurred merely because a template contains methodology fields.

A formally-verified result must link an exact Lean statement/file and declaration,
pinned Lean toolchain, successful reproducible build command/output, and source
commit. Lean 4 is the required formal proof environment; see LEAN.md for the pinned project and build protocol. Model review is
never a proof certificate. Follow REVIEW.md before shared/final integration.

## Publication and integrity

Keep paper drafts under papers with PAP records linking every substantive claim
to HYP/PRF/EXP and review records. Log decisions and rejected/unsuccessful paths.
Do not erase contradictory findings. Use a DEC for rationale and disposition.
Secrets, private identities, absolute home paths and raw provider histories do
not belong in Git. Run validation and inspect the diff before authorized push.
