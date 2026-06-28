from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from app.config import Settings
from app.main import create_app
from app.repositories.db import Base


def test_password_change_updates_credentials_and_revokes_refresh_tokens(
    tmp_path: Path,
) -> None:
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
            registered = client.post(
                "/auth/register",
                json={"email": "pharmacist@example.com", "password": "secretsecret12"},
            )
            assert registered.status_code == 201

            logged_in = client.post(
                "/auth/login",
                json={"email": "pharmacist@example.com", "password": "secretsecret12"},
            )
            assert logged_in.status_code == 200
            refresh_cookie = client.cookies.get("refresh")
            assert refresh_cookie
            token = logged_in.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            changed = client.patch(
                "/auth/password",
                headers=headers,
                json={
                    "current_password": "secretsecret12",
                    "new_password": "newsecretsecret12",
                },
            )
            assert changed.status_code == 204

            old_login = client.post(
                "/auth/login",
                json={"email": "pharmacist@example.com", "password": "secretsecret12"},
            )
            assert old_login.status_code == 401

            new_login = client.post(
                "/auth/login",
                json={"email": "pharmacist@example.com", "password": "newsecretsecret12"},
            )
            assert new_login.status_code == 200

            stale_refresh = client.post("/auth/refresh", cookies={"refresh": refresh_cookie})
            assert stale_refresh.status_code == 401


async def _prepare_database(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
