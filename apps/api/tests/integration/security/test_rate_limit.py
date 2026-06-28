from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from app.config import Settings
from app.main import create_app
from app.repositories.db import Base
from app.repositories.models.orgs import OrgModel
from app.repositories.models.users import UserModel
from app.services.auth.tokens import hash_password


def test_auth_and_api_rate_limits_enforced(tmp_path: Path) -> None:
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
            _register(client, "pharmacist@example.com")
            _register(client, "rate-limit@example.com")
            _assert_login_rate_limit(client, "rate-limit@example.com")
            _assert_register_rate_limit(client, start=3)

            token = _login(client, "pharmacist@example.com")
            headers = {"Authorization": f"Bearer {token}"}
            for _ in range(30):
                response = client.get("/api/courses", headers=headers)
                assert response.status_code == 200
            blocked = client.get("/api/courses", headers=headers)
            assert blocked.status_code == 429
            assert blocked.json()["type"].endswith("rate-limited")


def _assert_login_rate_limit(client: TestClient, email: str) -> None:
    for _ in range(4):
        response = client.post(
            "/auth/login",
            json={"email": email, "password": "secretsecret12"},
        )
        assert response.status_code == 200

    blocked = client.post(
        "/auth/login",
        json={"email": email, "password": "secretsecret12"},
    )
    assert blocked.status_code == 429
    assert blocked.json()["type"].endswith("rate-limited")


def _assert_register_rate_limit(client: TestClient, *, start: int) -> None:
    for index in range(start, 6):
        response = client.post(
            "/auth/register",
            json={"email": f"user{index}@example.com", "password": "secretsecret12"},
        )

        assert response.status_code == 201

    blocked = client.post(
        "/auth/register",
        json={"email": "user6@example.com", "password": "secretsecret12"},
    )
    assert blocked.status_code == 429
    assert blocked.json()["type"].endswith("rate-limited")


def _login(client: TestClient, email: str) -> str:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": "secretsecret12"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _register(client: TestClient, email: str) -> None:
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "secretsecret12"},
    )
    assert response.status_code == 201


async def _prepare_database(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(OrgModel.__table__.insert().values(id="org-1", name="Metro CE"))
        await conn.execute(
            UserModel.__table__.insert().values(
                id="user-1",
                org_id="org-1",
                email="admin@example.com",
                password_hash=hash_password("secretsecret12"),
                role="admin",
            )
        )
    await engine.dispose()
