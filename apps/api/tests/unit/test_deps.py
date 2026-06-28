from __future__ import annotations

import pytest
from fastapi import FastAPI
from starlette.requests import Request

from app.api.deps import _parse_rate_limit, _state


def test_state_helper_rejects_missing_services() -> None:
    request = _make_request(FastAPI(), "/healthz")

    with pytest.raises(RuntimeError):
        _state(request)


def test_parse_rate_limit_accepts_whitespace_and_case() -> None:
    assert _parse_rate_limit(" 30/MINUTE ") == (30, 60)


@pytest.mark.parametrize(
    "value",
    ["30", "zero/minute", "30/day"],
)
def test_parse_rate_limit_rejects_malformed_values(value: str) -> None:
    with pytest.raises(ValueError):
        _parse_rate_limit(value)


def _make_request(app: FastAPI, path: str) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "raw_path": path.encode("utf-8"),
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
