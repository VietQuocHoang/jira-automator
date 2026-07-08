"""Jira comment utilities — ADF builder and markdown-to-ADF converter."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from jira_tool.client import JiraClient


# ── Low-level ADF node builders ───────────────────────────────────────────────

def _text(t: str, *marks: dict[str, Any]) -> dict[str, Any]:
    node: dict[str, Any] = {"type": "text", "text": t}
    if marks:
        node["marks"] = list(marks)
    return node


def _mark(mark_type: str, **attrs: Any) -> dict[str, Any]:
    m: dict[str, Any] = {"type": mark_type}
    if attrs:
        m["attrs"] = attrs
    return m


def _para(inlines: list[dict[str, Any]]) -> dict[str, Any]:
    return {"type": "paragraph", "content": inlines}


def _heading(level: int, inlines: list[dict[str, Any]]) -> dict[str, Any]:
    return {"type": "heading", "attrs": {"level": level}, "content": inlines}


def _code_block(code: str, language: str = "text") -> dict[str, Any]:
    return {
        "type": "codeBlock",
        "attrs": {"language": language},
        "content": [{"type": "text", "text": code}],
    }


def _bullet_list(items: list[list[dict[str, Any]]]) -> dict[str, Any]:
    return {
        "type": "bulletList",
        "content": [
            {"type": "listItem", "content": [_para(inline)]}
            for inline in items
        ],
    }


def _ordered_list(items: list[list[dict[str, Any]]]) -> dict[str, Any]:
    return {
        "type": "orderedList",
        "content": [
            {"type": "listItem", "content": [_para(inline)]}
            for inline in items
        ],
    }


def _rule() -> dict[str, Any]:
    return {"type": "rule"}


# ── Inline markdown parser ────────────────────────────────────────────────────
# Handles: **bold**, `code`, plain text.

_INLINE_PATTERN = re.compile(r"(\*\*(.+?)\*\*|`([^`]+)`)")


def _parse_inline(text: str) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    pos = 0
    for m in _INLINE_PATTERN.finditer(text):
        if m.start() > pos:
            nodes.append(_text(text[pos:m.start()]))
        if m.group(2) is not None:
            nodes.append(_text(m.group(2), _mark("strong")))
        elif m.group(3) is not None:
            nodes.append(_text(m.group(3), _mark("code")))
        pos = m.end()
    if pos < len(text):
        nodes.append(_text(text[pos:]))
    return nodes or [_text("")]


# ── Markdown-to-ADF converter ─────────────────────────────────────────────────

def markdown_to_adf(md: str) -> dict[str, Any]:
    """Convert a markdown subset to an ADF document.

    Supported constructs:
      # / ## / ### headings
      **bold**, `inline code`
      ``` fenced code blocks (with optional language)
      - / * bullet lists  (nested items not supported)
      1. ordered lists
      --- horizontal rule
      Plain text paragraphs (blank lines separate paragraphs)
    """
    lines = md.splitlines()
    content: list[dict[str, Any]] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # ── Fenced code block ────────────────────────────────────────────────
        if line.startswith("```"):
            lang = line[3:].strip() or "text"
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            content.append(_code_block("\n".join(code_lines), lang))
            i += 1  # skip closing ```
            continue

        # ── Horizontal rule ──────────────────────────────────────────────────
        if re.fullmatch(r"[-*_]{3,}", line.strip()):
            content.append(_rule())
            i += 1
            continue

        # ── Heading ──────────────────────────────────────────────────────────
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            level = min(len(m.group(1)), 6)
            content.append(_heading(level, _parse_inline(m.group(2).strip())))
            i += 1
            continue

        # ── Bullet list ──────────────────────────────────────────────────────
        if re.match(r"^[-*]\s+", line):
            items: list[list[dict[str, Any]]] = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i]):
                items.append(_parse_inline(re.sub(r"^[-*]\s+", "", lines[i])))
                i += 1
            content.append(_bullet_list(items))
            continue

        # ── Ordered list ─────────────────────────────────────────────────────
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                items.append(_parse_inline(re.sub(r"^\d+\.\s+", "", lines[i])))
                i += 1
            content.append(_ordered_list(items))
            continue

        # ── Blank line — skip ────────────────────────────────────────────────
        if not line.strip():
            i += 1
            continue

        # ── Paragraph — collect until a structural break ─────────────────────
        para_lines: list[str] = []
        while i < len(lines):
            cur = lines[i]
            if not cur.strip():
                break
            if (
                cur.startswith("```")
                or re.match(r"^#{1,6}\s", cur)
                or re.match(r"^[-*]\s+", cur)
                or re.match(r"^\d+\.\s+", cur)
                or re.fullmatch(r"[-*_]{3,}", cur.strip())
            ):
                break
            para_lines.append(cur)
            i += 1

        if para_lines:
            content.append(_para(_parse_inline(" ".join(para_lines))))

    return {"type": "doc", "version": 1, "content": content}


# ── Comment API calls ─────────────────────────────────────────────────────────

def post_comment(
    client: JiraClient,
    issue_key: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    """POST a comment ADF body to a Jira issue. Returns the created comment."""
    return client.post(
        f"/rest/api/3/issue/{issue_key}/comment",
        json_body={"body": body},
    )


def load_comment_body(
    *,
    text: str | None = None,
    markdown_file: str | None = None,
    adf_file: str | None = None,
) -> dict[str, Any]:
    """Resolve a comment body from one of three input sources."""
    if sum(x is not None for x in (text, markdown_file, adf_file)) != 1:
        raise ValueError("Provide exactly one of --body, --file, or --adf-file")
    if text is not None:
        return markdown_to_adf(text)
    if markdown_file is not None:
        content = Path(markdown_file).read_text(encoding="utf-8")
        return markdown_to_adf(content)
    import json
    return json.loads(Path(adf_file).read_text(encoding="utf-8"))  # type: ignore[arg-type]
