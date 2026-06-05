# Agent Guide

This project is the approved interface for Jira reads and writes in this repository. AI agents such as Claude, Codex, Copilot, and MCP wrappers should use this tool rather than calling Jira directly when the tool supports the needed action.

> **Claude Code users:** see [CLAUDE.md](CLAUDE.md) for slash command shortcuts (`/jira-get`, `/jira-pull`, `/jira-fill`, `/jira-transition`, `/jira-sync-plan`).

Single-profile mode is supported with root `.env` and `config.yaml`. Multi-profile mode is optional and uses `profiles/<name>/`.

## Setup

1. For single-profile mode:

```bash
cp .env.example .env
cp config.yaml.example config.yaml
```

For multi-profile mode:

```bash
jira-tool profiles init company-a --json
```

2. Fill in Jira credentials in the active `.env`.
3. Fill in Jira field mappings and transition mappings in the active `config.yaml`.
5. Install the package:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

6. Verify credentials:

```bash
jira-tool healthcheck --json
jira-tool --profile company-a healthcheck --json
```

## Rules

- Prefer `--json` for every command.
- Use `--profile <name>` when multiple Jira profiles exist or when the target Jira site must be explicit.
- Do not hardcode Jira custom field IDs.
- Do not hardcode Jira transition IDs.
- Do not call Jira directly if the CLI already supports the operation.
- Treat the active `config.yaml` as the source of truth for field and transition mappings.
- Use `--dry-run` before a write action if the calling workflow requires review.

## Supported Commands

Pull issues:

```bash
jira-tool pull --query planning_queue --json
jira-tool --profile company-a pull --query planning_queue --json
jira-tool pull --jql 'project = ABC AND assignee = currentUser()' --json
```

Get one issue:

```bash
jira-tool get ABC-123 --json
jira-tool --profile company-a get ABC-123 --json
```

Fill planning fields:

```bash
jira-tool fill ABC-123 --file planning.json --json
jira-tool --profile company-a fill ABC-123 --file planning.json --json
```

Transition an issue:

```bash
jira-tool transition ABC-123 --to in_review --json
jira-tool --profile company-a transition ABC-123 --to in_review --json
```

Manage profiles:

```bash
jira-tool profiles list --json
jira-tool profiles init company-b --json
```

## Supported Planning Payload

```json
{
  "acceptance_criteria": "User can save a draft",
  "business": "Reduce loss of work during interruptions",
  "scope": "Draft save and resume flow",
  "qa_notes": "Verify save, reload, and draft overwrite behavior"
}
```

## Error Handling

The CLI returns structured JSON on failure. Common error codes:

- `AUTH_FAILED`
- `NOT_FOUND`
- `RATE_LIMITED`
- `VALUEERROR`
- `SETTINGSERROR`
- `JIRA_API_ERROR`

Agents should check `status == "ok"` before assuming a write or transition succeeded.

## Current Limits

- Batch sync is not implemented yet.
- The tool currently assumes Jira custom fields accept string values directly.
- Workflow transitions are resolved by configured transition name and currently apply the first matching available transition.
- Profile discovery requires both `profiles/<name>/.env` and `profiles/<name>/config.yaml` to exist.
- If root `.env` and `config.yaml` exist, they are used by default.
- If root config is absent and exactly one profile exists, that profile is used automatically.

For command and response contracts, see [docs/contracts.md](docs/contracts.md).
