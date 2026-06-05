---
mode: agent
description: Pull Jira issues using a named query or raw JQL and list them.
---

Run: `jira-tool pull $input --json`

where `$input` is one of:
- `--query <name>` (named query from `config.yaml`)
- `--jql '<JQL string>'` with an optional `--max-results <n>`
- optionally appended with `--profile <name>`

If no query or JQL is supplied, ask the user before running.

Parse the JSON. If `status` is `"ok"`, display the issues as a numbered list (key, summary, status, assignee) plus the resolved JQL and count. If `status` is `"error"`, report the `error_code` and `message`.
