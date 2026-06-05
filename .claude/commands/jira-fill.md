Apply planning fields to a Jira issue.

Usage:
  /jira-fill <ISSUE-KEY> --file <planning.json> [--dry-run] [--profile <name>]
  /jira-fill <ISSUE-KEY> --ac "..." --business "..." --scope "..." --qa-notes "..." [--dry-run] [--profile <name>]

Run the following command and show the result:

```bash
jira-tool fill $ARGUMENTS --json
```

Planning payload (when using --file):
```json
{
  "acceptance_criteria": "...",
  "business": "...",
  "scope": "...",
  "qa_notes": "..."
}
```

Parse the JSON response. If `status` is `"ok"`, confirm the updated fields and whether it was a dry run. If `status` is `"error"`, report the `error_code` and `message`.

If the user has not supplied a planning file or inline flags, ask them for the planning content before running the command. Always suggest `--dry-run` first when the user hasn't explicitly confirmed they want to write.
