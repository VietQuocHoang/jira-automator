from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import os
import shutil

import yaml
from dotenv import load_dotenv

from jira_tool.models import AppConfig, JiraCredentials


class SettingsError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(slots=True)
class Settings:
    credentials: JiraCredentials
    config: AppConfig


@dataclass(slots=True)
class ProfilePaths:
    name: str
    directory: Path
    env_file: Path
    config_file: Path


def load_settings(
    env_path: str | Path | None = None,
    config_path: str | Path | None = None,
    profile: str | None = None,
    profiles_dir: str | Path = "profiles",
) -> Settings:
    profile_paths = resolve_profile_paths(
        profile=profile,
        env_path=env_path,
        config_path=config_path,
        profiles_dir=profiles_dir,
    )
    load_dotenv(dotenv_path=profile_paths.env_file, override=False)

    base_url = os.getenv("JIRA_BASE_URL", "").strip().rstrip("/")
    email = os.getenv("JIRA_EMAIL", "").strip()
    api_token = os.getenv("JIRA_API_TOKEN", "").strip()
    project_key = os.getenv("JIRA_PROJECT_KEY", "").strip() or None
    timeout_raw = os.getenv("JIRA_TIMEOUT", "30").strip()

    missing = [
        name
        for name, value in {
            "JIRA_BASE_URL": base_url,
            "JIRA_EMAIL": email,
            "JIRA_API_TOKEN": api_token,
        }.items()
        if not value
    ]
    if missing:
        raise SettingsError(f"Missing required environment variables: {', '.join(missing)}")

    try:
        timeout = int(timeout_raw)
    except ValueError as exc:
        raise SettingsError("JIRA_TIMEOUT must be an integer") from exc

    config_file = profile_paths.config_file
    if not config_file.exists():
        raise SettingsError(
            f"Config file not found: {config_file}. Copy config.yaml.example to config.yaml."
        )

    with config_file.open("r", encoding="utf-8") as handle:
        raw_config: dict[str, Any] = yaml.safe_load(handle) or {}

    credentials = JiraCredentials(
        base_url=base_url,
        email=email,
        api_token=api_token,
        timeout=timeout,
        project_key=project_key,
    )
    return Settings(credentials=credentials, config=AppConfig(raw=raw_config))


def resolve_profile_paths(
    *,
    profile: str | None,
    env_path: str | Path | None,
    config_path: str | Path | None,
    profiles_dir: str | Path = "profiles",
) -> ProfilePaths:
    if profile:
        directory = Path(profiles_dir) / profile
        return ProfilePaths(
            name=profile,
            directory=directory,
            env_file=directory / ".env",
            config_file=directory / "config.yaml",
        )

    env_file = Path(env_path or ".env")
    config_file = Path(config_path or "config.yaml")
    if env_file.exists() and config_file.exists():
        return ProfilePaths(
            name="default",
            directory=Path("."),
            env_file=env_file,
            config_file=config_file,
        )

    profiles = list_profiles(profiles_dir)
    if len(profiles) == 1:
        only_profile = profiles[0]
        directory = Path(profiles_dir) / only_profile
        return ProfilePaths(
            name=only_profile,
            directory=directory,
            env_file=directory / ".env",
            config_file=directory / "config.yaml",
        )

    return ProfilePaths(
        name="default",
        directory=Path("."),
        env_file=env_file,
        config_file=config_file,
    )


def list_profiles(profiles_dir: str | Path = "profiles") -> list[str]:
    root = Path(profiles_dir)
    if not root.exists():
        return []
    return sorted(
        item.name
        for item in root.iterdir()
        if item.is_dir() and (item / ".env").exists() and (item / "config.yaml").exists()
    )


def init_profile(
    profile: str,
    *,
    profiles_dir: str | Path = "profiles",
    env_template: str | Path = ".env.example",
    config_template: str | Path = "config.yaml.example",
) -> ProfilePaths:
    paths = resolve_profile_paths(
        profile=profile,
        env_path=None,
        config_path=None,
        profiles_dir=profiles_dir,
    )
    paths.directory.mkdir(parents=True, exist_ok=True)

    env_template_path = Path(env_template)
    config_template_path = Path(config_template)
    if not env_template_path.exists():
        raise SettingsError(f"Template not found: {env_template_path}")
    if not config_template_path.exists():
        raise SettingsError(f"Template not found: {config_template_path}")

    if not paths.env_file.exists():
        shutil.copyfile(env_template_path, paths.env_file)
    if not paths.config_file.exists():
        shutil.copyfile(config_template_path, paths.config_file)

    return paths
