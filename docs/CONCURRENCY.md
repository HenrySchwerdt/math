# Task claims and file ownership

Use a single canonical origin for a project. `research.py claim PROJECT TSK RUN`
creates a unique claim commit and atomically creates `refs/heads/claims/TSK`
on origin with an empty expected value (`--force-with-lease=<ref>:`). Only one
contender can succeed, including across clones/providers. Claim commits contain
only a small JSON owner record, not uncommitted research or credentials.
A network failure is not permission to work: inspect the remote claim and stop
until ownership is confirmed. Offline sessions may inspect, not execute exclusive tasks.

The RUN must identify its task, provider/model and branch/worktree. Inspect a
claim with `git fetch origin refs/heads/claims/TSK` then `git show FETCH_HEAD`.
To release use `research.py release PROJECT TSK RUN CLAIM_COMMIT`; it compares
both owner metadata and expected remote hash. A stale owner cannot delete a
replacement claim. Keep claims until pushed handoff; takeover requires explicit
coordination and an auditable DEC, never elapsed-time guessing.

After the initial commit, create a worker worktree with:
`git worktree add ../math-TSK -b research/TSK HEAD` (substitute the actual ID).
Each task writes only owned files or its isolated worktree. PI alone integrates
shared STATUS/BACKLOG/methodology and final-result records after review. Commit
claims are coordination objects, not result branches: never merge them.
The main branch must be pushed before agents claim tasks.
