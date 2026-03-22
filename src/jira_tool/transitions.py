from __future__ import annotations

from typing import Any

from jira_tool.client import JiraClient


def get_available_transitions(client: JiraClient, issue_key: str) -> list[dict[str, Any]]:
    response = client.get(f"/rest/api/3/issue/{issue_key}/transitions")
    return list(response.get("transitions", []))


def resolve_transition_name(
    configured_transitions: dict[str, str],
    target_state: str,
) -> str:
    transition_name = configured_transitions.get(target_state)
    if not transition_name:
        raise ValueError(f"No transition configured for target state '{target_state}'")
    return transition_name


def transition_issue(
    client: JiraClient,
    issue_key: str,
    available_transitions: list[dict[str, Any]],
    transition_name: str,
) -> str:
    matches = [item for item in available_transitions if item.get("name") == transition_name]
    if not matches:
        raise ValueError(
            f"Configured transition '{transition_name}' is not available for issue {issue_key}"
        )

    transition_id = matches[0]["id"]
    client.post(
        f"/rest/api/3/issue/{issue_key}/transitions",
        json_body={"transition": {"id": transition_id}},
    )
    return transition_name
