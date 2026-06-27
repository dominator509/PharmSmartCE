from __future__ import annotations

import json
from pathlib import Path

from app.main import create_app


def test_openapi_snapshot_matches_committed_spec() -> None:
    snapshot = Path("openapi.json")
    current = create_app().openapi()

    assert snapshot.exists()
    assert json.loads(snapshot.read_text(encoding="utf-8")) == current
