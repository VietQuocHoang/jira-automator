from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from jira_tool.client import JiraClient
from jira_tool.service import JiraService, format_error
from jira_tool.settings import SettingsError, init_profile, list_profiles, load_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jira-tool", description="Jira automation CLI")
    parser.add_argument("--profile", help="Named Jira profile under profiles/<name>")
    parser.add_argument("--profiles-dir", default="profiles", help="Profiles directory")
    parser.add_argument("--env-file", default=".env", help="Path to .env file when not using --profile")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML when not using --profile")

    subparsers = parser.add_subparsers(dest="command", required=True)

    profiles = subparsers.add_parser("profiles", help="Manage Jira profiles")
    profiles_subparsers = profiles.add_subparsers(dest="profiles_command", required=True)

    profiles_list = profiles_subparsers.add_parser("list", help="List available profiles")
    profiles_list.add_argument("--json", action="store_true", help="Emit JSON output")

    profiles_init = profiles_subparsers.add_parser("init", help="Initialize a new profile")
    profiles_init.add_argument("name", help="Profile name")
    profiles_init.add_argument("--json", action="store_true", help="Emit JSON output")

    healthcheck = subparsers.add_parser("healthcheck", help="Validate Jira credentials")
    healthcheck.add_argument("--json", action="store_true", help="Emit JSON output")

    pull = subparsers.add_parser("pull", help="Pull Jira issues")
    pull.add_argument("--query", help="Named query from config.yaml")
    pull.add_argument("--jql", help="Raw JQL string")
    pull.add_argument("--max-results", type=int, default=50)
    pull.add_argument("--json", action="store_true", help="Emit JSON output")

    get_cmd = subparsers.add_parser("get", help="Fetch a Jira issue")
    get_cmd.add_argument("issue_key")
    get_cmd.add_argument("--json", action="store_true", help="Emit JSON output")

    fill = subparsers.add_parser("fill", help="Fill planning fields on a Jira issue")
    fill.add_argument("issue_key")
    fill.add_argument("--ac", dest="acceptance_criteria")
    fill.add_argument("--business")
    fill.add_argument("--scope")
    fill.add_argument("--qa-notes", dest="qa_notes")
    fill.add_argument("--file", help="JSON file with planning payload")
    fill.add_argument("--dry-run", action="store_true")
    fill.add_argument("--json", action="store_true", help="Emit JSON output")

    transition = subparsers.add_parser("transition", help="Transition a Jira issue")
    transition.add_argument("issue_key")
    transition.add_argument("--to", required=True, dest="target_state")
    transition.add_argument("--dry-run", action="store_true")
    transition.add_argument("--json", action="store_true", help="Emit JSON output")

    sync_plan = subparsers.add_parser("sync-plan", help="Apply planning updates in batch")
    sync_plan.add_argument("--file", required=True, help="JSON file with batch payload")
    sync_plan.add_argument("--dry-run", action="store_true")
    sync_plan.add_argument("--json", action="store_true", help="Emit JSON output")

    comment = subparsers.add_parser("comment", help="Post a comment on a Jira issue")
    comment.add_argument("issue_key")
    body_group = comment.add_mutually_exclusive_group(required=True)
    body_group.add_argument("--body", dest="body_text", metavar="TEXT",
                            help="Inline markdown text to post as comment")
    body_group.add_argument("--file", dest="markdown_file", metavar="FILE",
                            help="Markdown file whose content becomes the comment body")
    body_group.add_argument("--adf-file", dest="adf_file", metavar="FILE",
                            help="Pre-built ADF JSON file to post verbatim")
    comment.add_argument("--dry-run", action="store_true",
                         help="Parse and validate without posting")
    comment.add_argument("--json", action="store_true", help="Emit JSON output")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = _dispatch(args)
        _emit(result, as_json=getattr(args, "json", False))
        return 0
    except (SettingsError, Exception) as exc:
        error = format_error(exc)
        _emit(error, as_json=True)
        return 1


def _dispatch(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "profiles":
        return _dispatch_profiles(args)

    settings = load_settings(
        env_path=args.env_file,
        config_path=args.config,
        profile=args.profile,
        profiles_dir=args.profiles_dir,
    )
    service = JiraService(JiraClient(settings.credentials), settings.config)

    if args.command == "healthcheck":
        return service.healthcheck()
    if args.command == "pull":
        return service.pull(query_name=args.query, jql=args.jql, max_results=args.max_results)
    if args.command == "get":
        return service.get(args.issue_key)
    if args.command == "fill":
        return service.fill(
            args.issue_key,
            acceptance_criteria=args.acceptance_criteria,
            business=args.business,
            scope=args.scope,
            qa_notes=args.qa_notes,
            planning_file=args.file,
            dry_run=args.dry_run,
        )
    if args.command == "transition":
        return service.transition(args.issue_key, args.target_state, dry_run=args.dry_run)
    if args.command == "sync-plan":
        return service.sync_plan(args.file, dry_run=args.dry_run)
    if args.command == "comment":
        return service.comment(
            args.issue_key,
            body_text=args.body_text,
            markdown_file=args.markdown_file,
            adf_file=args.adf_file,
            dry_run=args.dry_run,
        )
    raise ValueError(f"Unsupported command: {args.command}")


def _dispatch_profiles(args: argparse.Namespace) -> dict[str, Any]:
    if args.profiles_command == "list":
        profiles = list_profiles(args.profiles_dir)
        return {"status": "ok", "profiles": profiles, "count": len(profiles)}
    if args.profiles_command == "init":
        paths = init_profile(args.name, profiles_dir=args.profiles_dir)
        return {
            "status": "ok",
            "profile": args.name,
            "env_file": str(paths.env_file),
            "config_file": str(paths.config_file),
        }
    raise ValueError(f"Unsupported profiles command: {args.profiles_command}")


def _emit(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return
    if payload.get("status") == "error":
        print(f"{payload['error_code']}: {payload['message']}")
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
