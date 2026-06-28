from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any

from app.config import Settings

_sentry_sdk: Any = None


@dataclass(slots=True)
class SentryState:
    enabled: bool


def init_sentry(settings: Settings) -> SentryState:
    global _sentry_sdk
    if not settings.sentry_dsn:
        return SentryState(enabled=False)

    try:
        _sentry_sdk = importlib.import_module("sentry_sdk")
    except ModuleNotFoundError:
        return SentryState(enabled=False)

    _sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.app_env,
        before_send=_before_send,
    )
    return SentryState(enabled=True)


def capture_exception(exc: BaseException) -> None:
    if _sentry_sdk is None:
        return
    _sentry_sdk.capture_exception(exc)


def _before_send(event: dict[str, object], _: dict[str, object] | None) -> dict[str, object]:
    request = event.get("request")
    if isinstance(request, dict):
        request.pop("cookies", None)
        headers = request.get("headers")
        if isinstance(headers, dict):
            for key in ("authorization", "cookie", "set-cookie"):
                headers.pop(key, None)
    event.pop("exception", None)
    return event
