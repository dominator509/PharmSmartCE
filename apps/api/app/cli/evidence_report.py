from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping
from pathlib import Path

READINESS_PATH = Path(__file__).resolve().parents[4] / "PRODUCTION_READINESS.md"
EVIDENCE_PATH = Path(__file__).resolve().parents[4] / "PRODUCTION_EVIDENCE.md"


def extract_open_checkboxes(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_section = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current_section = line.removeprefix("## ").strip()
            sections.setdefault(current_section, [])
            continue
        if line.startswith("- [ ] ") and current_section:
            sections.setdefault(current_section, []).append(line.removeprefix("- [ ] ").strip())
    return {section: items for section, items in sections.items() if items}


def extract_todo_rows(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_section = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current_section = line.removeprefix("## ").strip()
            sections.setdefault(current_section, [])
            continue
        if "TODO -" in line and current_section:
            sections.setdefault(current_section, []).append(line.removeprefix("- ").strip())
    return {section: rows for section, rows in sections.items() if rows}


def build_report(
    open_checkboxes: Mapping[str, list[str]],
    todo_rows: Mapping[str, list[str]],
) -> str:
    lines: list[str] = ["# EP-010 Evidence Report", ""]

    lines.append("## Open Readiness Checkboxes")
    if open_checkboxes:
        for section, items in open_checkboxes.items():
            lines.append(f"### {section}")
            for item in items:
                lines.append(f"- [ ] {item}")
            lines.append("")
    else:
        lines.append("- none")
        lines.append("")

    lines.append("## Remaining Evidence Rows")
    if todo_rows:
        for section, rows in todo_rows.items():
            lines.append(f"### {section}")
            for row in rows:
                lines.append(f"- {row}")
            lines.append("")
    else:
        lines.append("- none")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="evidence-report")
    parser.add_argument("--output", type=Path, help="write the report to a file")
    args = parser.parse_args(argv)
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")
    readiness = extract_open_checkboxes(READINESS_PATH.read_text(encoding="utf-8"))
    evidence = extract_todo_rows(EVIDENCE_PATH.read_text(encoding="utf-8"))
    report = build_report(readiness, evidence)
    if args.output is None:
        print(report, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
