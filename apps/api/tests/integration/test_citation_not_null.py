from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.repositories import models as _models  # noqa: F401
from app.repositories.db import Base


async def _assert_citation_not_null(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        with pytest.raises(IntegrityError):
            await session.execute(
                text(
                    "INSERT INTO questions "
                    "(id, session_id, text, options, correct_index, rationale, source_doc_id, "
                    "source_page, source_span, citation_overlap, created_at) "
                    "VALUES (:id, :session_id, :text, "
                    '\'{"choices": ["A", "B", "C", "D"]}\'::jsonb, '
                    ":correct_index, :rationale, :source_doc_id, :source_page, "
                    ":source_span, :citation_overlap, NOW())"
                ),
                {
                    "id": "question-null",
                    "session_id": "session-1",
                    "text": "What is the key point?",
                    "correct_index": 1,
                    "rationale": "Grounded rationale.",
                    "source_doc_id": None,
                    "source_page": 1,
                    "source_span": "p1:s1",
                    "citation_overlap": 0.5,
                },
            )

    await engine.dispose()


def test_question_requires_source_citation_fields() -> None:
    with PostgresContainer(
        image="postgres:15-alpine",
        username="app",
        password="app",
        dbname="pharm",
        driver="asyncpg",
    ) as postgres:
        asyncio.run(_assert_citation_not_null(postgres.get_connection_url()))
