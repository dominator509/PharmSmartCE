from __future__ import annotations

import pytest
from fastapi import FastAPI
from starlette.requests import Request

from app.api.deps import _state


def test_state_helper_rejects_missing_services() -> None:
    request = _make_request(FastAPI(), "/healthz")

    with pytest.raises(RuntimeError):
        _state(request)


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
