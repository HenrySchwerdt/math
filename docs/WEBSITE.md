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
