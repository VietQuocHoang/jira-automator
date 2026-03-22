from __future__ import annotations

from typing import Any

import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from jira_tool.models import JiraCredentials


class JiraAPIError(RuntimeError):
    """Normalized error for Jira API failures."""

    def __init__(self, status_code: int, code: str, message: str, details: Any | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class JiraClient:
    def __init__(self, credentials: JiraCredentials) -> None:
        self.credentials = credentials
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        self.auth = HTTPBasicAuth(credentials.email, credentials.api_token)

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, *, json_body: dict[str, Any] | None = None) -> Any:
        return self._request("POST", path, json=json_body)

    def put(self, path: str, *, json_body: dict[str, Any] | None = None) -> Any:
        return self._request("PUT", path, json=json_body)

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.credentials.base_url}{path}"
        response = self.session.request(
            method=method,
            url=url,
            auth=self.auth,
            timeout=self.credentials.timeout,
            **kwargs,
        )
        if response.status_code >= 400:
            self._raise_error(response)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def _raise_error(self, response: requests.Response) -> None:
        details: Any | None = None
        message = response.text
        try:
            details = response.json()
            message = details.get("errorMessages", [message])[0]
        except ValueError:
            details = None

        if response.status_code == 401:
            code = "AUTH_FAILED"
        elif response.status_code == 404:
            code = "NOT_FOUND"
        elif response.status_code == 429:
            code = "RATE_LIMITED"
        else:
            code = "JIRA_API_ERROR"

        raise JiraAPIError(
            status_code=response.status_code,
            code=code,
            message=message or "Jira API request failed",
            details=details,
        )
