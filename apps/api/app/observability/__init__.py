from __future__ import annotations

from app.config import Settings
from app.observability.logging import configure_logging
from app.observability.sentry import SentryState, init_sentry


def configure_observability(settings: Settings) -> SentryState:
    configure_logging(settings.app_env, settings.log_level)
    return init_sentry(settings)
