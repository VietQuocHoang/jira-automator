---
mode: agent
description: Apply planning fields (acceptance criteria, business value, scope, QA notes) to a Jira issue.
---

Run: `jira-tool fill $input --json`

where `$input` is `<ISSUE-KEY>` followed by one of:
- `--file <planning.json>` (JSON with `acceptance_criteria`, `business`, `scope`, `qa_notes`)
- `--ac "..." --business "..." --scope "..." --qa-notes "..."`
- optionally append `--dry-run` and/or `--profile <name>`

If the issue key or planning content is missing, ask the user before running. Suggest `--dry-run` unless the user has explicitly confirmed they want to write.

Parse the JSON. If `status` is `"ok"`, confirm the updated fields and whether it was a dry run. If `status` is `"error"`, report the `error_code` and `message`.
