Batch-apply a planning JSON file across multiple Jira issues.

Usage: /jira-sync-plan --file <batch.json> [--dry-run] [--profile <name>]

The batch file maps issue keys to planning payloads:
```json
{
  "ABC-123": {
    "acceptance_criteria": "...",
    "business": "...",
    "scope": "...",
    "qa_notes": "..."
  },
  "ABC-124": {
    "acceptance_criteria": "...",
    "scope": "..."
  }
}
```

Run the following command and show the result:

```bash
jira-tool sync-plan $ARGUMENTS --json
```

Parse the JSON response. If `status` is `"ok"`, summarise which issues were updated and any that were skipped. If `status` is `"error"`, report the `error_code` and `message`.

Always suggest `--dry-run` first when the user hasn't explicitly confirmed they want to write. If no file is provided, ask the user to supply one.
