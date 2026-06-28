from __future__ import annotations

from pathlib import Path

from app.cli.doc_scan import find_todo_markers, iter_document_lines, scan_paths


def test_iter_document_lines_ignores_fenced_code_blocks() -> None:
    text = """\
## One
```md
- [ ] ignored
```
- [ ] alpha
"""

    assert iter_document_lines(text) == ["## One", "- [ ] alpha"]


def test_find_todo_markers_ignores_fenced_code_blocks() -> None:
    text = """\
## One
```md
- TODO ignored
```
TODO counted
"""

    assert find_todo_markers(text) == ["TODO counted"]


def test_scan_paths_ignores_missing_files_and_returns_findings(tmp_path: Path) -> None:
    core_doc = tmp_path / "core.md"
    core_doc.write_text("## Core\nTODO - keep this\n", encoding="utf-8")

    findings = scan_paths([core_doc, tmp_path / "missing.md"])

    assert findings == {str(core_doc): ["TODO - keep this"]}
