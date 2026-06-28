from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import client_ip, get_rate_limiter
from app.api.errors import AuthError, RateLimitError
from app.observability.metrics import record_auth_login_attempt
from app.services.auth.service import AuthService

router = APIRouter(prefix="/auth")


class RegisterDTO(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=12)


class LoginDTO(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=12)


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    email: str
    role: str
    created_at: datetime


class AccessTokenDTO(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


def _auth_service(request: Request, session: AsyncSession) -> AuthService:
    return AuthService(session=session, settings=request.app.state.settings)


def _set_refresh_cookie(response: Response, request: Request, cookie_value: str) -> None:
    response.set_cookie(
        key="refresh",
        value=cookie_value,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/auth",
        max_age=request.app.state.settings.refresh_token_ttl_days * 24 * 60 * 60,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key="refresh", path="/auth")


def _allow_login(request: Request, email: str) -> None:
    limiter = get_rate_limiter(request)
    ip = client_ip(request)
    if not limiter.allow(f"auth:login:ip:{ip}", limit=10, window_seconds=60):
        record_auth_login_attempt("rate_limited")
        raise RateLimitError("Too many login attempts.")
    if not limiter.allow(
        f"auth:login:email:{email.lower()}",
        limit=4,
        window_seconds=60,
    ):
        record_auth_login_attempt("rate_limited")
        raise RateLimitError("Too many login attempts.")


def _allow_register(request: Request) -> None:
    limiter = get_rate_limiter(request)
    ip = client_ip(request)
    if not limiter.allow(f"auth:register:ip:{ip}", limit=5, window_seconds=60):
        raise RateLimitError("Too many registration attempts.")


@router.post("/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterDTO, request: Request) -> UserDTO:
    _allow_register(request)
    async with request.app.state.session_factory() as session:
        user = await _auth_service(request, session).register(payload.email, payload.password)
        return UserDTO(
            id=user.id,
            org_id=user.org_id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        )


@router.post("/login", response_model=AccessTokenDTO)
async def login(payload: LoginDTO, request: Request, response: Response) -> AccessTokenDTO:
    _allow_login(request, payload.email)
    async with request.app.state.session_factory() as session:
        try:
            auth = await _auth_service(request, session).login(payload.email, payload.password)
        except AuthError as exc:
            outcome = (
                "unknown_user" if "Invalid email or password." in exc.detail else "bad_password"
            )
            record_auth_login_attempt(outcome)
            raise
        _set_refresh_cookie(response, request, auth.refresh_cookie)
        record_auth_login_attempt("success")
        return AccessTokenDTO(access_token=auth.access_token, expires_in=auth.expires_in)


@router.post("/refresh", response_model=AccessTokenDTO)
async def refresh(request: Request, response: Response) -> AccessTokenDTO:
    refresh_cookie = request.cookies.get("refresh")
    if not refresh_cookie:
        raise AuthError("Refresh cookie required.")

    async with request.app.state.session_factory() as session:
        auth = await _auth_service(request, session).refresh(refresh_cookie)
        _set_refresh_cookie(response, request, auth.refresh_cookie)
        return AccessTokenDTO(access_token=auth.access_token, expires_in=auth.expires_in)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response) -> Response:
    refresh_cookie = request.cookies.get("refresh")
    if not refresh_cookie:
        raise AuthError("Refresh cookie required.")

    async with request.app.state.session_factory() as session:
        await _auth_service(request, session).logout(refresh_cookie)
        _clear_refresh_cookie(response)
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
