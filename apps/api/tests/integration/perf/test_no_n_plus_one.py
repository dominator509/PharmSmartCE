from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from app.api.deps import current_admin, current_user
from app.config import Settings
from app.main import create_app
from app.repositories.db import Base
from app.repositories.models.orgs import OrgModel
from app.repositories.models.users import UserModel


def test_session_read_route_stays_within_query_budget(tmp_path: Path) -> None:
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
        principal = current_principal()
        app.dependency_overrides[current_user] = lambda: principal
        app.dependency_overrides[current_admin] = lambda: principal

        with TestClient(app) as client:
            created = client.post(
                "/api/courses",
                json={"title": "Cardiology CE", "n_questions": 6, "pass_pct": 70},
            )
            course_id = created.json()["id"]
            client.post(
                f"/api/courses/{course_id}/sources",
                files={
                    "file": (
                        "source.pdf",
                        b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
                        "application/pdf",
                    )
                },
            )
            started = client.post(f"/api/sessions/{course_id}/start")
            session_id = started.json()["id"]

            query_count = _count_queries(
                client,
                lambda: client.get(f"/api/sessions/{session_id}"),
            )

            assert query_count <= 6


def _count_queries(client: TestClient, action: Callable[[], object]) -> int:
    engine = client.app.state.session_factory.kw["bind"]
    query_count = 0

    def before_cursor_execute(
        _: Connection,
        __: object,
        statement: object,
        parameters: object,
        context: object,
        executemany: object,
    ) -> None:
        nonlocal query_count
        text = str(statement).strip().lower()
        if text.startswith("select") or text.startswith("insert") or text.startswith("update"):
            query_count += 1

    event.listen(engine.sync_engine, "before_cursor_execute", before_cursor_execute)
    try:
        action()
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", before_cursor_execute)
    return query_count


def current_principal() -> object:
    return type(
        "Principal",
        (),
        {"id": "user-1", "org_id": "org-1", "role": "admin"},
    )()


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
