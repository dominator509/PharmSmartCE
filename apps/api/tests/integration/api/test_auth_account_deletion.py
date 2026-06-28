from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from app.config import Settings
from app.main import create_app
from app.repositories.db import Base
from app.repositories.models.orgs import OrgModel
from app.repositories.models.users import UserModel


def test_account_deletion_removes_last_user_and_org(tmp_path: Path) -> None:
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

            deleted = client.delete("/auth/account", headers=headers)
            assert deleted.status_code == 204
            assert client.cookies.get("refresh") is None

            client.cookies.set("refresh", refresh_cookie, path="/auth")
            stale_refresh = client.post("/auth/refresh")
            assert stale_refresh.status_code == 401

            protected = client.get("/api/courses", headers=headers)
            assert protected.status_code == 401

            relogin = client.post(
                "/auth/login",
                json={"email": "pharmacist@example.com", "password": "secretsecret12"},
            )
            assert relogin.status_code == 401

            users, orgs = asyncio.run(_count_org_rows(database_url))
            assert users == 0
            assert orgs == 0


async def _prepare_database(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def _count_org_rows(database_url: str) -> tuple[int, int]:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        users = await conn.scalar(select(func.count(UserModel.id)))
        orgs = await conn.scalar(select(func.count(OrgModel.id)))
    await engine.dispose()
    return int(users or 0), int(orgs or 0)
