Pull Jira issues using a named query or raw JQL.

Usage:
  /jira-pull --query <name> [--profile <name>]
  /jira-pull --jql '<JQL string>' [--max-results <n>] [--profile <name>]

Run the following command and show the result:

```bash
jira-tool pull $ARGUMENTS --json
```

Parse the JSON response. If `status` is `"ok"`, display the issues as a numbered list showing key, summary, status, and assignee. Include the resolved JQL and total count. If `status` is `"error"`, report the `error_code` and `message`.

Named queries are defined in `config.yaml` under the `queries` key. If no query or JQL is supplied, ask the user which one to use.
