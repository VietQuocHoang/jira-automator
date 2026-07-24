# CLI Contracts

## General Rules

- Use `--json` when the caller is an AI agent or another program.
- Exit code `0` means success.
- Exit code `1` means failure.
- On failure, the CLI emits a JSON error object.

## Commands

### `jira-tool profiles list --json`

Success:

```json
{
  "status": "ok",
  "profiles": ["company-a", "company-b"],
  "count": 2
}
```

### `jira-tool profiles init company-a --json`

Success:

```json
{
  "status": "ok",
  "profile": "company-a",
  "env_file": "profiles/company-a/.env",
  "config_file": "profiles/company-a/config.yaml"
}
```

### `jira-tool healthcheck --json`

Uses root `.env` and `config.yaml` in single-profile mode. If those files are absent and exactly one profile exists, the CLI falls back to that profile.

### `jira-tool --profile company-a healthcheck --json`

Success:

```json
{
  "status": "ok",
  "account_id": "abc123",
  "display_name": "Example User",
  "email": "user@example.com",
  "base_url": "https://your-domain.atlassian.net"
}
```

### `jira-tool pull --query planning_queue --json`

Single-profile form.

### `jira-tool --profile company-a pull --query planning_queue --json`

Success:

```json
{
  "status": "ok",
  "jql": "project = ABC AND status = \"To Do\" ORDER BY priority DESC",
  "count": 2,
  "issues": [
    {
      "key": "ABC-123",
      "summary": "Implement draft save",
      "status": "To Do",
      "assignee": "Example User"
    }
  ]
}
```

### `jira-tool create --summary "..." --type Bug --json`

Single-profile form.

### `jira-tool --profile company-a create --summary "..." --type Bug --json`

`--project` defaults to `projects.default` in `config.yaml`, then `JIRA_PROJECT_KEY`. `--type` defaults to `Bug`. `--body`/`--file` (description) are optional and mutually exclusive; `--label` may be repeated.

Success:

```json
{
  "status": "ok",
  "issue_key": "ABC-124",
  "project_key": "ABC",
  "issue_type": "Bug",
  "dry_run": false,
  "fields_payload": {
    "project": {"key": "ABC"},
    "issuetype": {"name": "Bug"},
    "summary": "Login button unresponsive on Safari"
  }
}
```

### `jira-tool update ABC-123 --body "..." --json`

Single-profile form.

### `jira-tool --profile company-a update ABC-123 --summary "..." --file description.md --label backend --json`

At least one of `--summary`, `--body`/`--file`, `--label` is required. `--label` replaces the full label set (not additive).

Success:

```json
{
  "status": "ok",
  "issue_key": "ABC-123",
  "updated_fields": ["labels", "summary"],
  "dry_run": false,
  "fields_payload": {
    "summary": "New title",
    "labels": ["backend"]
  }
}
```

### `jira-tool get ABC-123 --json`

Single-profile form.

### `jira-tool --profile company-a get ABC-123 --json`

Success:

```json
{
  "status": "ok",
  "issue": {
    "id": "10001",
    "key": "ABC-123"
  }
}
```

### `jira-tool fill ABC-123 --file planning.json --json`

Single-profile form.

### `jira-tool --profile company-a fill ABC-123 --file planning.json --json`

Input file:

```json
{
  "acceptance_criteria": "User can save a draft",
  "business": "Reduce loss of work during interruptions",
  "scope": "Draft save and resume flow",
  "qa_notes": "Verify save, reload, and draft overwrite behavior",
  "build_number": 877
}
```

`build_number` (also settable via `--build-number`) maps to `fields.build_number` in `config.yaml` — a numeric field, typically used to record the PR/MR number under review.

Success:

```json
{
  "status": "ok",
  "issue_key": "ABC-123",
  "updated_fields": [
    "acceptance_criteria",
    "build_number",
    "business",
    "qa_notes",
    "scope"
  ],
  "dry_run": false,
  "fields_payload": {
    "customfield_10041": "User can save a draft"
  }
}
```

### `jira-tool transition ABC-123 --to in_review --json`

Single-profile form.

### `jira-tool --profile company-a transition ABC-123 --to in_review --json`

Success:

```json
{
  "status": "ok",
  "issue_key": "ABC-123",
  "target_state": "in_review",
  "transition_name": "Ready for Review",
  "available_transitions": [
    "Start Progress",
    "Ready for Review"
  ],
  "dry_run": false
}
```

## Error Contract

```json
{
  "status": "error",
  "error_code": "AUTH_FAILED",
  "message": "Unauthorized",
  "details": {}
}
```
