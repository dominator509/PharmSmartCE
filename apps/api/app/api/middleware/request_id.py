from __future__ import annotations

import random
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

import structlog
import structlog.contextvars
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.handlers import bind_request_id, reset_request_id
from app.observability.metrics import record_http_request

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def generate_request_id() -> str:
    timestamp_ms = int(datetime.now(UTC).timestamp() * 1000) & ((1 << 48) - 1)
    random_bits = random.getrandbits(80)
    value = (timestamp_ms << 80) | random_bits
    chars = []
    for _ in range(26):
        chars.append(_CROCKFORD[value & 31])
        value >>= 5
    return "".join(reversed(chars))


class RequestIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, *, app_env: str, image_sha: str) -> None:
        super().__init__(app)
        self.app_env = app_env
        self.image_sha = image_sha

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = generate_request_id()
        token = bind_request_id(request_id)
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            app_env=self.app_env,
            image_sha=self.image_sha,
        )
        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-Id"] = request_id
            response.headers["X-Request-ID"] = request_id
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; img-src 'self' data:; connect-src 'self'"
            )
            return response
        finally:
            duration = time.perf_counter() - start
            principal = getattr(request.state, "principal", None)
            user_id = getattr(principal, "id", "") if principal is not None else ""
            org_id = getattr(principal, "org_id", "") if principal is not None else ""
            route = request.url.path
            record_http_request(request.method, route, status_code, duration)
            alert_provider = getattr(request.app.state, "alert_provider", None)
            if status_code >= 500 and alert_provider is not None:
                record = getattr(alert_provider, "record", None)
                if callable(record):
                    record("api_5xx_high")
            structlog.get_logger("http_request").info(
                "http_request",
                request_id=request_id,
                user_id=user_id,
                org_id=org_id,
                route=route,
                method=request.method,
                status=status_code,
                duration_ms=round(duration * 1000, 2),
                app_env=self.app_env,
                image_sha=self.image_sha,
            )
            reset_request_id(token)
            structlog.contextvars.clear_contextvars()
