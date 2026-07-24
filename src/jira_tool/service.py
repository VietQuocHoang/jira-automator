from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from jira_tool.client import JiraAPIError, JiraClient
from jira_tool.comments import load_comment_body, markdown_to_adf, post_comment
from jira_tool.fields import build_issue_fields_payload
from jira_tool.issues import create_issue, get_issue, search_issues, update_issue
from jira_tool.models import AppConfig
from jira_tool.planning import normalize_planning_data
from jira_tool.transitions import (
    get_available_transitions,
    resolve_transition_name,
    transition_issue,
)


class JiraService:
    def __init__(self, client: JiraClient, config: AppConfig) -> None:
        self.client = client
        self.config = config

    def healthcheck(self) -> dict[str, Any]:
        me = self.client.get("/rest/api/3/myself")
        return {
            "status": "ok",
            "account_id": me.get("accountId"),
            "display_name": me.get("displayName"),
            "email": me.get("emailAddress"),
            "base_url": self.client.credentials.base_url,
        }

    def pull(
        self,
        *,
        query_name: str | None = None,
        jql: str | None = None,
        max_results: int = 50,
    ) -> dict[str, Any]:
        resolved_jql = jql or self.config.queries.get(query_name or "")
        if not resolved_jql:
            raise ValueError("Either --jql or a valid --query name is required")
        result = search_issues(
            self.client,
            resolved_jql,
            fields=["summary", "status", "assignee"],
            max_results=max_results,
        )
        issues = []
        for issue in result.get("issues", []):
            fields = issue.get("fields", {})
            assignee = fields.get("assignee") or {}
            status = fields.get("status") or {}
            issues.append(
                {
                    "key": issue.get("key"),
                    "summary": fields.get("summary"),
                    "status": status.get("name"),
                    "assignee": assignee.get("displayName"),
                }
            )
        return {
            "status": "ok",
            "jql": resolved_jql,
            "count": len(issues),
            "issues": issues,
        }

    def get(self, issue_key: str) -> dict[str, Any]:
        issue = get_issue(self.client, issue_key)
        return {"status": "ok", "issue": issue}

    def fill(
        self,
        issue_key: str,
        *,
        acceptance_criteria: str | None = None,
        business: str | None = None,
        scope: str | None = None,
        qa_notes: str | None = None,
        build_number: float | int | str | None = None,
        planning_file: str | None = None,
        raw_planning: dict[str, Any] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        file_planning = self._load_json_file(planning_file) if planning_file else None
        planning = normalize_planning_data(
            acceptance_criteria=acceptance_criteria,
            business=business,
            scope=scope,
            qa_notes=qa_notes,
            build_number=build_number,
            raw=raw_planning or file_planning,
        )
        payload = build_issue_fields_payload(self.config.fields, planning)
        if not dry_run:
            update_issue(self.client, issue_key, payload)
        return {
            "status": "ok",
            "issue_key": issue_key,
            "updated_fields": sorted(planning.keys()),
            "dry_run": dry_run,
            "fields_payload": payload,
        }

    def create(
        self,
        *,
        summary: str,
        project_key: str | None = None,
        issue_type: str = "Bug",
        body_text: str | None = None,
        markdown_file: str | None = None,
        labels: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        if not summary:
            raise ValueError("--summary is required")

        resolved_project = (
            project_key
            or self.config.projects.get("default")
            or self.client.credentials.project_key
        )
        if not resolved_project:
            raise ValueError(
                "Project key is required: pass --project, or set projects.default in "
                "config.yaml, or set JIRA_PROJECT_KEY"
            )

        fields_payload: dict[str, Any] = {
            "project": {"key": resolved_project},
            "issuetype": {"name": issue_type},
            "summary": summary,
        }
        if body_text is not None or markdown_file is not None:
            description_md = (
                body_text if body_text is not None else Path(markdown_file).read_text(encoding="utf-8")
            )
            fields_payload["description"] = markdown_to_adf(description_md)
        if labels:
            fields_payload["labels"] = labels

        issue_key = None
        if not dry_run:
            result = create_issue(self.client, fields_payload)
            issue_key = result.get("key")

        return {
            "status": "ok",
            "issue_key": issue_key,
            "project_key": resolved_project,
            "issue_type": issue_type,
            "dry_run": dry_run,
            "fields_payload": fields_payload,
        }

    def update(
        self,
        issue_key: str,
        *,
        summary: str | None = None,
        body_text: str | None = None,
        markdown_file: str | None = None,
        labels: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        fields_payload: dict[str, Any] = {}
        if summary is not None:
            fields_payload["summary"] = summary
        if body_text is not None or markdown_file is not None:
            description_md = (
                body_text if body_text is not None else Path(markdown_file).read_text(encoding="utf-8")
            )
            fields_payload["description"] = markdown_to_adf(description_md)
        if labels is not None:
            fields_payload["labels"] = labels

        if not fields_payload:
            raise ValueError("Provide at least one of --summary, --body/--file, or --label")

        if not dry_run:
            update_issue(self.client, issue_key, fields_payload)

        return {
            "status": "ok",
            "issue_key": issue_key,
            "updated_fields": sorted(fields_payload.keys()),
            "dry_run": dry_run,
            "fields_payload": fields_payload,
        }

    def transition(self, issue_key: str, target_state: str, *, dry_run: bool = False) -> dict[str, Any]:
        transition_name = resolve_transition_name(self.config.transitions, target_state)
        available = get_available_transitions(self.client, issue_key)
        available_names = [item.get("name") for item in available]
        if not dry_run:
            applied = transition_issue(self.client, issue_key, available, transition_name)
        else:
            applied = transition_name
        return {
            "status": "ok",
            "issue_key": issue_key,
            "target_state": target_state,
            "transition_name": applied,
            "available_transitions": available_names,
            "dry_run": dry_run,
        }

    def sync_plan(self, payload_file: str, *, dry_run: bool = False) -> dict[str, Any]:
        payload = self._load_json_file(payload_file)
        items = payload.get("items", [])
        if not items:
            raise ValueError("sync-plan payload must include a non-empty 'items' array")

        results = []
        for item in items:
            issue_key = item["issue_key"]
            planning = item.get("planning", {})
            target_state = item.get("target_state")
            fill_result = self.fill(issue_key, raw_planning=planning, dry_run=dry_run)
            transition_result = None
            if target_state:
                transition_result = self.transition(issue_key, target_state, dry_run=dry_run)
            results.append(
                {
                    "issue_key": issue_key,
                    "fill": fill_result,
                    "transition": transition_result,
                }
            )
        return {"status": "ok", "results": results, "dry_run": dry_run}

    def comment(
        self,
        issue_key: str,
        *,
        body_text: str | None = None,
        markdown_file: str | None = None,
        adf_file: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        body = load_comment_body(text=body_text, markdown_file=markdown_file, adf_file=adf_file)
        if not dry_run:
            result = post_comment(self.client, issue_key, body)
            comment_id = result.get("id")
            comment_url = result.get("self", "")
        else:
            comment_id = None
            comment_url = ""
        return {
            "status": "ok",
            "issue_key": issue_key,
            "comment_id": comment_id,
            "comment_url": comment_url,
            "dry_run": dry_run,
        }

    def _load_json_file(self, path: str) -> dict[str, Any]:
        with Path(path).open("r", encoding="utf-8") as handle:
            return json.load(handle)


def format_error(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, JiraAPIError):
        return {
            "status": "error",
            "error_code": exc.code,
            "message": exc.message,
            "details": exc.details,
        }
    return {
        "status": "error",
        "error_code": exc.__class__.__name__.upper(),
        "message": str(exc),
    }
