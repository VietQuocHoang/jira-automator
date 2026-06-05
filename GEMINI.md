# Gemini CLI Guide

This project provides `jira-tool`, the approved CLI for all Jira reads and writes. Do not call Jira APIs directly.

## Quick-start custom commands

Run `/jira-get`, `/jira-pull`, `/jira-fill`, `/jira-transition`, or `/jira-sync-plan` directly in Gemini CLI.

## Setup (first time)

```bash
cp .env.example .env
cp config.yaml.example config.yaml
# fill in credentials and field/transition mappings, then:
python3 -m venv .venv && source .venv/bin/activate && pip install -e .
jira-tool healthcheck --json
```

Multi-profile: `jira-tool profiles init company-a --json`, then fill `profiles/company-a/.env` and `profiles/company-a/config.yaml`.

## Rules

- Always pass `--json` and check `status == "ok"` before trusting a write result.
- Use `--profile <name>` when the target Jira site must be explicit.
- Never hardcode custom field IDs or transition IDs — they come from `config.yaml`.
- Run `--dry-run` before any destructive write when review is needed.

## Error codes

`AUTH_FAILED` · `NOT_FOUND` · `RATE_LIMITED` · `VALUEERROR` · `SETTINGSERROR` · `JIRA_API_ERROR`

See [docs/contracts.md](docs/contracts.md) for full request/response contracts.
