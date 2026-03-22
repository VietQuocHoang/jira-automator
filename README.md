# Jira Automation

API-first Jira automation tool for human operators and AI agents. The project provides a stable Python CLI for pulling tickets, filling planning fields, and transitioning issues through Jira workflows.

Single-profile mode is the default. Multi-profile mode is optional for teams that need to work with multiple Jira sites.

## Implementation Plan

1. Build a shared Jira client with `.env` authentication and YAML-based field and transition mappings, with optional named profiles for multiple Jira sites.
2. Expose a stable CLI with machine-readable JSON output for `profiles`, `healthcheck`, `pull`, `get`, `fill`, `transition`, and `sync-plan`.
3. Document the exact setup and usage contract in repo-local docs so AI agents can use the tool without guessing.
4. Keep Jira REST API as the execution layer; MCP and other agents should call this tool rather than writing to Jira directly.
5. Extend later with field discovery, edit metadata validation, richer batch sync, CI hooks, and optional MCP wrappers.

## Setup

1. Create a virtual environment and install the package:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. For a single Jira setup, copy the example files:

```bash
cp .env.example .env
cp config.yaml.example config.yaml
```

For multiple Jira setups, initialize a profile instead:

```bash
jira-tool profiles init company-a
```

Profile init creates:
- `profiles/company-a/.env`
- `profiles/company-a/config.yaml`

3. Fill in either:
- `.env` and `config.yaml` for single-profile mode
- `profiles/company-a/.env` and `profiles/company-a/config.yaml` for multi-profile mode

4. Update the matching `config.yaml` with your actual Jira custom field IDs and transition names.

5. Run the health check:

```bash
jira-tool healthcheck --json
jira-tool --profile company-a healthcheck --json
```

Use the first command for single-profile mode and the second for multi-profile mode.

## Usage

List profiles:

```bash
jira-tool profiles list --json
```

Pull issues:

```bash
jira-tool pull --query planning_queue --json
jira-tool --profile company-a pull --query planning_queue --json
jira-tool pull --jql 'project = ABC AND sprint in openSprints()' --json
```

Fetch one issue:

```bash
jira-tool get ABC-123 --json
jira-tool --profile company-a get ABC-123 --json
```

Fill planning fields:

```bash
jira-tool fill ABC-123 \
  --ac "User can save a draft" \
  --business "Reduce loss of work during interruptions" \
  --scope "Draft save and resume flow" \
  --qa-notes "Verify save, reload, and draft overwrite behavior" \
  --json

jira-tool --profile company-a fill ABC-123 \
  --ac "User can save a draft" \
  --business "Reduce loss of work during interruptions" \
  --scope "Draft save and resume flow" \
  --qa-notes "Verify save, reload, and draft overwrite behavior" \
  --json
```

Or from a JSON file:

```json
{
  "acceptance_criteria": "User can save a draft",
  "business": "Reduce loss of work during interruptions",
  "scope": "Draft save and resume flow",
  "qa_notes": "Verify save, reload, and draft overwrite behavior"
}
```

```bash
jira-tool fill ABC-123 --file planning.json --json
jira-tool --profile company-a fill ABC-123 --file planning.json --json
```

Transition an issue:

```bash
jira-tool transition ABC-123 --to in_review --json
jira-tool --profile company-a transition ABC-123 --to in_review --json
```

Dry run:

```bash
jira-tool fill ABC-123 --file planning.json --dry-run --json
jira-tool transition ABC-123 --to done --dry-run --json

jira-tool --profile company-a fill ABC-123 --file planning.json --dry-run --json
jira-tool --profile company-a transition ABC-123 --to done --dry-run --json
```

## Notes

- Single-profile mode uses root `.env` and `config.yaml`.
- Multi-profile mode uses `profiles/<name>/`.
- API tokens are configured through profile-local `.env` files and must be rotated manually.
- AI agents should use `--json` always. They should use `--profile <name>` when multiple Jira profiles exist.
- Jira custom field IDs and workflow transition names are environment-specific and belong in the active `config.yaml`.

See [AGENTS.md](/Users/viethoang/Workspace/jira-automation/AGENTS.md) and [docs/contracts.md](/Users/viethoang/Workspace/jira-automation/docs/contracts.md) for the agent-facing operating contract.
