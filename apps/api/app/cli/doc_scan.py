from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import re

TODO_MARKER_PATTERN = re.compile(r"\b(?:TODO|FIXME)\b")
INLINE_CODE_PATTERN = re.compile(r"`[^`]*`")


def iter_document_lines(text: str) -> list[str]:
    lines: list[str] = []
    in_fenced_block = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(("```", "~~~")):
            in_fenced_block = not in_fenced_block
            continue
        if in_fenced_block:
            continue
        lines.append(line)
    return lines


def find_todo_markers(text: str) -> list[str]:
    markers: list[str] = []
    for line in iter_document_lines(text):
        if TODO_MARKER_PATTERN.search(strip_inline_code_spans(line)):
            markers.append(line)
    return markers


def strip_inline_code_spans(text: str) -> str:
    return INLINE_CODE_PATTERN.sub("", text)


def unwrap_inline_code(text: str) -> str:
    if len(text) >= 2 and text.startswith("`") and text.endswith("`"):
        return text[1:-1]
    return text


def scan_paths(paths: Iterable[Path]) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    for path in paths:
        if not path.exists():
            continue
        markers = find_todo_markers(path.read_text(encoding="utf-8"))
        if markers:
            findings[str(path)] = markers
    return findings
