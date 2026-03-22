# Playbooks

## Pull Tickets For Planning

```bash
jira-tool pull --query planning_queue --json
jira-tool --profile company-a pull --query planning_queue --json
```

Use this before planning starts to collect the current queue.

## Apply Planning Details

1. Prepare a planning payload file.
2. Dry-run the update.
3. Apply the real update.

```bash
jira-tool fill ABC-123 --file planning.json --dry-run --json
jira-tool fill ABC-123 --file planning.json --json

jira-tool --profile company-a fill ABC-123 --file planning.json --dry-run --json
jira-tool --profile company-a fill ABC-123 --file planning.json --json
```

## Move Ticket After Review

```bash
jira-tool transition ABC-123 --to in_review --json
jira-tool --profile company-a transition ABC-123 --to in_review --json
```

## Move Ticket After Testing

```bash
jira-tool transition ABC-123 --to testing --json
jira-tool --profile company-a transition ABC-123 --to testing --json
```
