from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from jira_tool.client import JiraClient
from jira_tool.service import JiraService, format_error
from jira_tool.settings import load_settings

mcp = FastMCP("jira-tool")

_PROFILES_DIR = os.getenv("JIRA_PROFILES_DIR", "profiles")


def _get_service(profile: str | None = None) -> JiraService:
    settings = load_settings(profile=profile, profiles_dir=_PROFILES_DIR)
    return JiraService(JiraClient(settings.credentials), settings.config)


@mcp.tool()
def healthcheck(profile: str | None = None) -> dict[str, Any]:
    """Validate Jira credentials and return account info for the active profile."""
    try:
        return _get_service(profile).healthcheck()
    except Exception as exc:
        return format_error(exc)


@mcp.tool()
def pull_issues(
    query: str | None = None,
    jql: str | None = None,
    max_results: int = 50,
    profile: str | None = None,
) -> dict[str, Any]:
    """Fetch Jira issues by named query (from config.yaml) or raw JQL string.

    Provide either 'query' (a named query key) or 'jql' (a raw JQL expression).
    """
    try:
        return _get_service(profile).pull(query_name=query, jql=jql, max_results=max_results)
    except Exception as exc:
        return format_error(exc)


@mcp.tool()
def get_issue(issue_key: str, profile: str | None = None) -> dict[str, Any]:
    """Fetch the full details of a single Jira issue (e.g. ABC-123)."""
    try:
        return _get_service(profile).get(issue_key)
    except Exception as exc:
        return format_error(exc)


@mcp.tool()
def fill_issue(
    issue_key: str,
    acceptance_criteria: str | None = None,
    business: str | None = None,
    scope: str | None = None,
    qa_notes: str | None = None,
    dry_run: bool = False,
    profile: str | None = None,
) -> dict[str, Any]:
    """Write planning fields to a Jira issue.

    Provide any combination of acceptance_criteria, business, scope, and qa_notes.
    Set dry_run=True to preview the payload without writing to Jira.
    """
    try:
        return _get_service(profile).fill(
            issue_key,
            acceptance_criteria=acceptance_criteria,
            business=business,
            scope=scope,
            qa_notes=qa_notes,
            dry_run=dry_run,
        )
    except Exception as exc:
        return format_error(exc)


@mcp.tool()
def transition_issue(
    issue_key: str,
    target_state: str,
    dry_run: bool = False,
    profile: str | None = None,
) -> dict[str, Any]:
    """Move a Jira issue to a new workflow state.

    'target_state' must match a key defined in config.yaml transitions
    (e.g. 'in_review', 'done', 'in_progress').
    Set dry_run=True to preview without applying the transition.
    """
    try:
        return _get_service(profile).transition(issue_key, target_state, dry_run=dry_run)
    except Exception as exc:
        return format_error(exc)


@mcp.tool()
def sync_plan(
    items: list[dict[str, Any]],
    dry_run: bool = False,
    profile: str | None = None,
) -> dict[str, Any]:
    """Batch-apply planning data and optional transitions across multiple Jira issues.

    Each item must have:
      - issue_key (str): the Jira issue key, e.g. "ABC-123"
      - planning (dict): any subset of acceptance_criteria, business, scope, qa_notes
      - target_state (str, optional): workflow state key from config.yaml transitions

    Set dry_run=True to preview all writes without applying them.
    """
    try:
        service = _get_service(profile)
        results = []
        for item in items:
            issue_key = item["issue_key"]
            planning = item.get("planning", {})
            target_state = item.get("target_state")
            fill_result = service.fill(issue_key, raw_planning=planning, dry_run=dry_run)
            transition_result = None
            if target_state:
                transition_result = service.transition(issue_key, target_state, dry_run=dry_run)
            results.append({
                "issue_key": issue_key,
                "fill": fill_result,
                "transition": transition_result,
            })
        return {"status": "ok", "results": results, "dry_run": dry_run}
    except Exception as exc:
        return format_error(exc)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
