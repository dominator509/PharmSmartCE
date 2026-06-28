from __future__ import annotations

import asyncio

from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.health import _check_database


def test_check_database_returns_false_for_sqlalchemy_errors(monkeypatch) -> None:
    class _FakeConnection:
        async def execute(self, *_args, **_kwargs) -> None:
            raise SQLAlchemyError("boom")

    class _FakeEngine:
        def connect(self) -> _FakeConnectionContext:
            return _FakeConnectionContext()

        async def dispose(self) -> None:
            return None

    class _FakeConnectionContext:
        async def __aenter__(self) -> _FakeConnection:
            return _FakeConnection()

        async def __aexit__(self, *_exc_info) -> None:
            return None

    monkeypatch.setattr("app.api.routes.health.create_async_engine", lambda *_args, **_kwargs: _FakeEngine())

    assert asyncio.run(_check_database("postgresql+asyncpg://app:app@localhost:5432/pharm")) is False
