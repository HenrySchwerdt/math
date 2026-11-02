# Provider configuration verification

Checked 2026-11-02 against installed CLI help, bundled Codex catalog and official
pages below. No model inference requests were made to prove account entitlement.

| Environment | Installed CLI | PI/final review ID | Worker/critic ID |
| --- | --- | --- | --- |
| Codex | 0.166.0-alpha.5.1 | gpt-6.1-sol | gpt-6-luna |
| Claude Code | 2.1.316 (updated from 2.1.215) | claude-opus-5-5 | claude-sonnet-5-5 |

Codex `debug models --bundled` lists both configured OpenAI IDs. Codex project
config uses `[agents]` defaults and standalone `.codex/agents/*.toml` with name,
description, model, reasoning effort and developer_instructions. The installed
CLI supports `--strict-config app-server --print-startup-config` for offline
configuration validation; project trust still determines whether project config
loads. Our tests also parse each adapter and compare it to the shared roles.

Claude uses `.claude/settings.json` and `.claude/agents/*.md` with documented YAML
frontmatter name/description/model. Explicit IDs prevent floating alias drift.
Anthropic's model overview lists both 5.5 IDs. Official model configuration docs
require >=2.1.280 for Opus 5.5 and >=2.1.284 for Sonnet 5.5. The initial 2.1.215
installation was below these requirements; `claude update` successfully installed
2.1.316. Syntax/static validation is distinct from authenticated inference and
agent runtime loading. Confirm effective models and loaded agents when starting
real sessions; managed settings/environment can override project defaults.

## Sources (retrieved 2026-11-02)

- [Codex subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
- [Claude subagents/frontmatter](https://code.claude.com/docs/en/sub-agents)
- [Claude model selection and minimum CLI versions](https://code.claude.com/docs/en/model-config)
- [Claude settings scope](https://code.claude.com/docs/en/settings)
- [Anthropic exact model IDs](https://platform.claude.com/docs/en/models/overview)

These are configuration sources, not evidence for any factorization bound.

## Observed local readiness limits

`claude doctor` on 2.1.316 parsed the project without a project-settings error,
but reported missing claude.ai sign-in and no usable credentials for organization
policy lookup. It also reported an invalid PostToolUse hook in an existing
user-level settings file outside this repository. Bootstrap does not edit global
user hooks or fabricate authentication. Sign in/configure credentials and resolve
that user hook before a full live Claude session; local schema checks do not
prove account access or a successful 5.5 inference request. See captured doctor
evidence in the platform RUN.
