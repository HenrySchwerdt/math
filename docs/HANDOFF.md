# Cross-provider handoff

## Start (either provider)

1. Read AGENTS.md, METHODOLOGY.md, this file and the selected project STATUS.md.
2. Read BACKLOG.md and unfinished/blocked TSK records, their claims and blockers.
3. Run `python scripts/research.py audit <project>`; inspect recent RUN reports,
   evidence, referenced commits (`git show <commit>`) and REV/DEC dispositions.
4. Inspect unresolved hypotheses, rejected approaches and source assumptions.
   Check remote claims with `git ls-remote origin 'refs/heads/claims/*'`.
5. Choose a bounded new or resumable task. Record why it was selected and its
   success criteria; do not duplicate completed/refuted work.
6. Start a RUN, claim the TSK remotely, assign ownership and budget; then execute.

## Finish (either provider)

1. Reconcile workers, exit codes, incomplete evidence and independent reviews.
2. Finalize RUN JSON and report, linking results and negative findings to evidence.
3. Integrate reviewed changes only; update hypotheses, decisions, STATUS.md and
   BACKLOG.md. State exactly what is established and what is unresolved.
4. In STATUS.md write the next task ID, exact first command/question, required
   inputs, blockers, failed approaches and remaining verification. Anyone with
   only the repository must be able to continue.
5. Run validation, inspect diff, commit when authorized. Set each completed RUN's
   resulting_commit to the implementation/evidence commit; a later ledger commit
   records that hash (a commit cannot contain its own hash). Then push authorized
   verified updates. Never claim a failed push succeeded.
6. Release remote claims only after evidence and handoff are pushed. Leave blocked
   work with an explicit owner handoff; coordinate takeover, never steal a claim.

Private CLI resume/history may help locally but must never be required. If a
session dies, use the claim commit and open RUN as the recovery entry point.
