from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class JiraCredentials:
    base_url: str
    email: str
    api_token: str
    timeout: int = 30
    project_key: str | None = None


@dataclass(slots=True)
class AppConfig:
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def fields(self) -> dict[str, str]:
        return dict(self.raw.get("fields", {}))

    @property
    def transitions(self) -> dict[str, str]:
        return dict(self.raw.get("transitions", {}))

    @property
    def queries(self) -> dict[str, str]:
        return dict(self.raw.get("queries", {}))

    @property
    def behavior(self) -> dict[str, Any]:
        return dict(self.raw.get("behavior", {}))
