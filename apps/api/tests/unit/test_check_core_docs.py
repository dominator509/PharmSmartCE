from __future__ import annotations

from app.cli import check_core_docs


def test_main_returns_zero_when_no_findings(monkeypatch) -> None:
    monkeypatch.setattr(check_core_docs, "scan_paths", lambda paths: {})

    assert check_core_docs.main([]) == 0


def test_main_returns_one_and_reports_findings(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        check_core_docs,
        "scan_paths",
        lambda paths: {"/repo/AGENTS.md": ["TODO should fail"]},
    )

    assert check_core_docs.main([]) == 1
    captured = capsys.readouterr()
    assert "WARNING: unresolved TODO/FIXME in /repo/AGENTS.md: TODO should fail" in captured.err
