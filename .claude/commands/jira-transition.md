Transition a Jira issue to a new workflow state.

Usage: /jira-transition <ISSUE-KEY> --to <state-name> [--dry-run] [--profile <name>]

State names are the keys defined under `transitions` in `config.yaml` (e.g. `in_review`, `done`). Do not use raw Jira transition IDs.

Run the following command and show the result:

```bash
jira-tool transition $ARGUMENTS --json
```

Parse the JSON response. If `status` is `"ok"`, confirm the issue key, resolved transition name, and whether it was a dry run. If `status` is `"error"`, report the `error_code` and `message`.

If `--to` is missing, ask the user which state they want to transition to before running the command. Suggest `--dry-run` first when the user hasn't explicitly confirmed the write.
