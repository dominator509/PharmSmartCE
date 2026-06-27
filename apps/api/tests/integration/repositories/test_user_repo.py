from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.repositories import models as _models  # noqa: F401
from app.repositories.course_repo import CourseRepo
from app.repositories.db import Base
from app.repositories.models.answers import AnswerModel
from app.repositories.models.ce_records import CERecordModel
from app.repositories.models.chunks import ChunkModel
from app.repositories.models.courses import CourseModel
from app.repositories.models.openai_cost_ledger import OpenAICostLedgerModel
from app.repositories.models.orgs import OrgModel
from app.repositories.models.questions import QuestionModel
from app.repositories.models.sessions import SessionModel
from app.repositories.models.sources import SourceModel
from app.repositories.models.users import UserModel
from app.repositories.session_repo import SessionRepo
from app.repositories.source_repo import SourceRepo
from app.repositories.user_repo import UserRepo


async def _round_trip(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        org = OrgModel(id="org-1", name="Metro CE")
        session.add(org)
        await session.flush()
        assert org.id == "org-1"

        user_repo = UserRepo(session)
        user = await user_repo.add(
            UserModel(
                id="user-1",
                org_id=org.id,
                email="pharmacist@example.com",
                password_hash="hash",
                role="member",
            )
        )
        assert await user_repo.get(user.id) is user
        assert await user_repo.get_by_email(user.email) is user

        course_repo = CourseRepo(session)
        course = await course_repo.add(
            CourseModel(
                id="course-1",
                org_id=org.id,
                title="Cardiology CE",
                n_questions=6,
                pass_pct=70,
                status="ready",
            )
        )
        assert await course_repo.get(course.id) is course

        source_repo = SourceRepo(session)
        source = await source_repo.add(
            SourceModel(
                id="source-1",
                course_id=course.id,
                filename="cardiology.pdf",
                bytes_=128,
                sha256="a" * 64,
                status="ready",
                last_error=None,
            )
        )
        assert await source_repo.get(source.id) is source

        chunk = ChunkModel(
            id="chunk-1",
            source_id=source.id,
            page=1,
            span_start=0,
            span_end=42,
            text="Alpha beta gamma.",
            embedding_index=0,
        )
        session.add(chunk)
        await session.flush()
        assert chunk.id == "chunk-1"

        session_repo = SessionRepo(session)
        session_row = await session_repo.add(
            SessionModel(
                id="session-1",
                course_id=course.id,
                user_id=user.id,
                seed="seed-1",
                started_at=datetime.now(UTC),
                completed_at=None,
                score_pct=91.5,
                passed=True,
            )
        )
        assert await session_repo.get(session_row.id) is session_row
        assert await session_repo.list_by_user_course(user.id, course.id) == [session_row]

        question = QuestionModel(
            id="question-1",
            session_id=session_row.id,
            text="What is the key point?",
            options={"choices": ["A", "B", "C", "D"]},
            correct_index=1,
            rationale="The source text explains the key point clearly.",
            source_doc_id=source.id,
            source_page=1,
            source_span="p1:s1",
            citation_overlap=0.75,
        )
        session.add(question)
        await session.flush()
        assert question.id == "question-1"

        answer = AnswerModel(
            id="answer-1",
            question_id=question.id,
            chosen_index=1,
            correct=True,
            answered_at=datetime.now(UTC),
        )
        session.add(answer)
        await session.flush()
        assert answer.id == "answer-1"

        ce_record = CERecordModel(
            id="ce-1",
            session_id=session_row.id,
            pdf_storage_key="records/session-1.pdf",
            issued_at=datetime.now(UTC),
        )
        session.add(ce_record)
        await session.flush()
        assert ce_record.id == "ce-1"

        cost_row = OpenAICostLedgerModel(
            id="cost-1",
            year_month="2026-06",
            usd=12.50,
            request_count=3,
        )
        session.add(cost_row)
        await session.flush()
        assert cost_row.id == "cost-1"

        assert await course_repo.list_by_org(org.id) == [course]
        assert await source_repo.list_by_course(course.id) == [source]
        assert await session_repo.list_by_user_course(user.id, course.id) == [session_row]

    await engine.dispose()


def test_user_repo_round_trips_core_tables() -> None:
    with PostgresContainer(
        image="postgres:15-alpine",
        username="app",
        password="app",
        dbname="pharm",
        driver="asyncpg",
    ) as postgres:
        asyncio.run(_round_trip(postgres.get_connection_url()))
