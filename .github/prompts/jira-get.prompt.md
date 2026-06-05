---
mode: agent
description: Fetch a single Jira issue by key and display its details.
---

Run: `jira-tool get $input --json`

where `$input` is the issue key (e.g. `ABC-123`), optionally prefixed with `--profile <name>`.

Parse the JSON. If `status` is `"ok"`, display key, summary, status, assignee, and any planning fields in a readable format. If `status` is `"error"`, report the `error_code` and `message`.
