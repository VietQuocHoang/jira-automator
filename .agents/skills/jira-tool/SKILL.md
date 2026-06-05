---
name: jira-tool
description: Interact with Jira using the jira-tool CLI — fetch issues, pull issue lists, apply planning fields, transition workflow states, and batch-sync plans. Use whenever a task involves reading or writing Jira issues in this repository.
---

# jira-tool skill

`jira-tool` is the approved CLI for all Jira reads and writes. Never call Jira APIs directly.

## Rules

- Always pass `--json` and check `status == "ok"` before treating a write as successful.
- Use `--profile <name>` when multiple Jira profiles exist or the target site must be explicit.
- Never hardcode custom field IDs or transition IDs — they come from `config.yaml`.
- Use `--dry-run` before any write when the workflow requires review.

## Commands

### Get one issue
```bash
jira-tool get <ISSUE-KEY> --json
jira-tool --profile <name> get <ISSUE-KEY> --json
```

### Pull issues
```bash
jira-tool pull --query <named-query> --json
jira-tool pull --jql '<JQL>' --max-results 50 --json
```
Named queries are defined under `queries` in `config.yaml`.

### Fill planning fields
```bash
# From inline flags
jira-tool fill <ISSUE-KEY> --ac "..." --business "..." --scope "..." --qa-notes "..." --json

# From a JSON file
jira-tool fill <ISSUE-KEY> --file planning.json --json
```
Planning file schema:
```json
{
  "acceptance_criteria": "...",
  "business": "...",
  "scope": "...",
  "qa_notes": "..."
}
```

### Transition an issue
```bash
jira-tool transition <ISSUE-KEY> --to <state-key> --json
```
State keys are defined under `transitions` in `config.yaml` (e.g. `in_review`, `done`).

### Batch sync plan
```bash
jira-tool sync-plan --file batch.json --json
```
Batch file maps issue keys to planning payloads (same fields as above).

### Profiles
```bash
jira-tool profiles list --json
jira-tool profiles init <name> --json
```

### Healthcheck
```bash
jira-tool healthcheck --json
```

## Error codes
`AUTH_FAILED` · `NOT_FOUND` · `RATE_LIMITED` · `VALUEERROR` · `SETTINGSERROR` · `JIRA_API_ERROR`

## Setup (if not yet installed)
```bash
cp .env.example .env && cp config.yaml.example config.yaml
python3 -m venv .venv && source .venv/bin/activate && pip install -e .
jira-tool healthcheck --json
```

See [docs/contracts.md](../../../docs/contracts.md) for full request/response contracts.
