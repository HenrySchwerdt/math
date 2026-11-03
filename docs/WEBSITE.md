# Public research website

The public notebook uses **VitePress**, the Markdown/Vue documentation framework
used by the Mini website. It has a documentation sidebar, local full-text search,
light/dark themes, project pages and a searchable research ledger.

The source of truth remains `research/<project>/`. The site does not introduce a
second task database or any write access to the research state.

## Update and preview

From the repository root:

```sh
.venv/bin/python scripts/research.py check
.venv/bin/python scripts/research.py site
npm ci --prefix website
npm run docs:build --prefix website
npm run docs:preview --prefix website
```

Open the preview URL with `/math/` appended. For interactive development use
`npm run docs:dev --prefix website`. Rerun the Python `site` command after changing
the ledger, then rebuild for production. Node 22 is used in GitHub Actions.

The CLI generates `website/research/` Markdown and `.vitepress/ledger.json` from
validated records, project STATUS/BACKLOG files and selected canonical guides.
Generated files and build output are ignored by Git. Authored theme, home page,
configuration, dependency lockfile and generator are committed. Ledger content
is rendered as inert text/Markdown; research artifacts cannot add Vue components.
Only allowlisted summary fields enter the browser data; raw command logs and
private directories are not bundled. Evidence links point to the source commit.

## Publication

`.github/workflows/pages.yml` validates and generates the notebook, builds
VitePress and deploys only from `main` using the GitHub Pages Actions environment.
Pull requests build for verification without publishing. A manual dispatch is
also available. No deploy token, separate hosting service or database is needed.

The site is a snapshot of the most recently deployed commit, not a live view of
uncommitted local work or running agents. New task results appear after their
ledger updates are committed and the Pages workflow succeeds.

The site keeps artifact status, run outcome and mathematical proof status
separate. A successful test or a completed task is not a theorem. The public
results page explicitly shows when no formally verified research exists.

## Project task board and task IDs

The home page is a read-only task board with Open, In progress, Blocked and
Completed columns. Select a project, search for a task ID or title, then open a
card to inspect its criteria, next action, linked results/reviews and recorded
execution steps. Share the URL with `?project=ecdlp&task=ECDLP-1` to open that task.
No steps are invented for tasks with no execution records. Recorded commands show
argv, time and exit status, with links to the full evidence; raw output is not
bundled in the board. A successful run does not complete its parent task.

Each project's `TASKS.json` maps immutable canonical TSK UUIDs to readable display
keys such as ECDLP-1, FACTOR-1 and LAB-1. Existing keys are never renumbered, even
when an older record is imported. The UUID remains the cross-provider identity.
`new PROJECT TSK` assigns a missing key automatically. To initialize/import keys:

```sh
.venv/bin/python scripts/research.py task-keys example --prefix EXAMPLE
```

Task creation/key allocation is a PI/integration operation under exclusive file
ownership. Workers use their assigned task; they must not concurrently allocate
numbers in separate worktrees. If two task-index edits conflict, reconcile before
integration; validation rejects duplicate aliases. Site generation is read-only
and never changes IDs or research status.

## Updating tasks through the CLI

Agents never edit website pages to report progress. They create/update shared
records and record command evidence; the generator projects those records into
the board, documentation and history. Publish their committed changes to main.

```sh
# A new task receives its project key automatically.
.venv/bin/python scripts/research.py new ecdlp TSK
# Explicit progress update from the task's active RUN:
.venv/bin/python scripts/research.py task ecdlp ECDLP-1 \
  --run RUN-<actual-assigned-run-id> --status active \
  --reason 'Beginning the assigned toy lifecycle' \
  --next-action 'Run the bounded counterexample test'
```

Use status `blocked` with a concrete reason when blocked. To complete a task,
set `--status completed --outcome verified` (or another observed outcome), with
a reason and next action. Task completion never changes mathematical proof status.
`exec` automatically links timestamped command evidence to the assigned RUN.

Each status command atomically updates the task and links a new immutable event
under `research/<project>/events/`. The board reads these linked events directly.
Only linked events count as applied; an interruption before the atomic task
replace may leave an unreferenced event file. A per-task local lock prevents
concurrent writers in one checkout; remote task claims and worktree ownership
remain required across clones. Inspect an interrupted run before removing a stale
local lock. Commit both the task and event files with the evidence.
