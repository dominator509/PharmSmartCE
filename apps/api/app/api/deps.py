from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Protocol, runtime_checkable

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.errors import AuthError, AuthorizationError, RateLimitError
from app.config import Settings
from app.repositories.user_repo import UserRepo
from app.services.auth.tokens import verify_access_token
from app.services.ingest.service import IngestService
from app.services.ports.storage import StoragePort
from app.services.rate_limit import RateLimiter


@dataclass(slots=True)
class Principal:
    id: str
    org_id: str
    role: str


@runtime_checkable
class AppState(Protocol):
    settings: Settings
    session_factory: async_sessionmaker[AsyncSession]
    storage: StoragePort
    ingest_service: IngestService
    rate_limiter: RateLimiter


def get_settings(request: Request) -> Settings:
    return _state(request).settings


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with _state(request).session_factory() as session:
        yield session


def get_storage(request: Request) -> StoragePort:
    return _state(request).storage


def get_ingest_service(request: Request) -> IngestService:
    return _state(request).ingest_service


def get_rate_limiter(request: Request) -> RateLimiter:
    return _state(request).rate_limiter


def client_ip(request: Request) -> str:
    if request.client is None or not request.client.host:
        return "unknown"
    return request.client.host


async def current_user(request: Request) -> Principal:
    authorization = request.headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthError("Bearer token required.")

    settings = get_settings(request)
    try:
        claims = verify_access_token(settings.jwt_secret, token)
    except ValueError as exc:
        raise AuthError("Invalid bearer token.") from exc

    async with _state(request).session_factory() as session:
        user = await UserRepo(session).get(claims.user_id)
        if user is None or user.org_id != claims.org_id:
            raise AuthError("Invalid bearer token.")
        principal = Principal(id=user.id, org_id=user.org_id, role=user.role)
        request.state.principal = principal
        return principal


async def current_admin(
    user: Annotated[Principal, Depends(current_user)],
) -> Principal:
    if user.role != "admin":
        raise AuthorizationError("Admin access required.")
    return user


def _parse_rate_limit(value: str) -> tuple[int, int]:
    normalized = value.strip().lower()
    if "/" not in normalized:
        raise ValueError("Rate limit must use '<limit>/<unit>' format.")
    limit_part, unit = normalized.split("/", 1)
    if not limit_part.isdigit() or int(limit_part) <= 0:
        raise ValueError("Rate limit limit must be positive.")
    try:
        window_seconds = {"second": 1, "minute": 60, "hour": 3600}[unit]
    except KeyError as exc:
        raise ValueError("Rate limit unit must be second, minute, or hour.") from exc
    limit = int(limit_part)
    return limit, window_seconds


def _allow_rate_limit(request: Request, *, key: str, limit: int, window_seconds: int) -> None:
    limiter = get_rate_limiter(request)
    if not limiter.allow(key, limit=limit, window_seconds=window_seconds):
        raise RateLimitError("Rate limit exceeded.")


async def require_api_rate_limit(
    request: Request,
    user: Annotated[Principal, Depends(current_user)],
) -> None:
    limit, window_seconds = _parse_rate_limit(get_settings(request).rate_limit_default)
    _allow_rate_limit(
        request,
        key=f"api:{user.id}",
        limit=limit,
        window_seconds=window_seconds,
    )


def _state(request: Request) -> AppState:
    state = request.app.state
    if not isinstance(state, AppState):
        raise RuntimeError("FastAPI app state is missing required services.")
    return state
