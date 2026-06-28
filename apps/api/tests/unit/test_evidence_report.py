from __future__ import annotations

from app.cli import evidence_report
from app.cli.evidence_report import (
    build_report,
    extract_execplan_milestones,
    extract_open_checkboxes,
    extract_verified_rows,
    extract_todo_rows,
)


def test_extract_open_checkboxes_groups_by_section() -> None:
    text = """\
## One
- [ ] alpha
- [x] done

## Two
- [ ] beta
"""

    assert extract_open_checkboxes(text) == {"One": ["alpha"], "Two": ["beta"]}


def test_extract_open_checkboxes_ignores_fenced_code_blocks() -> None:
    text = """\
## One
```md
- [ ] ignored
```
- [ ] alpha
"""

    assert extract_open_checkboxes(text) == {"One": ["alpha"]}


def test_extract_todo_rows_uses_sections() -> None:
    text = """\
## A
- Foo: TODO - do thing

## B
- Bar: TODO - do other thing
"""

    assert extract_todo_rows(text) == {
        "A": ["Foo: TODO - do thing"],
        "B": ["Bar: TODO - do other thing"],
    }


def test_extract_todo_rows_ignores_non_bullets() -> None:
    text = """\
## A
This line mentions TODO - but is not a bullet.
* Baz: TODO - still counted
"""

    assert extract_todo_rows(text) == {"A": ["Baz: TODO - still counted"]}


def test_extract_todo_rows_ignores_fenced_code_blocks() -> None:
    text = """\
## A
```md
- Foo: TODO - ignored
```
- Bar: TODO - counted
"""

    assert extract_todo_rows(text) == {"A": ["Bar: TODO - counted"]}


def test_extract_verified_rows_uses_sections() -> None:
    text = """\
## A
- verified line
* another verified line
- TODO - ignored
"""

    assert extract_verified_rows(text) == {
        "A": ["verified line", "another verified line"],
    }


def test_extract_verified_rows_ignores_fenced_code_blocks() -> None:
    text = """\
## A
```md
- verified line in code block
```
- verified line
"""

    assert extract_verified_rows(text) == {"A": ["verified line"]}


def test_extract_execplan_milestones_reads_status_and_commands() -> None:
    text = """\
## 8. Milestones

### M1: Functional category audit
- **Validation command:** `pnpm --filter web test:e2e -- happy_path.spec.ts --grep '@staging'`
- **Expected result:** All happy-path tests pass against staging.

### M2: Test category audit
- **Validation command:** `scripts/verify.sh && uv run --directory apps/api pytest --cov-fail-under=80 -q && uv run --directory apps/api pytest tests/integration/test_generation_golden.py -q`
- **Expected result:** verify exit 0; backend coverage >= 80%; golden-set thresholds met.

## 12. Progress
- [ ] M1: Functional category audit
- [x] M2: Test category audit - 2026-06-27T19:00Z - done
"""

    assert extract_execplan_milestones(text) == [
        {
            "id": "M1",
            "title": "Functional category audit",
            "status": "open",
            "validation": "`pnpm --filter web test:e2e -- happy_path.spec.ts --grep '@staging'`",
            "expected": "All happy-path tests pass against staging.",
        },
        {
            "id": "M2",
            "title": "Test category audit",
            "status": "done",
            "validation": "`scripts/verify.sh && uv run --directory apps/api pytest --cov-fail-under=80 -q && uv run --directory apps/api pytest tests/integration/test_generation_golden.py -q`",
            "expected": "verify exit 0; backend coverage >= 80%; golden-set thresholds met.",
        },
    ]


def test_build_report_renders_markdown_sections() -> None:
    report = build_report(
        {"Test": ["one"]},
        {"Data": ["- Foo: TODO - bar"]},
        {"Data": ["local proof"], "Security": ["security proof"]},
        [
            {
                "id": "M1",
                "title": "Functional category audit",
                "status": "open",
                "validation": "cmd-one",
                "expected": "All happy-path tests pass against staging.",
            },
            {
                "id": "M2",
                "title": "Test category audit",
                "status": "done",
                "validation": "cmd-two",
                "expected": "verify exit 0; backend coverage >= 80%; golden-set thresholds met.",
            },
        ],
    )

    assert "# EP-010 Evidence Report" in report
    assert "## Summary" in report
    assert "- Open readiness items: 1 across 1 sections" in report
    assert "- Remaining evidence rows: 1 across 1 sections" in report
    assert "- Verified evidence rows: 2 across 2 sections" in report
    assert "- EP-010 milestones complete: 1 across 2 milestones" in report
    assert "## Open Readiness Checkboxes" in report
    assert "### Test" in report
    assert "- [ ] one" in report
    assert "## Verified Evidence Rows" in report
    assert "### Data" in report
    assert "- local proof" in report
    assert "### Security" in report
    assert "- security proof" in report
    assert "## EP-010 Milestones" in report
    assert "- M1 [open] `cmd-one` -> All happy-path tests pass against staging." in report
    assert (
        "- M2 [done] `cmd-two` -> verify exit 0; backend coverage >= 80%; golden-set thresholds met."
        in report
    )
    assert "## Remaining Evidence Rows" in report
    assert "### Data" in report
    assert "- Foo: TODO - bar" in report


def test_main_writes_output_file(tmp_path) -> None:
    readiness = tmp_path / "readiness.md"
    evidence = tmp_path / "evidence.md"
    execplan = tmp_path / "execplan.md"
    output = tmp_path / "report.md"
    readiness.write_text("## One\n- [ ] alpha\n", encoding="utf-8")
    evidence.write_text("## Two\n- Beta: TODO - gamma\n", encoding="utf-8")
    execplan.write_text(
        """\
## 8. Milestones

### M1: Functional category audit
- **Validation command:** `cmd-one`
- **Expected result:** ready

## 12. Progress
- [x] M1: Functional category audit - complete
""",
        encoding="utf-8",
    )

    original_readiness = evidence_report.READINESS_PATH
    original_evidence = evidence_report.EVIDENCE_PATH
    original_execplan = evidence_report.EXECPLAN_PATH
    evidence_report.READINESS_PATH = readiness
    evidence_report.EVIDENCE_PATH = evidence
    evidence_report.EXECPLAN_PATH = execplan
    try:
        assert evidence_report.main(["--output", str(output)]) == 0
    finally:
        evidence_report.READINESS_PATH = original_readiness
        evidence_report.EVIDENCE_PATH = original_evidence
        evidence_report.EXECPLAN_PATH = original_execplan

    assert output.read_text(encoding="utf-8") == (
        "# EP-010 Evidence Report\n\n"
        "## Summary\n"
        "- Open readiness items: 1 across 1 sections\n"
        "- Remaining evidence rows: 1 across 1 sections\n\n"
        "- Verified evidence rows: 0 across 0 sections\n"
        "- EP-010 milestones complete: 1 across 1 milestones\n\n"
        "## Open Readiness Checkboxes\n"
        "### One\n"
        "- [ ] alpha\n\n"
        "## Verified Evidence Rows\n"
        "- none\n\n"
        "## EP-010 Milestones\n"
        "- M1 [done] `cmd-one` -> ready\n\n"
        "## Remaining Evidence Rows\n"
        "### Two\n"
        "- Beta: TODO - gamma\n"
    )
