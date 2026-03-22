from __future__ import annotations

from typing import Any


PLANNING_KEYS = ("acceptance_criteria", "business", "scope", "qa_notes")


def build_issue_fields_payload(
    field_mapping: dict[str, str],
    planning_data: dict[str, Any],
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    missing_mappings = []

    for logical_name in PLANNING_KEYS:
        if logical_name not in planning_data:
            continue
        jira_field_id = field_mapping.get(logical_name)
        if not jira_field_id:
            missing_mappings.append(logical_name)
            continue
        payload[jira_field_id] = planning_data[logical_name]

    if missing_mappings:
        missing = ", ".join(sorted(missing_mappings))
        raise ValueError(f"Missing field mapping for: {missing}")

    return payload
