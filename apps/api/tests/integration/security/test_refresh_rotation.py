from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from app.config import Settings
from app.main import create_app
from app.repositories.db import Base


def test_refresh_rotation_revokes_the_stale_chain(tmp_path: Path) -> None:
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
                app_env="test",
                database_url=database_url,
                storage_root=str(tmp_path / "uploads"),
                faiss_index_dir=str(tmp_path / "faiss"),
            )
        )

        with TestClient(app, base_url="https://testserver") as client:
            client.post(
                "/auth/register",
                json={"email": "pharmacist@example.com", "password": "secretsecret12"},
            )
            first_login = client.post(
                "/auth/login",
                json={"email": "pharmacist@example.com", "password": "secretsecret12"},
            )
            assert first_login.status_code == 200
            original_refresh = client.cookies.get("refresh")
            assert original_refresh

            first_refresh = client.post("/auth/refresh")
            assert first_refresh.status_code == 200
            rotated_refresh = client.cookies.get("refresh")
            assert rotated_refresh and rotated_refresh != original_refresh

            client.cookies.set("refresh", original_refresh, path="/auth")
            stale_refresh = client.post("/auth/refresh")
            assert stale_refresh.status_code == 401

            revived_refresh = client.post("/auth/refresh")
            assert revived_refresh.status_code == 401


async def _prepare_database(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
