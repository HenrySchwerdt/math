# Ledger metadata and evidence contract

`research/_templates/artifact.schema.json` is JSON Schema 2020-12. Each artifact
is `<directory>/<TYPE-UUID4>.json` with an adjacent `.md` report. `new` creates a
draft; complete fields before execution and again at completion. `check` checks
schema, UUID/type, unique IDs, local references, paths, reports, timestamps and
completed-run commits. It cannot certify mathematical truth or audit arbitrary
shell actions. Drafts explicitly say unassigned/not recorded, never successful.

Common fields: id, type, title, UTC created_at, status, exact question, rationale,
assumptions, sources (title/URL/retrieval/locator), refs (artifact IDs), evidence
(repository-relative paths), claims, proof_status, outcome, next_action, notes.
TSK adds success_criteria, owned_files, resource_limit. RUN adds start/completion,
provider/model/role, task, hypothesis inputs, starting/resulting commits,
branch/worktree (portable logical name), commands (evidence files), files_changed,
tests, benchmark methodology or not-applicable rationale, machine and reviews.
Null commit is permitted only with an explicit explanation, e.g. unborn repository
or unfinished run. Commit a completed run's resulting hash in a later ledger commit.

REV adds reviewer run ID, exact target commit/artifacts, neutral initial packet,
counterexamples, complexity, limitations, decision and rationale. Formal results
add exact Lean file/declaration, toolchain file, build evidence and source commit.
The validator enforces presence and paths; human review must establish that build
evidence matches the exact theorem and successful execution.

`audit` lists records chronologically. `audit PROJECT --hypothesis HYP-ID` follows
refs, run inputs/tasks/reviews and review targets transitively, showing the claim's
linked attempts, failures, reviews and decisions. Read adjacent reports/evidence
for why tasks were chosen and what commands established. Do not treat a summary
as a substitute for evidence.
