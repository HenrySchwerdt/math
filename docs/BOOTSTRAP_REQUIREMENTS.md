## Mandatory: Provider-Independent Research and Complete Auditability

The repository MUST work equally well with OpenAI Codex and Anthropic Claude Code.

This is a foundational architectural requirement, not an optional integration.

### 1. Supported AI research environments

Configure two equivalent agent orchestration environments.

**OpenAI Codex:**
- GPT-6.1 Sol: Principal Investigator, research strategist and final reviewer.
- GPT-6 Luna: Research workers, implementers, experimenters and adversarial critics.
- Use `.codex/config.toml`, `.codex/agents/`, and `AGENTS.md`.

**Anthropic Claude Code:**
- Claude Opus 5.5: Principal Investigator, research strategist and final reviewer.
- Claude Sonnet 5.5: Parallel research workers, implementers, experimenters and adversarial critics.
- Use `CLAUDE.md`, `.claude/agents/`, and supported Claude Code project configuration.

Verify the exact supported model identifiers and configuration syntax for each installed CLI. Do not fabricate configuration fields.

Both environments MUST use the same research protocol, task definitions, result schemas, review standards and persistent project state.

No research result may depend on a proprietary conversation history that the other environment cannot access.

### 2. Shared research state

Create a provider-independent, Git-versioned research ledger.

Suggested structure:

```text
research/<project>/
├── STATUS.md
├── BACKLOG.md
├── hypotheses/
├── experiments/
├── algorithms/
├── proofs/
├── reviews/
├── decisions/
├── runs/
└── papers/
```

Use globally unique, stable identifiers for research artifacts.

Examples:
- `HYP-0001`: Mathematical hypothesis
- `EXP-0001`: Experiment
- `ALG-0001`: Algorithm
- `PRF-0001`: Proof attempt
- `REV-0001`: Independent review
- `RUN-0001`: Agent execution
- `DEC-0001`: Research decision

Create concise schemas or templates and automated validation where feasible.

### 3. Complete provenance

Every meaningful research activity must record:

- Unique run identifier
- UTC start and completion timestamps
- AI provider and model identifier
- Agent role
- Assigned research task
- Exact research question
- Input hypothesis and relevant sources
- Starting Git commit
- Git worktree or branch
- Commands and experiments actually executed
- Files created or changed
- Resulting Git commit
- Test results
- Benchmark methodology and machine details
- Proof and verification status
- Review references
- Outcome: verified, refuted, unresolved, blocked or inconclusive
- Next recommended action

Use machine-readable metadata plus concise human-readable Markdown reports.

Never invent execution records, tool calls, timestamps, benchmark results, or successful verifications.

Record what was actually observed.

Where full executable command logs are practical, preserve them as reproducible artifacts. Do not commit secrets, credentials, sensitive local paths, or unbounded raw transcripts.

A short summary is not a substitute for supporting evidence.

### 4. Cross-provider handoff

Implement a documented handoff protocol.

When Codex finishes a research session, Claude Code must be able to resume from the repository alone.

The reverse must also work.

At the beginning of every session, the principal investigator must:

1. Read the shared research methodology.
2. Inspect the latest project status.
3. Read unfinished and blocked tasks.
4. Inspect recent run summaries and associated commits.
5. Identify unresolved hypotheses.
6. Avoid duplicating completed or refuted work.
7. Assign new tasks with stable identifiers.

At the end of every session, the principal investigator must:

1. Reconcile completed worker tasks.
2. Update the persistent research ledger.
3. Link new results to their evidence.
4. Record unsuccessful approaches.
5. Update the project backlog.
6. Write an actionable next-session handoff.
7. Commit and push verified updates when authorized.

Do not rely on conversational memory.

### 5. Research audit trail

Create a lightweight way to answer:

- What did each agent work on?
- Why was that task selected?
- What approach was attempted?
- Which sources and assumptions were used?
- Which commands and experiments were run?
- What changed in the repository?
- What was mathematically established?
- Which claims were rejected, and why?
- What was reviewed by Sol or Opus?
- Which work remains unresolved?
- What should the next agent do?

Preserve a chronological record and a hypothesis-centered record.

Prefer lightweight structured files initially. Introduce a database only when justified by scale.

### 6. Review independence

Reviewer agents should not simply approve another model's conclusions.

Where practical:

- Assign reviewers independently.
- Hide the proposing agent's confidence assessment during initial review.
- Require explicit attempts to find counterexamples.
- Verify algorithmic complexity separately from implementation performance.
- Distinguish experimental evidence from mathematical proof.
- Record every review decision and its rationale.
- Permit reviewers to reject work from their own provider.

An Opus review and a Sol review are assessments, not mathematical proof certificates.

A theorem marked formally verified must link to its exact Lean statement and a successful reproducible build.

### 7. Concurrent agent safety

Parallel agents must not edit the same files without coordination.

Use isolated Git worktrees or strict file ownership.

Implement task claiming or assignment so two agent systems cannot unknowingly work on the same exclusive task.

Changes to shared methodology, hypotheses or final research results must pass integration review.

Do not automatically merge conflicting research findings.

### 8. Generic research-project support

The research platform must support any number of mathematical research projects and publications.

Do not hardcode integer-factorization-specific assumptions into common orchestration, reporting, verification or publication infrastructure.

The integer-factorization project is the first consumer of this infrastructure.

Provide a documented template for initializing a second research project.

### 9. Bootstrap acceptance criteria

During the current quota-limited bootstrap session:

- Create valid Codex configuration files.
- Create valid Claude Code configuration files.
- Establish shared `AGENTS.md` and `CLAUDE.md` instructions.
- Create research state and provenance templates.
- Document the cross-provider handoff protocol.
- Prepare a first-session bootstrap for either provider.
- Validate formats and paths where tools allow.
- Push all completed work.

Do NOT launch expensive multi-agent research during bootstrap.

Do NOT implement a large orchestration framework yet.

Prioritize a small, correct, inspectable foundation over ambitious but unfinished automation.

Both AI systems must be able to start the same research task from the same repository without losing context or changing the definition of success.
