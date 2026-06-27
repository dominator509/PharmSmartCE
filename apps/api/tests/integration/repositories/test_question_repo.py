from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.repositories import models as _models  # noqa: F401
from app.repositories.db import Base
from app.repositories.models.courses import CourseModel
from app.repositories.models.orgs import OrgModel
from app.repositories.models.questions import QuestionModel
from app.repositories.models.refresh_tokens import RefreshTokenModel
from app.repositories.models.sessions import SessionModel
from app.repositories.models.sources import SourceModel
from app.repositories.models.users import UserModel
from app.repositories.question_repo import QuestionRepo
from app.repositories.refresh_token_repo import RefreshTokenRepo


async def _exercise(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        session.add(OrgModel(id="org-1", name="Metro CE"))
        await session.flush()
        session.add(
            CourseModel(
                id="course-1",
                org_id="org-1",
                title="Cardiology CE",
                n_questions=6,
                pass_pct=70,
                status="ready",
            )
        )
        session.add(
            UserModel(
                id="user-1",
                org_id="org-1",
                email="pharmacist@example.com",
                password_hash="hash",
                role="member",
            )
        )
        await session.flush()
        session.add(
            SourceModel(
                id="source-1",
                course_id="course-1",
                filename="cardiology.pdf",
                bytes_=128,
                sha256="b" * 64,
                status="ready",
                last_error=None,
            )
        )
        session.add(
            SessionModel(
                id="session-1",
                course_id="course-1",
                user_id="user-1",
                seed="seed-1",
                started_at=datetime.now(UTC),
                completed_at=None,
                score_pct=None,
                passed=None,
            )
        )
        await session.flush()

        question_repo = QuestionRepo(session)
        question = await question_repo.add(
            QuestionModel(
                id="question-1",
                session_id="session-1",
                text="What is the key point?",
                options={"choices": ["A", "B", "C", "D"]},
                correct_index=1,
                rationale="The source text explains the key point clearly.",
                source_doc_id="source-1",
                source_page=3,
                source_span="p3:s7",
                citation_overlap=0.5,
            )
        )
        assert await question_repo.get(question.id) is question
        assert await question_repo.list_by_session("session-1") == [question]

        refresh_repo = RefreshTokenRepo(session)
        first = await refresh_repo.add(
            RefreshTokenModel(
                jti="token-1",
                user_id="user-1",
                token_sha256="c" * 64,
                expires_at=datetime.now(UTC) + timedelta(days=30),
                revoked_at=None,
                replaced_by_jti=None,
            )
        )
        second = await refresh_repo.add(
            RefreshTokenModel(
                jti="token-2",
                user_id="user-1",
                token_sha256="d" * 64,
                expires_at=datetime.now(UTC) + timedelta(days=60),
                revoked_at=None,
                replaced_by_jti=None,
            )
        )
        revoked = await refresh_repo.revoke(first.jti, replaced_by_jti=second.jti)
        assert revoked is first
        assert revoked.revoked_at is not None
        assert revoked.replaced_by_jti == second.jti
        assert await refresh_repo.get_by_user("user-1") == [first, second]

    await engine.dispose()


def test_question_repo_and_refresh_token_chain() -> None:
    with PostgresContainer(
        image="postgres:15-alpine",
        username="app",
        password="app",
        dbname="pharm",
        driver="asyncpg",
    ) as postgres:
        asyncio.run(_exercise(postgres.get_connection_url()))
