# Claude Code Guide

This project provides `jira-tool`, the approved CLI for all Jira reads and writes. Use it instead of calling Jira directly.

## Quick-start slash commands

Claude Code users can invoke these slash commands directly:

| Command | Description |
|---|---|
| `/jira-get <KEY>` | Fetch a single issue |
| `/jira-pull` | Pull issues by named query or JQL |
| `/jira-fill <KEY>` | Apply planning fields to an issue |
| `/jira-transition <KEY>` | Transition an issue to a new state |
| `/jira-sync-plan` | Batch-apply a planning JSON file |

## Setup (first time)

```bash
cp .env.example .env
cp config.yaml.example config.yaml
# fill in credentials and field/transition mappings, then:
python3 -m venv .venv && source .venv/bin/activate && pip install -e .
jira-tool healthcheck --json
```

Multi-profile:

```bash
jira-tool profiles init company-a --json
# then fill profiles/company-a/.env and profiles/company-a/config.yaml
```

## Rules

- Always pass `--json`; parse `status == "ok"` before trusting a write result.
- Use `--profile <name>` when the target Jira site must be explicit.
- Never hardcode custom field IDs or transition IDs — use `config.yaml` mappings.
- Run `--dry-run` before any destructive write when review is needed.

## Error codes

`AUTH_FAILED` · `NOT_FOUND` · `RATE_LIMITED` · `VALUEERROR` · `SETTINGSERROR` · `JIRA_API_ERROR`

See [docs/contracts.md](docs/contracts.md) for full request/response contracts.
