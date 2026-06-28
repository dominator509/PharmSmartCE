from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request

from app.api.errors import AppException, AuthError, UnreadyError
from app.api.handlers import (
    _adapt_exception_handler,
    app_exception_handler,
    bind_request_id,
    domain_error_handler,
    http_exception_handler,
    install_exception_handlers,
    not_implemented_error_handler,
    problem_response,
    request_validation_error_handler,
    reset_request_id,
    unready_error_handler,
)
from app.domain.errors import DomainError
from app.domain.errors import GroundingError as DomainGroundingError


def test_problem_response_and_request_id_binding() -> None:
    request = _make_request("/boom")
    token = bind_request_id("req-123")
    try:
        response = problem_response(
            request,
            status_code=422,
            slug="validation",
            title="Validation Error",
            detail="bad",
        )
    finally:
        reset_request_id(token)

    body = response.body.decode("utf-8")
    assert '"request_id":"req-123"' in body
    assert response.status_code == 422
    assert response.media_type == "application/problem+json"


def test_exception_handlers_cover_problem_json_branches() -> None:
    request = _make_request("/boom")

    async def _run() -> None:
        app_response = await app_exception_handler(request, AuthError("no auth"))
        assert app_response.status_code == 401

        domain_response = await domain_error_handler(request, DomainError("domain"))
        assert domain_response.status_code == 422

        grounding_response = await domain_error_handler(request, DomainGroundingError("grounding"))
        assert grounding_response.status_code == 503

        validation_response = await request_validation_error_handler(
            request, RequestValidationError([])
        )
        assert validation_response.status_code == 422

        http_responses = [
            await http_exception_handler(
                request,
                HTTPException(status_code=404, detail="missing"),
            ),
            await http_exception_handler(request, HTTPException(status_code=401, detail="auth")),
            await http_exception_handler(
                request,
                HTTPException(status_code=403, detail="forbidden"),
            ),
            await http_exception_handler(
                request,
                HTTPException(status_code=409, detail="conflict"),
            ),
            await http_exception_handler(request, HTTPException(status_code=429, detail="rate")),
            await http_exception_handler(
                request,
                HTTPException(status_code=503, detail="unready"),
            ),
            await http_exception_handler(request, HTTPException(status_code=500, detail=None)),
        ]
        assert [response.status_code for response in http_responses] == [
            404,
            401,
            403,
            409,
            429,
            503,
            500,
        ]

        not_implemented = await not_implemented_error_handler(request, NotImplementedError("todo"))
        assert not_implemented.status_code == 501

        unready = await unready_error_handler(request, UnreadyError("not ready"))
        assert unready.status_code == 503

        adapter = _adapt_exception_handler(AppException, app_exception_handler)
        with pytest.raises(TypeError):
            await adapter(request, ValueError("wrong type"))

    asyncio.run(_run())


def test_install_exception_handlers_wires_all_known_errors() -> None:
    app = FastAPI()
    install_exception_handlers(app)
    assert AppException in app.exception_handlers
    assert DomainError in app.exception_handlers


def _make_request(path: str) -> Request:
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
    }
    return Request(scope)
