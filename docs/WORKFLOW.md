# Package workflow (orchestrator protocol)

A research *package* is everything on the research branch since `origin/main` that is proposed as
one pull request. Follow this loop so no progress is lost and CI runs only once per package.

| Step | Command / action |
| --- | --- |
| 1. Start bounded work | `python scripts/research.py start <project> --title … --question … --role … --model …` |
| 2. While agents run, no PR open | `python scripts/research.py snapshot "<msg>"` (WIP commit + push; no CI because no PR is open) |
| 3. While a PR is open | `python scripts/research.py snapshot "<msg>" --no-push` (pushing would restart the PR's CI) |
| 4. Integrate a finished run | reproduce evidence via `exec`, commit the work, then `python scripts/research.py finish <project> <RUN> --outcome … --reason …`, commit |
| 5. Close the package | `python scripts/research.py package-check --lean` (validates committed HEAD in a clean worktree) |
| 6. PR text | `python scripts/research.py package-summary` → paste into the PR body (add highlights and limitations) |
| 7. Open PR | push, then create the PR with the orchestrator's GitHub tool; subscribe to its activity |
| 8. CI red | fix the cause (never skip tests), re-run `package-check`, push the fix only |
| 9. CI green | merge the PR with the GitHub tool, passing the **exact** head SHA from `git rev-parse HEAD` / `git ls-remote` |
| 10. After merge | `python scripts/research.py sync-main`, then push; continue at step 1 |

Rules: CI runs only for PRs into `main` and pushes to `main` (see `.github/workflows`). Never
rebase research history (ledger records reference commit hashes). Commit attribution lines can be
supplied for `snapshot` via the environment variable `RESEARCH_COMMIT_TRAILER` (use `\n` for
newlines). Merging publishes the public notebook; merge only reviewed, validated packages.
