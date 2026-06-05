Fetch a single Jira issue and display its details.

Usage: /jira-get <ISSUE-KEY> [--profile <name>]

Run the following command and show the result:

```bash
jira-tool get $ARGUMENTS --json
```

Parse the JSON response. If `status` is `"ok"`, display the issue details in a readable format (key, summary, status, assignee, description, and any planning fields present). If `status` is `"error"`, report the `error_code` and `message`.
