from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

from prometheus_client import generate_latest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.adapters.storage.local_storage import LocalSourceStorage
from app.config import Settings
from app.repositories import models as _models  # noqa: F401
from app.repositories.db import Base
from app.repositories.models.courses import CourseModel
from app.repositories.models.openai_cost_ledger import OpenAICostLedgerModel
from app.repositories.models.orgs import OrgModel
from app.repositories.models.sources import SourceModel
from app.repositories.models.users import UserModel
from app.services.auth.tokens import hash_password
from app.services.generation.cost_cap import OpenAICostCap
from app.services.generation.service import GenerationService


class RecordingLLM:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload
        self.calls: list[tuple[str, int]] = []

    def generate(self, prompt: str, max_tokens: int) -> str:
        self.calls.append((prompt, max_tokens))
        return json.dumps(self.payload, sort_keys=True)


def test_openai_cost_cap_warns_at_eighty_percent(tmp_path: Path) -> None:
    with PostgresContainer(
        image="postgres:15-alpine",
        username="app",
        password="app",
        dbname="pharm",
        driver="asyncpg",
    ) as postgres:
        database_url = postgres.get_connection_url()
        asyncio.run(_prepare_database(database_url, usd=40.0))
        before_warn = _metric_value("openai_cap_warn_80_total")

        async def _exercise() -> bool:
            engine = create_async_engine(database_url, pool_pre_ping=True)
            async with async_sessionmaker(engine, expire_on_commit=False)() as session:
                cost_cap = OpenAICostCap(session=session, monthly_cap_usd=50.0)
                allowed = await cost_cap.allow()
            await engine.dispose()
            return allowed

        assert asyncio.run(_exercise()) is True
        after_warn = _metric_value("openai_cap_warn_80_total")
        assert after_warn == before_warn + 1
        assert _monthly_spend_value() == 40.0


def test_generation_service_falls_back_when_openai_cap_reached(tmp_path: Path) -> None:
    with PostgresContainer(
        image="postgres:15-alpine",
        username="app",
        password="app",
        dbname="pharm",
        driver="asyncpg",
    ) as postgres:
        database_url = postgres.get_connection_url()
        asyncio.run(_prepare_database(database_url, usd=50.0))
        storage = LocalSourceStorage(tmp_path / "uploads")
        asyncio.run(
            storage.save_source(
                "course-1",
                "source-1",
                "cardiology.pdf",
                b"Beta blockers reduce heart rate and blood pressure.",
            )
        )
        settings = Settings(
            app_env="test",
            database_url=database_url,
            storage_root=str(tmp_path / "uploads"),
            faiss_index_dir=str(tmp_path / "faiss"),
            llm_provider="openai",
            openai_api_key="sk-test",
            openai_monthly_usd_cap=50.0,
        )
        payload = {
            "stem": "What is the best answer based on the source?",
            "choices": ["A", "B", "C", "D"],
            "correct_choice_index": 0,
            "rationale": "The source says the answer is supported.",
        }
        openai_llm = RecordingLLM(payload)
        local_llm = RecordingLLM(payload)
        before_reached = _metric_value("openai_cap_reached_total")

        async def _exercise() -> None:
            engine = create_async_engine(database_url, pool_pre_ping=True)
            async with async_sessionmaker(engine, expire_on_commit=False)() as session:
                service = GenerationService(
                    session=session,
                    storage=storage,
                    settings=settings,
                    local_llm=local_llm,
                    openai_llm=openai_llm,
                )
                started = await service.start_session("user-1", "org-1", "course-1")
                assert started.questions
            await engine.dispose()

        asyncio.run(_exercise())

        after_reached = _metric_value("openai_cap_reached_total")
        assert after_reached == before_reached + 1
        assert openai_llm.calls == []
        assert local_llm.calls


async def _prepare_database(database_url: str, *, usd: float) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(OrgModel.__table__.insert().values(id="org-1", name="Metro CE"))
        await conn.execute(
            CourseModel.__table__.insert().values(
                id="course-1",
                org_id="org-1",
                title="Cardiology CE",
                n_questions=1,
                pass_pct=70,
                status="ready",
            )
        )
        await conn.execute(
            SourceModel.__table__.insert().values(
                id="source-1",
                course_id="course-1",
                filename="cardiology.pdf",
                bytes=128,
                sha256="a" * 64,
                status="ready",
                last_error=None,
            )
        )
        await conn.execute(
            UserModel.__table__.insert().values(
                id="user-1",
                org_id="org-1",
                email="pharmacist@example.com",
                password_hash=hash_password("secretsecret12"),
                role="member",
            )
        )
        await conn.execute(
            OpenAICostLedgerModel.__table__.insert().values(
                id="cost-1",
                year_month=datetime.now(UTC).strftime("%Y-%m"),
                usd=usd,
                request_count=1,
            )
        )
    await engine.dispose()


def _metric_value(name: str) -> float:
    lines = generate_latest().decode("utf-8").splitlines()
    for line in lines:
        if line.startswith(f"{name} "):
            return float(line.split(" ", 1)[1])
    raise AssertionError(f"metric {name} not found")


def _monthly_spend_value() -> float:
    lines = generate_latest().decode("utf-8").splitlines()
    for line in lines:
        if line.startswith("openai_cost_usd_monthly{"):
            return float(line.rsplit(" ", 1)[1])
    raise AssertionError("monthly spend metric not found")
