---
mode: agent
description: Transition a Jira issue to a new workflow state using a configured state key.
---

Run: `jira-tool transition $input --json`

where `$input` is `<ISSUE-KEY> --to <state-key>`, optionally with `--dry-run` and/or `--profile <name>`.

State keys come from `transitions` in `config.yaml` (e.g. `in_review`, `done`). Never use raw Jira transition IDs.

If `--to` is missing, ask the user which state before running. Suggest `--dry-run` unless the user has explicitly confirmed the write.

Parse the JSON. If `status` is `"ok"`, confirm the issue key, resolved transition name, and dry-run status. If `status` is `"error"`, report the `error_code` and `message`.
