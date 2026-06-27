from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_auth_stub_register_returns_problem_json_501() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/auth/register",
        json={"email": "pharmacist@example.com", "password": "secret"},
    )

    assert response.status_code == 501
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["type"].endswith("not-implemented")
    assert body["status"] == 501
    assert body["request_id"]
