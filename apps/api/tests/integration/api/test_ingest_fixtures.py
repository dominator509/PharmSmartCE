from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.api.deps import Principal, current_admin, current_user
from app.config import Settings
from app.main import create_app
from app.repositories.db import Base
from app.repositories.models.chunks import ChunkModel
from app.repositories.models.orgs import OrgModel
from app.repositories.models.sources import SourceModel


def test_three_reference_fixture_pdfs_ingest_successfully(tmp_path: Path) -> None:
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
                database_url=database_url,
                storage_root=str(tmp_path / "uploads"),
                faiss_index_dir=str(tmp_path / "faiss"),
            )
        )
        principal = Principal(id="user-1", org_id="org-1", role="admin")
        app.dependency_overrides[current_user] = lambda: principal
        app.dependency_overrides[current_admin] = lambda: principal

        with TestClient(app) as client:
            course = client.post(
                "/api/courses",
                json={"title": "Cardiology CE", "n_questions": 6, "pass_pct": 70},
            )
            assert course.status_code == 201
            course_id = course.json()["id"]

            fixture_dir = Path(__file__).resolve().parents[2] / "fixtures" / "sample_ce"
            for fixture_path in sorted(fixture_dir.glob("*.pdf")):
                upload = client.post(
                    f"/api/courses/{course_id}/sources",
                    files={
                        "file": (
                            fixture_path.name,
                            fixture_path.read_bytes(),
                            "application/pdf",
                        )
                    },
                )
                assert upload.status_code == 202

        asyncio.run(_assert_ingested(database_url, course_id))


async def _prepare_database(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(OrgModel.__table__.insert().values(id="org-1", name="Metro CE"))
    await engine.dispose()


async def _assert_ingested(database_url: str, course_id: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        sources = list(
            (
                await session.execute(
                    select(SourceModel)
                    .where(SourceModel.course_id == course_id)
                    .order_by(SourceModel.filename)
                )
            ).scalars()
        )
        assert len(sources) == 3
        assert all(source.status == "ready" for source in sources)

        chunk_counts = []
        for source in sources:
            result = await session.execute(
                select(ChunkModel).where(ChunkModel.source_id == source.id)
            )
            chunk_counts.append(len(list(result.scalars())))

        assert chunk_counts == [3, 3, 3]
    await engine.dispose()
