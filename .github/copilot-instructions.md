# GitHub Copilot Instructions

This repository provides `jira-tool`, a CLI for Jira reads and writes. Use it instead of calling Jira directly.

## Jira operations

Use the prompt files in `.github/prompts/` for common workflows:
- `/jira-get` — fetch a single issue
- `/jira-pull` — list issues by query or JQL
- `/jira-fill` — apply planning fields
- `/jira-transition` — change workflow state
- `/jira-sync-plan` — batch planning update

## Rules

- Always pass `--json` to `jira-tool` commands; check `status == "ok"` before treating any write as successful.
- Use `--profile <name>` when the target Jira site must be explicit.
- Never hardcode custom field IDs or transition IDs — use `config.yaml` mappings.
- Propose `--dry-run` before any write unless the user has explicitly confirmed.

## Error codes

`AUTH_FAILED` · `NOT_FOUND` · `RATE_LIMITED` · `VALUEERROR` · `SETTINGSERROR` · `JIRA_API_ERROR`

## References

- [AGENTS.md](../AGENTS.md) — full agent guide and setup instructions
- [docs/contracts.md](../docs/contracts.md) — CLI request/response contracts
