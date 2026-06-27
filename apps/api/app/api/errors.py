from __future__ import annotations


class AppException(Exception):
    status_code = 500
    slug = "internal"
    title = "Internal Server Error"

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail or self.title)
        self.detail = detail or self.title


class NotFoundError(AppException):
    status_code = 404
    slug = "not-found"
    title = "Not Found"


class AuthError(AppException):
    status_code = 401
    slug = "unauthenticated"
    title = "Unauthenticated"


class AuthorizationError(AppException):
    status_code = 403
    slug = "forbidden"
    title = "Forbidden"


class ValidationError(AppException):
    status_code = 422
    slug = "validation"
    title = "Validation Error"


class RateLimitError(AppException):
    status_code = 429
    slug = "rate-limited"
    title = "Rate Limited"


class ExternalServiceError(AppException):
    status_code = 502
    slug = "upstream"
    title = "Upstream Service Error"


class GroundingError(AppException):
    status_code = 503
    slug = "grounding-failed"
    title = "Grounding Failed"


class ConflictError(AppException):
    status_code = 409
    slug = "conflict"
    title = "Conflict"


class UnreadyError(AppException):
    status_code = 503
    slug = "not-ready"
    title = "Not Ready"
