from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.adapters.storage import LocalSourceStorage
from app.api import install_exception_handlers
from app.api.middleware import RequestIdMiddleware
from app.api.routes import (
    auth_router,
    ce_records_router,
    courses_router,
    health_router,
    sessions_router,
)
from app.config import Settings
from app.observability import configure_observability
from app.services.ingest.service import IngestService
from app.services.rate_limit import RateLimiter


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    Path(settings.storage_root).mkdir(parents=True, exist_ok=True)
    Path(settings.faiss_index_dir).mkdir(parents=True, exist_ok=True)
    app.state.engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    app.state.session_factory = async_sessionmaker(app.state.engine, expire_on_commit=False)
    app.state.storage = LocalSourceStorage(settings.storage_root)
    app.state.rate_limiter = RateLimiter()
    app.state.sentry_state = configure_observability(settings)
    app.state.ingest_service = IngestService(
        session_factory=app.state.session_factory,
        storage=app.state.storage,
    )
    yield
    await app.state.engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    app = FastAPI(title="PharmSmartCE API", lifespan=lifespan)
    app.state.settings = settings or Settings()
    app.state.image_sha = app.state.settings.image_sha
    app.state.llm_ready = True

    install_exception_handlers(app)
    app.add_middleware(
        RequestIdMiddleware,
        app_env=app.state.settings.app_env,
        image_sha=app.state.settings.image_sha,
    )

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(courses_router)
    app.include_router(sessions_router)
    app.include_router(ce_records_router)
    return app


app = create_app()
