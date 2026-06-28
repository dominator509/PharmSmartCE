from __future__ import annotations

from contextvars import ContextVar, Token
from collections.abc import Awaitable, Callable
from typing import TypeVar

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.errors import AppException, GroundingError, UnreadyError
from app.domain.errors import DomainError
from app.domain.errors import GroundingError as DomainGroundingError
from app.observability.sentry import capture_exception

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
TException = TypeVar("TException", bound=Exception)


def problem_response(
    request: Request,
    *,
    status_code: int,
    slug: str,
    title: str,
    detail: str,
) -> JSONResponse:
    payload = {
        "type": f"https://pharmsmartce.com/errors/{slug}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": request.url.path,
        "request_id": request_id_var.get() or "",
    }
    return JSONResponse(
        status_code=status_code,
        content=payload,
        media_type="application/problem+json",
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return problem_response(
        request,
        status_code=exc.status_code,
        slug=exc.slug,
        title=exc.title,
        detail=exc.detail,
    )


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    if isinstance(exc, DomainGroundingError):
        return problem_response(
            request,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            slug="grounding-failed",
            title="Grounding Failed",
            detail=str(exc),
        )
    return problem_response(
        request,
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        slug="domain-invariant",
        title="Domain Invariant Violation",
        detail=str(exc),
    )


async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return problem_response(
        request,
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        slug="validation",
        title="Validation Error",
        detail="Request validation failed.",
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    slug = "internal"
    title = "Internal Server Error"
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        slug = "not-found"
        title = "Not Found"
    elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
        slug = "unauthenticated"
        title = "Unauthenticated"
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        slug = "forbidden"
        title = "Forbidden"
    elif exc.status_code == status.HTTP_409_CONFLICT:
        slug = "conflict"
        title = "Conflict"
    elif exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        slug = "rate-limited"
        title = "Rate Limited"
    elif exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        slug = "not-ready"
        title = "Not Ready"

    return problem_response(
        request,
        status_code=exc.status_code,
        slug=slug,
        title=title,
        detail=str(exc.detail) if exc.detail is not None else title,
    )


async def not_implemented_error_handler(request: Request, exc: NotImplementedError) -> JSONResponse:
    return problem_response(
        request,
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        slug="not-implemented",
        title="Not Implemented",
        detail=str(exc) or "Not implemented.",
    )


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    capture_exception(exc)
    return problem_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        slug="internal",
        title="Internal Server Error",
        detail="An unexpected error occurred.",
    )


async def unready_error_handler(request: Request, exc: UnreadyError) -> JSONResponse:
    return problem_response(
        request,
        status_code=exc.status_code,
        slug=exc.slug,
        title=exc.title,
        detail=exc.detail,
    )


def _adapt_exception_handler(
    exc_type: type[TException],
    handler: Callable[[Request, TException], Awaitable[JSONResponse]],
) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    async def wrapper(request: Request, exc: Exception) -> JSONResponse:
        if not isinstance(exc, exc_type):
            raise TypeError(f"Expected {exc_type.__name__}, got {type(exc).__name__}.")
        return await handler(request, exc)

    return wrapper


def install_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        AppException,
        _adapt_exception_handler(AppException, app_exception_handler),
    )
    app.add_exception_handler(
        GroundingError,
        _adapt_exception_handler(GroundingError, app_exception_handler),
    )
    app.add_exception_handler(
        UnreadyError,
        _adapt_exception_handler(UnreadyError, unready_error_handler),
    )
    app.add_exception_handler(DomainError, _adapt_exception_handler(DomainError, domain_error_handler))
    app.add_exception_handler(
        RequestValidationError,
        _adapt_exception_handler(RequestValidationError, request_validation_error_handler),
    )
    app.add_exception_handler(HTTPException, _adapt_exception_handler(HTTPException, http_exception_handler))
    app.add_exception_handler(
        NotImplementedError,
        _adapt_exception_handler(NotImplementedError, not_implemented_error_handler),
    )
    app.add_exception_handler(Exception, _adapt_exception_handler(Exception, exception_handler))


def bind_request_id(request_id: str) -> Token[str | None]:
    return request_id_var.set(request_id)


def reset_request_id(token: Token[str | None]) -> None:
    request_id_var.reset(token)
