from __future__ import annotations

from app.cli import evidence_report
from app.cli.evidence_report import build_report, extract_open_checkboxes, extract_todo_rows


def test_extract_open_checkboxes_groups_by_section() -> None:
    text = """\
## One
- [ ] alpha
- [x] done

## Two
- [ ] beta
"""

    assert extract_open_checkboxes(text) == {"One": ["alpha"], "Two": ["beta"]}


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


def test_build_report_renders_markdown_sections() -> None:
    report = build_report({"Test": ["one"]}, {"Data": ["- Foo: TODO - bar"]})

    assert "# EP-010 Evidence Report" in report
    assert "## Summary" in report
    assert "- Open readiness items: 1 across 1 sections" in report
    assert "- Remaining evidence rows: 1 across 1 sections" in report
    assert "## Open Readiness Checkboxes" in report
    assert "### Test" in report
    assert "- [ ] one" in report
    assert "## Remaining Evidence Rows" in report
    assert "### Data" in report
    assert "- Foo: TODO - bar" in report


def test_main_writes_output_file(tmp_path) -> None:
    readiness = tmp_path / "readiness.md"
    evidence = tmp_path / "evidence.md"
    output = tmp_path / "report.md"
    readiness.write_text("## One\n- [ ] alpha\n", encoding="utf-8")
    evidence.write_text("## Two\n- Beta: TODO - gamma\n", encoding="utf-8")

    original_readiness = evidence_report.READINESS_PATH
    original_evidence = evidence_report.EVIDENCE_PATH
    evidence_report.READINESS_PATH = readiness
    evidence_report.EVIDENCE_PATH = evidence
    try:
        assert evidence_report.main(["--output", str(output)]) == 0
    finally:
        evidence_report.READINESS_PATH = original_readiness
        evidence_report.EVIDENCE_PATH = original_evidence

    assert output.read_text(encoding="utf-8") == (
        "# EP-010 Evidence Report\n\n"
        "## Summary\n"
        "- Open readiness items: 1 across 1 sections\n"
        "- Remaining evidence rows: 1 across 1 sections\n\n"
        "## Open Readiness Checkboxes\n"
        "### One\n"
        "- [ ] alpha\n\n"
        "## Remaining Evidence Rows\n"
        "### Two\n"
        "- Beta: TODO - gamma\n"
    )
