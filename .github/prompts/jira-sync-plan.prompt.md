---
mode: agent
description: Batch-apply a planning JSON file across multiple Jira issues at once.
---

Run: `jira-tool sync-plan $input --json`

where `$input` is `--file <batch.json>`, optionally with `--dry-run` and/or `--profile <name>`.

The batch file maps issue keys to planning payloads:
```json
{
  "ABC-123": { "acceptance_criteria": "...", "business": "...", "scope": "...", "qa_notes": "..." },
  "ABC-124": { "acceptance_criteria": "...", "scope": "..." }
}
```

If no file is provided, ask the user to supply one. Suggest `--dry-run` unless the user has explicitly confirmed the write.

Parse the JSON. If `status` is `"ok"`, summarise updated and skipped issues. If `status` is `"error"`, report the `error_code` and `message`.
