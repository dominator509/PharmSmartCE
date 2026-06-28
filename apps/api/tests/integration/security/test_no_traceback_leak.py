from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_uncaught_exceptions_do_not_leak_tracebacks() -> None:
    app = create_app()

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("traceback should not leak")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom")

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.text
    assert "Traceback" not in body
    assert "RuntimeError" not in body
    assert "traceback should not leak" not in body
    assert response.json()["detail"] == "An unexpected error occurred."
