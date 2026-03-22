from __future__ import annotations

from typing import Any


def normalize_planning_data(
    *,
    acceptance_criteria: str | None = None,
    business: str | None = None,
    scope: str | None = None,
    qa_notes: str | None = None,
    raw: dict[str, Any] | None = None,
) -> dict[str, Any]:
    planning = dict(raw or {})
    overrides = {
        "acceptance_criteria": acceptance_criteria,
        "business": business,
        "scope": scope,
        "qa_notes": qa_notes,
    }
    for key, value in overrides.items():
        if value is not None:
            planning[key] = value

    cleaned = {key: value for key, value in planning.items() if value is not None}
    if not cleaned:
        raise ValueError("At least one planning field must be provided")
    return cleaned
