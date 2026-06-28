from __future__ import annotations

import asyncio
import time
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from app.api.deps import get_ingest_service
from app.config import Settings
from app.main import create_app
from app.repositories.db import Base
from app.repositories.models.orgs import OrgModel


class FakeIngestService:
    async def enqueue(self, source_id: str) -> None:
        del source_id


def test_session_start_overhead_stays_within_budget(tmp_path: Path) -> None:
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
        app.dependency_overrides[get_ingest_service] = lambda: FakeIngestService()

        with TestClient(app, base_url="https://testserver") as client:
            client.post(
                "/auth/register",
                json={"email": "pharmacist@example.com", "password": "secretsecret12"},
            )
            login = client.post(
                "/auth/login",
                json={"email": "pharmacist@example.com", "password": "secretsecret12"},
            )
            token = login.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            course = client.post(
                "/api/courses",
                headers=headers,
                json={"title": "Cardiology CE", "n_questions": 6, "pass_pct": 70},
            )
            course_id = course.json()["id"]
            client.post(
                f"/api/courses/{course_id}/sources",
                headers=headers,
                files={
                    "file": (
                        "source.pdf",
                        b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
                        "application/pdf",
                    )
                },
            )

            started_at = time.perf_counter()
            started = client.post(f"/api/sessions/{course_id}/start", headers=headers)
            elapsed = time.perf_counter() - started_at

            assert started.status_code == 201
            assert elapsed <= 2.0


async def _prepare_database(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(OrgModel.__table__.insert().values(id="org-1", name="Metro CE"))
    await engine.dispose()
