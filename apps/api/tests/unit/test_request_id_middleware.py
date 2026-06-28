from __future__ import annotations

from fastapi import FastAPI
from starlette.requests import Request

from app.api.middleware.request_id import _record_alert


class _FakeAlertProvider:
    def __init__(self) -> None:
        self.alerts: list[str] = []

    def record(self, alert_name: str) -> None:
        self.alerts.append(alert_name)


def test_record_alert_is_noop_without_provider() -> None:
    request = _make_request(FastAPI())

    _record_alert(request)


def test_record_alert_uses_alert_provider_protocol() -> None:
    app = FastAPI()
    app.state.alert_provider = _FakeAlertProvider()
    request = _make_request(app)

    _record_alert(request)

    assert app.state.alert_provider.alerts == ["api_5xx_high"]


def _make_request(app: FastAPI) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/boom",
        "raw_path": b"/boom",
        "root_path": "",
        "scheme": "https",
        "query_string": b"",
        "headers": [],
        "client": ("testclient", 12345),
        "server": ("testserver", 443),
        "http_version": "1.1",
        "app": app,
    }
    return Request(scope)
