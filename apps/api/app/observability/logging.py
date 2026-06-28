from __future__ import annotations

import logging
import sys
from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from typing import Any

import structlog
import structlog.contextvars

REDACT_KEYS = {
    "password",
    "password_hash",
    "authorization",
    "cookie",
    "set-cookie",
    "refresh_token",
    "access_token",
    "jwt",
    "api_key",
    "openai_api_key",
    "s3_secret_access_key",
    "body",
    "request_body",
    "payload",
}


@dataclass(slots=True)
class RedactProcessor:
    redacted_keys: frozenset[str] = frozenset(REDACT_KEYS)

    def __call__(
        self,
        _: structlog.typing.WrappedLogger,
        __: str,
        event_dict: MutableMapping[str, Any],
    ) -> Mapping[str, Any]:
        for key, value in list(event_dict.items()):
            event_dict[key] = _redact_value(value, self.redacted_keys, str(key).lower())
        return event_dict


def configure_logging(app_env: str, log_level: str = "info") -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(message)s",
        force=True,
    )
    renderer: structlog.types.Processor = (
        structlog.dev.ConsoleRenderer(colors=False)
        if app_env in {"local", "test"}
        else structlog.processors.JSONRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
            structlog.processors.add_log_level,
            RedactProcessor(),
            renderer,
        ],
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )


def _redact_value(
    value: object,
    redacted_keys: frozenset[str],
    key_text: str | None = None,
) -> object:
    if key_text is not None and (
        key_text in redacted_keys
        or "password" in key_text
        or "token" in key_text
        or "secret" in key_text
    ):
        return "[REDACTED]"
    if isinstance(value, Mapping):
        redacted: dict[str, object] = {}
        for key, nested_value in value.items():
            redacted[str(key)] = _redact_value(nested_value, redacted_keys, str(key).lower())
        return redacted
    if isinstance(value, list):
        return [_redact_value(item, redacted_keys) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_value(item, redacted_keys) for item in value)
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_redact_value(item, redacted_keys) for item in value]
    return value
