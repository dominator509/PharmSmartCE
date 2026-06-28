from __future__ import annotations

import asyncio
import tempfile
from base64 import b64encode
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


def test_login_logs_do_not_include_request_body_secrets(capsys) -> None:
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
                    app_env="prod",
                    image_sha="sha-123",
                    jwt_secret=_prod_secret(),
                    refresh_secret=_prod_secret(),
                    database_url=database_url,
                    storage_root=str(Path(tempdir) / "uploads"),
                    faiss_index_dir=str(Path(tempdir) / "faiss"),
                )
            )

            capsys.readouterr()
            with TestClient(app, base_url="https://testserver") as client:
                response = client.post(
                    "/auth/login",
                    json={"email": "pharmacist@example.com", "password": "secretsecret12"},
                )
                assert response.status_code == 200

            captured = capsys.readouterr().err
            assert "secretsecret12" not in captured
            assert '"request_id"' in captured
            assert "image_sha" in captured
            assert "auth/login" in captured or "/auth/login" in captured


async def _prepare_database(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(OrgModel.__table__.insert().values(id="org-1", name="Metro CE"))
        await conn.execute(
            UserModel.__table__.insert().values(
                id="user-1",
                org_id="org-1",
                email="pharmacist@example.com",
                password_hash=hash_password("secretsecret12"),
                role="admin",
            )
        )
    await engine.dispose()


def _prod_secret() -> str:
    return b64encode(b"0123456789abcdef0123456789abcdef").decode("ascii")
