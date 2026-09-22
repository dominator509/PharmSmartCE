#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PATH="$PWD/scripts/bin:$PATH"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.tools/uv-cache}"
export TMP="${TMP:-$PWD/.tools/tmp}"
export TEMP="${TEMP:-$PWD/.tools/tmp}"
export TMPDIR="${TMPDIR:-$PWD/.tools/tmp}"
mkdir -p "$PWD/.tools" "$UV_CACHE_DIR" "$TMP" "$TMPDIR"

uv run --directory apps/api python - "$PWD/PRODUCTION_EVIDENCE.md" <<'PY'
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

required_sections = [
    "Staging / Release",
    "Rollback",
    "Data",
    "Security",
    "Privacy",
    "Performance",
    "Observability",
    "Support / Ops",
    "Launch Gate",
]

ledger_path = Path(sys.argv[1])
lines = ledger_path.read_text(encoding="utf-8").splitlines()

section_rows: dict[str, list[str]] = defaultdict(list)
section_counts: dict[str, int] = defaultdict(int)
current_section = ""

for raw_line in lines:
    line = raw_line.strip()
    if line.startswith("## "):
        current_section = line.removeprefix("## ").strip()
        section_counts[current_section] += 1
        continue
    if current_section and line.startswith(("- ", "* ")):
        section_rows[current_section].append(line[2:].strip())

missing_sections = [section for section in required_sections if section_counts[section] == 0]
duplicate_sections = [section for section, count in section_counts.items() if count > 1]
empty_sections = [section for section in required_sections if not section_rows.get(section)]
duplicate_rows = {
    section: sorted({row for row in rows if rows.count(row) > 1})
    for section, rows in section_rows.items()
    if len(rows) != len(set(rows))
}
placeholder_rows = [
    raw_line.strip()
    for raw_line in lines
    if re.match(r"^- [A-Za-z].*:\s*$", raw_line.strip())
]

required_patterns = {
    "Staging / Release": [
        "Happy path vs staging",
        "Bluegreen verification",
        "Release smoke",
    ],
    "Rollback": [
        "Rollback drill",
        "Rollback verification",
        "DB rollback policy documented in ROLLBACK.md",
        "Customer-impact follow-up",
    ],
    "Data": [
        "Local migration proof",
        "Local integration proof",
        "Backup test-restore",
        "R2 retention evidence",
        "S3 encryption evidence",
    ],
    "Security": [
        "Local security proof",
    ],
    "Privacy": [
        "Uploaded docs SSE-S3 encrypted at rest",
    ],
    "Performance": [
        "Local perf proof",
        "Target-host P95 session-start",
        "Target-host 30-page ingest",
    ],
    "Observability": [
        "Local observability proof",
    ],
    "Support / Ops": [
        "Local incident-response doc check",
        "Local evidence-ledger check",
        "Incident tabletop",
        "Sentry staging/prod evidence",
        "Alerting provider wiring",
    ],
    "Launch Gate": [
        "Human approval comment",
    ],
}

missing_patterns: list[str] = []
for section, patterns in required_patterns.items():
    rows = section_rows.get(section, [])
    for pattern in patterns:
        if not any(pattern in row for row in rows):
            missing_patterns.append(f"{section}: {pattern}")

if missing_sections:
    print(f"ERROR: missing ledger sections: {', '.join(missing_sections)}", file=sys.stderr)
    raise SystemExit(1)
if duplicate_sections:
    print(f"ERROR: duplicate ledger sections: {', '.join(duplicate_sections)}", file=sys.stderr)
    raise SystemExit(1)
if empty_sections:
    print(f"ERROR: empty ledger sections: {', '.join(empty_sections)}", file=sys.stderr)
    raise SystemExit(1)
if duplicate_rows:
    details = ", ".join(
        f"{section} ({'; '.join(rows)})" for section, rows in sorted(duplicate_rows.items())
    )
    print(f"ERROR: duplicate evidence rows detected: {details}", file=sys.stderr)
    raise SystemExit(1)
if placeholder_rows:
    print(
        "ERROR: unresolved placeholder evidence rows: "
        + "; ".join(placeholder_rows),
        file=sys.stderr,
    )
    raise SystemExit(1)
if missing_patterns:
    print(
        "ERROR: required evidence rows missing: " + "; ".join(missing_patterns),
        file=sys.stderr,
    )
    raise SystemExit(1)

print("evidence ledger: ok")
PY
