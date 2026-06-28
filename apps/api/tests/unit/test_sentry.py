from __future__ import annotations

import sys
from types import SimpleNamespace

from app.config import Settings
from app.observability import sentry as sentry_module


def test_init_sentry_rejects_modules_missing_capture_exception(monkeypatch) -> None:
    monkeypatch.setattr(sentry_module, "_sentry_sdk", None)
    monkeypatch.setitem(sys.modules, "sentry_sdk", SimpleNamespace(init=lambda **kwargs: None))

    state = sentry_module.init_sentry(Settings(sentry_dsn="https://public@example.invalid/1"))

    assert state.enabled is False
    sentry_module.capture_exception(RuntimeError("boom"))
