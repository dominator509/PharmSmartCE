from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.api.deps import get_ingest_service
from app.config import Settings
from app.main import create_app
from app.repositories.db import Base
from app.repositories.models.ce_records import CERecordModel
from app.repositories.models.questions import QuestionModel


class FakeIngestService:
    def __init__(self) -> None:
        self.enqueued: list[str] = []

    async def enqueue(self, source_id: str) -> None:
        self.enqueued.append(source_id)


def test_auth_register_login_refresh_and_protected_routes() -> None:
    with tempfile.TemporaryDirectory() as tempdir:
        with PostgresContainer(
            image="postgres:15-alpine",
            username="app",
            password="app",
            dbname="pharm",
            driver="asyncpg",
        ) as postgres:
            database_url = postgres.get_connection_url()
            app = create_app(
                Settings(
                    app_env="test",
                    database_url=database_url,
                    storage_root=str(Path(tempdir) / "uploads"),
                    faiss_index_dir=str(Path(tempdir) / "faiss"),
                )
            )
            fake_ingest = FakeIngestService()
            app.dependency_overrides[get_ingest_service] = lambda: fake_ingest

            async def _prepare_database() -> None:
                engine = create_async_engine(database_url, pool_pre_ping=True)
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                await engine.dispose()

            asyncio.run(_prepare_database())

            client = TestClient(app, base_url="https://testserver")
            with client:
                anonymous = client.get("/api/courses")
                assert anonymous.status_code == 401
                assert anonymous.json()["type"].endswith("unauthenticated")

                registered = client.post(
                    "/auth/register",
                    json={"email": "pharmacist@example.com", "password": "secretsecret12"},
                )
                assert registered.status_code == 201
                assert registered.json()["role"] == "admin"

                logged_in = client.post(
                    "/auth/login",
                    json={"email": "pharmacist@example.com", "password": "secretsecret12"},
                )
                assert logged_in.status_code == 200
                login_body = logged_in.json()
                assert login_body["token_type"] == "Bearer"
                assert login_body["access_token"]
                assert login_body["expires_in"] > 0
                refresh_cookie = client.cookies.get("refresh")
                assert refresh_cookie

                refreshed = client.post("/auth/refresh")
                assert refreshed.status_code == 200
                refresh_body = refreshed.json()
                assert refresh_body["access_token"]
                assert refresh_body["access_token"] != login_body["access_token"]
                rotated_cookie = client.cookies.get("refresh")
                assert rotated_cookie and rotated_cookie != refresh_cookie

                auth_headers = {"Authorization": f"Bearer {refresh_body['access_token']}"}

                created = client.post(
                    "/api/courses",
                    headers=auth_headers,
                    json={"title": "Cardiology CE", "n_questions": 6, "pass_pct": 70},
                )
                assert created.status_code == 201
                course_id = created.json()["id"]

                uploaded = client.post(
                    f"/api/courses/{course_id}/sources",
                    headers=auth_headers,
                    files={
                        "file": (
                            "source.pdf",
                            b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
                            "application/pdf",
                        )
                    },
                )
                assert uploaded.status_code == 202
                source_id = uploaded.json()["id"]
                assert fake_ingest.enqueued == [source_id]

                started = client.post(
                    f"/api/sessions/{course_id}/start",
                    headers=auth_headers,
                )
                assert started.status_code == 201
                session_id = started.json()["id"]

                question_rows = asyncio.run(_load_questions(database_url, session_id))
                assert len(question_rows) >= 6

                for question in question_rows:
                    answer = client.post(
                        f"/api/sessions/{session_id}/answers",
                        headers=auth_headers,
                        json={"question_id": question.id, "chosen_index": question.correct_index},
                    )
                    assert answer.status_code == 200

                session_response = client.get(f"/api/sessions/{session_id}", headers=auth_headers)
                assert session_response.status_code == 200
                assert session_response.json()["status"] == "completed"
                assert session_response.json()["passed"] is True

                record_id = asyncio.run(_load_record_id(database_url, session_id))
                record_meta = client.get(f"/api/ce-records/{record_id}", headers=auth_headers)
                assert record_meta.status_code == 200
                assert record_meta.json()["download_url"] == f"/api/ce-records/{record_id}/download"
                pdf = client.get(record_meta.json()["download_url"], headers=auth_headers)
                assert pdf.status_code == 200
                assert pdf.headers["content-type"].startswith("application/pdf")

                logout = client.post("/auth/logout")
                assert logout.status_code == 204
                stale_refresh = client.post("/auth/refresh", cookies={"refresh": refresh_cookie})
                assert stale_refresh.status_code == 401


async def _load_questions(database_url: str, session_id: str) -> list[QuestionModel]:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        result = await session.execute(
            select(QuestionModel).where(QuestionModel.session_id == session_id)
        )
        rows = list(result.scalars())
    await engine.dispose()
    return rows


async def _load_record_id(database_url: str, session_id: str) -> str:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        result = await session.execute(
            select(CERecordModel).where(CERecordModel.session_id == session_id)
        )
        record_id = result.scalar_one().id
    await engine.dispose()
    return record_id
