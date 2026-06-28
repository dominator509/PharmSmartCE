from __future__ import annotations

import asyncio
import sys
import tempfile
from base64 import b64encode
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from app.config import Settings
from app.main import create_app
from app.repositories.db import Base


def test_sentry_initializes_and_captures_exceptions(monkeypatch) -> None:
    fake_sentry = SimpleNamespace(init_calls=[], captured=[])

    def init(**kwargs):
        fake_sentry.init_calls.append(kwargs)

    def capture_exception(exc):
        fake_sentry.captured.append(exc)

    fake_sentry.init = init
    fake_sentry.capture_exception = capture_exception
    monkeypatch.setitem(sys.modules, "sentry_sdk", fake_sentry)

    with tempfile.TemporaryDirectory() as tempdir:
        with PostgresContainer(
            image="postgres:15-alpine",
            username="app",
            password="app",
            dbname="pharm",
            driver="asyncpg",
        ) as postgres:
            database_url = postgres.get_connection_url()
            asyncio.run(_prepare_database(database_url))
            app = create_app(
                Settings(
                    app_env="staging",
                    image_sha="sha-abc",
                    sentry_dsn="https://public@example.invalid/1",
                    jwt_secret=_staging_secret(),
                    refresh_secret=_staging_secret(),
                    database_url=database_url,
                    storage_root=str(Path(tempdir) / "uploads"),
                    faiss_index_dir=str(Path(tempdir) / "faiss"),
                )
            )

            @app.get("/boom")
            async def boom() -> None:
                raise RuntimeError("synthetic exception")

            with TestClient(app, raise_server_exceptions=False) as client:
                response = client.get("/boom")

            assert response.status_code == 500
            assert fake_sentry.init_calls
            assert fake_sentry.init_calls[0]["dsn"] == "https://public@example.invalid/1"
            assert fake_sentry.init_calls[0]["environment"] == "staging"
            assert fake_sentry.captured and isinstance(fake_sentry.captured[0], RuntimeError)


async def _prepare_database(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


def _staging_secret() -> str:
    return b64encode(b"0123456789abcdef0123456789abcdef").decode("ascii")
