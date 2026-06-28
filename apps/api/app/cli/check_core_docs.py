from __future__ import annotations

import sys
from pathlib import Path

from app.cli.doc_scan import scan_paths

CORE_DOCS = (
    "PROJECT_BRIEF.md",
    "AGENTS.md",
    "COMMANDS.md",
    "ARCHITECTURE.md",
    "ROADMAP.md",
    "DECISIONS.md",
    "PRODUCTION_READINESS.md",
)


def main(argv: list[str] | None = None) -> int:
    del argv
    root = Path(__file__).resolve().parents[4]
    findings = scan_paths(root / doc for doc in CORE_DOCS)
    if not findings:
        return 0

    for path, markers in findings.items():
        for marker in markers:
            print(f"WARNING: unresolved TODO/FIXME in {path}: {marker}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
