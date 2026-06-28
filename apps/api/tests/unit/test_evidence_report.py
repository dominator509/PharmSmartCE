from __future__ import annotations

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
    assert "## Open Readiness Checkboxes" in report
    assert "### Test" in report
    assert "- [ ] one" in report
    assert "## Remaining Evidence Rows" in report
    assert "### Data" in report
    assert "- Foo: TODO - bar" in report
