from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.deps import Principal, current_admin, current_user
from app.config import Settings
from app.main import create_app
from app.repositories.db import Base
from app.repositories.models.ce_records import CERecordModel
from app.repositories.models.chunks import ChunkModel
from app.repositories.models.orgs import OrgModel
from app.repositories.models.questions import QuestionModel
from app.repositories.models.users import UserModel
from testcontainers.postgres import PostgresContainer


def test_session_routes_answer_and_pdf(tmp_path: Path) -> None:
    with PostgresContainer(
        image="postgres:15-alpine",
        username="app",
        password="app",
        dbname="pharm",
        driver="asyncpg",
    ) as postgres:
        asyncio.run(_prepare_database(postgres.get_connection_url()))
        app = create_app(
            Settings(
                database_url=postgres.get_connection_url(),
                storage_root=str(tmp_path / "uploads"),
                faiss_index_dir=str(tmp_path / "faiss"),
            )
        )
        principal = Principal(id="user-1", org_id="org-1", role="admin")
        app.dependency_overrides[current_user] = lambda: principal
        app.dependency_overrides[current_admin] = lambda: principal

        with TestClient(app) as client:
            created = client.post(
                "/api/courses",
                json={"title": "Cardiology CE", "n_questions": 6, "pass_pct": 70},
            )
            course_id = created.json()["id"]

            upload = client.post(
                f"/api/courses/{course_id}/sources",
                files={
                    "file": (
                        "source.pdf",
                        b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
                        "application/pdf",
                    )
                },
            )
            source_id = upload.json()["id"]

            started = client.post(f"/api/sessions/{course_id}/start")
            assert started.status_code == 201
            session_id = started.json()["id"]
            questions = started.json()["questions"]
            assert len(questions) == 6
            assert questions[0]["citation"]["url"].startswith(
                f"/sessions/{session_id}?cite={source_id}:"
            )

            citation_preview = client.get(
                f"/api/sessions/{session_id}/citation",
                params={
                    "doc_id": source_id,
                    "page": questions[0]["citation"]["page"],
                    "span": questions[0]["citation"]["span"],
                },
            )
            assert citation_preview.status_code == 200
            assert citation_preview.json()["doc_id"] == source_id
            assert citation_preview.json()["page"] == questions[0]["citation"]["page"]
            assert citation_preview.json()["passage"] == asyncio.run(
                _load_chunk_text(
                    postgres.get_connection_url(),
                    source_id,
                    questions[0]["citation"]["page"],
                )
            )

            blank_span = client.get(
                f"/api/sessions/{session_id}/citation",
                params={
                    "doc_id": source_id,
                    "page": questions[0]["citation"]["page"],
                    "span": "   ",
                },
            )
            assert blank_span.status_code == 422

            question_rows = asyncio.run(_load_questions(postgres.get_connection_url(), session_id))

            for question in question_rows:
                answer = client.post(
                    f"/api/sessions/{session_id}/answers",
                    json={"question_id": question.id, "chosen_index": question.correct_index},
                )
                assert answer.status_code == 200

            session_response = client.get(f"/api/sessions/{session_id}")
            assert session_response.status_code == 200
            assert session_response.json()["status"] == "completed"
            assert session_response.json()["passed"] is True

            record_id = asyncio.run(_load_record_id(postgres.get_connection_url(), session_id))

            record_meta = client.get(f"/api/ce-records/{record_id}")
            assert record_meta.status_code == 200
            download = client.get(record_meta.json()["download_url"])
            assert download.status_code == 200
            assert download.headers["content-type"].startswith("application/pdf")


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
                password_hash="hash",
                role="admin",
            )
        )
    await engine.dispose()


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
        record = result.scalar_one()
    await engine.dispose()
    return record.id


async def _load_chunk_text(database_url: str, source_id: str, page: int) -> str:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        result = await session.execute(
            select(ChunkModel)
            .where(ChunkModel.source_id == source_id)
            .where(ChunkModel.page == page)
        )
        chunk = result.scalar_one()
    await engine.dispose()
    return chunk.text
