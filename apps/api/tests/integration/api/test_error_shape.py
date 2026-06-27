from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.errors import (
    AppException,
    AuthError,
    AuthorizationError,
    ConflictError,
    ExternalServiceError,
    GroundingError,
    NotFoundError,
    RateLimitError,
    UnreadyError,
    ValidationError,
)
from app.config import Settings
from app.domain.errors import DomainError
from app.domain.errors import GroundingError as DomainGroundingError
from app.main import create_app


def _build_app() -> FastAPI:
    app = create_app(Settings())

    @app.get("/boom/app/{name}")
    async def boom_app(name: str) -> None:
        mapping: dict[str, AppException] = {
            "not-found": NotFoundError("missing"),
            "auth": AuthError("no auth"),
            "forbidden": AuthorizationError("nope"),
            "validation": ValidationError("bad input"),
            "rate": RateLimitError("slow down"),
            "upstream": ExternalServiceError("upstream exploded"),
            "grounding": GroundingError("bad grounding"),
            "conflict": ConflictError("conflict"),
            "not-ready": UnreadyError("not ready"),
        }
        raise mapping[name]

    @app.get("/boom/domain")
    async def boom_domain() -> None:
        raise DomainError("domain violation")

    @app.get("/boom/domain-grounding")
    async def boom_domain_grounding() -> None:
        raise DomainGroundingError("grounding violation")

    return app


def test_error_shape_matches_problem_json() -> None:
    app = _build_app()
    client = TestClient(app)

    cases = [
        ("/boom/app/not-found", 404, "not-found"),
        ("/boom/app/auth", 401, "unauthenticated"),
        ("/boom/app/forbidden", 403, "forbidden"),
        ("/boom/app/validation", 422, "validation"),
        ("/boom/app/rate", 429, "rate-limited"),
        ("/boom/app/upstream", 502, "upstream"),
        ("/boom/app/grounding", 503, "grounding-failed"),
        ("/boom/app/conflict", 409, "conflict"),
        ("/boom/app/not-ready", 503, "not-ready"),
        ("/boom/domain", 422, "domain-invariant"),
        ("/boom/domain-grounding", 503, "grounding-failed"),
    ]

    for path, status_code, slug in cases:
        response = client.get(path)
        body = response.json()
        assert response.status_code == status_code
        assert response.headers["content-type"].startswith("application/problem+json")
        assert body["type"].endswith(slug)
        assert body["status"] == status_code
        assert body["request_id"]
        assert body["instance"] == path
        assert isinstance(body["detail"], str)
