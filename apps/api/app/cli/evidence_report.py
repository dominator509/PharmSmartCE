from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Mapping
from pathlib import Path

READINESS_PATH = Path(__file__).resolve().parents[4] / "PRODUCTION_READINESS.md"
EVIDENCE_PATH = Path(__file__).resolve().parents[4] / "PRODUCTION_EVIDENCE.md"
EXECPLAN_PATH = Path(__file__).resolve().parents[4] / ".agent" / "execplans" / "EP-010-production-readiness.md"
MILESTONE_PROGRESS_PATTERN = re.compile(r"^- \[(?P<checked>[ x])\] (?P<id>M\d+): (?P<summary>.+)$")


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
        if current_section and line.startswith(("- ", "* ")) and "TODO -" in line:
            sections.setdefault(current_section, []).append(line[2:].strip())
    return {section: rows for section, rows in sections.items() if rows}


def extract_verified_rows(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_section = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current_section = line.removeprefix("## ").strip()
            sections.setdefault(current_section, [])
            continue
        if current_section and line.startswith(("- ", "* ")) and "TODO -" not in line:
            sections.setdefault(current_section, []).append(line[2:].strip())
    return {section: rows for section, rows in sections.items() if rows}


def extract_execplan_milestones(text: str) -> list[dict[str, str]]:
    milestones: dict[str, dict[str, str]] = {}
    current_milestone = ""
    mode = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == "## 8. Milestones":
            mode = "milestones"
            current_milestone = ""
            continue
        if line == "## 12. Progress":
            mode = "progress"
            current_milestone = ""
            continue
        if line.startswith("## "):
            mode = ""
            current_milestone = ""
            continue
        if mode == "milestones" and line.startswith("### M"):
            milestone_id, title = line.removeprefix("### ").split(": ", 1)
            milestones[milestone_id] = {
                "id": milestone_id,
                "title": title,
                "status": "open",
                "validation": "",
                "expected": "",
            }
            current_milestone = milestone_id
            continue
        if mode == "milestones" and current_milestone:
            if line.startswith("- **Validation command:** "):
                milestones[current_milestone]["validation"] = line.removeprefix(
                    "- **Validation command:** "
                ).strip()
            elif line.startswith("- **Expected result:** "):
                milestones[current_milestone]["expected"] = line.removeprefix(
                    "- **Expected result:** "
                ).strip()
            continue
        if mode == "progress":
            match = MILESTONE_PROGRESS_PATTERN.match(line)
            if match:
                milestone_id = match.group("id")
                milestone = milestones.setdefault(
                    milestone_id,
                    {
                        "id": milestone_id,
                        "title": match.group("summary").strip(),
                        "status": "open",
                        "validation": "",
                        "expected": "",
                    },
                )
                if not milestone["title"]:
                    milestone["title"] = match.group("summary").strip()
                milestone["status"] = "done" if match.group("checked") == "x" else "open"
    return sorted(milestones.values(), key=lambda milestone: int(milestone["id"].removeprefix("M")))


def build_report(
    open_checkboxes: Mapping[str, list[str]],
    todo_rows: Mapping[str, list[str]],
    verified_rows: Mapping[str, list[str]],
    milestones: list[dict[str, str]],
) -> str:
    open_item_count = sum(len(items) for items in open_checkboxes.values())
    todo_item_count = sum(len(rows) for rows in todo_rows.values())
    verified_item_count = sum(len(rows) for rows in verified_rows.values())
    completed_milestone_count = sum(1 for milestone in milestones if milestone["status"] == "done")
    lines: list[str] = ["# EP-010 Evidence Report", ""]

    lines.append("## Summary")
    lines.append(
        f"- Open readiness items: {open_item_count} across " f"{len(open_checkboxes)} sections"
    )
    lines.append(
        f"- Remaining evidence rows: {todo_item_count} across " f"{len(todo_rows)} sections"
    )
    lines.append(
        f"- Verified evidence rows: {verified_item_count} across {len(verified_rows)} sections"
    )
    lines.append(
        f"- EP-010 milestones complete: {completed_milestone_count} across {len(milestones)} milestones"
    )
    lines.append("")

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

    lines.append("## Verified Evidence Rows")
    if verified_rows:
        for section, rows in verified_rows.items():
            lines.append(f"### {section}")
            for row in rows:
                lines.append(f"- {row}")
            lines.append("")
    else:
        lines.append("- none")
        lines.append("")

    lines.append("## EP-010 Milestones")
    if milestones:
        for milestone in milestones:
            validation = milestone["validation"] or "n/a"
            line = f"- {milestone['id']} [{milestone['status']}] `{validation}`"
            if milestone["expected"]:
                line += f" -> {milestone['expected']}"
            lines.append(line)
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
    parser.add_argument(
        "--output",
        type=Path,
        help="write the report to a file",
    )
    args = parser.parse_args(argv)
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")
    readiness = extract_open_checkboxes(READINESS_PATH.read_text(encoding="utf-8"))
    evidence = extract_todo_rows(EVIDENCE_PATH.read_text(encoding="utf-8"))
    verified = extract_verified_rows(EVIDENCE_PATH.read_text(encoding="utf-8"))
    milestones = extract_execplan_milestones(EXECPLAN_PATH.read_text(encoding="utf-8"))
    report = build_report(readiness, evidence, verified, milestones)
    if args.output is None:
        print(report, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
