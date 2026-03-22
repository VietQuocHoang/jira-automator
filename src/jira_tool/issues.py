from __future__ import annotations

from typing import Any

from jira_tool.client import JiraClient


def search_issues(
    client: JiraClient,
    jql: str,
    *,
    fields: list[str] | None = None,
    max_results: int = 50,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "jql": jql,
        "maxResults": max_results,
    }
    if fields:
        payload["fields"] = fields
    return client.post("/rest/api/3/search", json_body=payload)


def get_issue(
    client: JiraClient,
    issue_key: str,
    *,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    params = {"fields": ",".join(fields)} if fields else None
    return client.get(f"/rest/api/3/issue/{issue_key}", params=params)


def update_issue(client: JiraClient, issue_key: str, fields_payload: dict[str, Any]) -> None:
    client.put(f"/rest/api/3/issue/{issue_key}", json_body={"fields": fields_payload})
