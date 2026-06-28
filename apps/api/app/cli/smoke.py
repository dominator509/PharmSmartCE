from __future__ import annotations

import argparse
import asyncio
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.api.deps import Principal, current_admin, current_user, get_ingest_service
from app.config import Settings
from app.main import create_app
from app.repositories.db import Base
from app.repositories.models.ce_records import CERecordModel
from app.repositories.models.orgs import OrgModel
from app.repositories.models.questions import QuestionModel
from app.repositories.models.users import UserModel


class FakeIngestService:
    def __init__(self) -> None:
        self.enqueued: list[str] = []

    async def enqueue(self, source_id: str) -> None:
        self.enqueued.append(source_id)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="smoke")
    parser.add_argument("base_url", nargs="?", default="http://localhost:8000")
    args = parser.parse_args(argv)

    if _is_local_base_url(args.base_url):
        _run_local_smoke()
    else:
        _run_remote_smoke(args.base_url)

    print("smoke test: ok")
    return 0


def _is_local_base_url(base_url: str) -> bool:
    parsed = urlparse(base_url)
    return parsed.hostname in {None, "localhost", "127.0.0.1", "::1"}


def _run_remote_smoke(base_url: str) -> None:
    email = f"pharmacist-{uuid4().hex[:12]}@example.com"
    with httpx.Client(base_url=base_url, timeout=10.0, follow_redirects=True) as client:
        _assert_ok(client.get("/healthz"), "/healthz")
        _assert_ok(client.get("/readyz"), "/readyz")

        registered = client.post(
            "/auth/register",
            json={"email": email, "password": "secretsecret12"},
        )
        _assert_status(registered, 201, "/auth/register")

        logged_in = client.post(
            "/auth/login",
            json={"email": email, "password": "secretsecret12"},
        )
        _assert_status(logged_in, 200, "/auth/login")
        refresh_cookie = client.cookies.get("refresh")
        if not refresh_cookie:
            raise RuntimeError("Smoke login did not set a refresh cookie.")

        refreshed = client.post("/auth/refresh")
        _assert_status(refreshed, 200, "/auth/refresh")
        refresh_body = refreshed.json()
        auth_headers = {"Authorization": f"Bearer {refresh_body['access_token']}"}

        created = client.post(
            "/api/courses",
            headers=auth_headers,
            json={"title": "Cardiology CE", "n_questions": 6, "pass_pct": 70},
        )
        _assert_status(created, 201, "/api/courses")
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
        _assert_status(uploaded, 202, f"/api/courses/{course_id}/sources")
        if uploaded.json()["status"] != "uploaded":
            raise RuntimeError("Smoke upload did not reach uploaded state.")

        started = client.post(f"/api/sessions/{course_id}/start", headers=auth_headers)
        _assert_status(started, 201, f"/api/sessions/{course_id}/start")
        session_id = started.json()["id"]

        session_response = client.get(f"/api/sessions/{session_id}", headers=auth_headers)
        _assert_status(session_response, 200, f"/api/sessions/{session_id}")
        session_body = session_response.json()
        if len(session_body["questions"]) < 6:
            raise RuntimeError("Smoke session did not generate enough questions.")

        for question in session_body["questions"]:
            citation_response = client.get(question["citation"]["url"], headers=auth_headers)
            _assert_status(citation_response, 200, question["citation"]["url"])
            chosen_index = _supported_choice_index(question["options"])
            answer = client.post(
                f"/api/sessions/{session_id}/answers",
                headers=auth_headers,
                json={"question_id": question["id"], "chosen_index": chosen_index},
            )
            _assert_status(answer, 200, f"/api/sessions/{session_id}/answers")

        completed = client.get(f"/api/sessions/{session_id}", headers=auth_headers)
        _assert_status(completed, 200, f"/api/sessions/{session_id}")
        completed_body = completed.json()
        if completed_body["status"] != "completed":
            raise RuntimeError("Smoke session did not complete.")

        record_id = completed_body.get("record_id")
        if not record_id:
            raise RuntimeError("Smoke session did not expose a CE record id.")
        record_meta = client.get(f"/api/ce-records/{record_id}", headers=auth_headers)
        _assert_status(record_meta, 200, f"/api/ce-records/{record_id}")
        pdf = client.get(record_meta.json()["download_url"], headers=auth_headers)
        _assert_status(pdf, 200, record_meta.json()["download_url"])
        if not pdf.headers.get("content-type", "").startswith("application/pdf"):
            raise RuntimeError("Smoke CE record did not return PDF content.")

        logout = client.post("/auth/logout")
        _assert_status(logout, 204, "/auth/logout")
        stale_refresh = client.post("/auth/refresh", cookies={"refresh": refresh_cookie})
        _assert_status(stale_refresh, 401, "/auth/refresh after logout")


def _run_local_smoke() -> None:
    with (
        tempfile.TemporaryDirectory() as tempdir,
        PostgresContainer(
            image="postgres:15-alpine",
            username="app",
            password="app",
            dbname="pharm",
            driver="asyncpg",
        ) as postgres,
    ):
        asyncio.run(_prepare_database(postgres.get_connection_url()))
        app = create_app(
            Settings(
                database_url=postgres.get_connection_url(),
                storage_root=str(Path(tempdir) / "uploads"),
                faiss_index_dir=str(Path(tempdir) / "faiss"),
            )
        )
        fake_ingest = FakeIngestService()
        principal = Principal(id="user-1", org_id="org-1", role="admin")
        app.dependency_overrides[current_user] = lambda: principal
        app.dependency_overrides[current_admin] = lambda: principal
        app.dependency_overrides[get_ingest_service] = lambda: fake_ingest

        with TestClient(app) as client:
            _assert_ok(client.get("/healthz"), "/healthz")
            _assert_ok(client.get("/readyz"), "/readyz")

            created = client.post(
                "/api/courses",
                json={"title": "Cardiology CE", "n_questions": 6, "pass_pct": 70},
            )
            _assert_status(created, 201, "/api/courses")
            course_id = created.json()["id"]

            uploaded = client.post(
                f"/api/courses/{course_id}/sources",
                files={
                    "file": (
                        "source.pdf",
                        b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
                        "application/pdf",
                    )
                },
            )
            _assert_status(uploaded, 202, "/api/courses/{course_id}/sources")
            body = uploaded.json()
            if body["status"] != "uploaded":
                raise RuntimeError("Smoke upload did not reach uploaded state.")
            if fake_ingest.enqueued != [body["id"]]:
                raise RuntimeError("Smoke ingest did not enqueue exactly one source.")
            saved = Path(tempdir) / "uploads" / course_id / body["id"] / "source.pdf"
            if not saved.exists():
                raise RuntimeError("Smoke upload file was not persisted.")

            started = client.post(f"/api/sessions/{course_id}/start")
            _assert_status(started, 201, f"/api/sessions/{course_id}/start")
            session_id = started.json()["id"]

            question_rows = asyncio.run(_load_questions(postgres.get_connection_url(), session_id))
            if len(question_rows) < 6:
                raise RuntimeError("Smoke session did not generate enough questions.")

            for question in question_rows:
                answer = client.post(
                    f"/api/sessions/{session_id}/answers",
                    json={"question_id": question.id, "chosen_index": question.correct_index},
                )
                _assert_status(answer, 200, f"/api/sessions/{session_id}/answers")

            session_response = client.get(f"/api/sessions/{session_id}")
            _assert_status(session_response, 200, f"/api/sessions/{session_id}")
            if session_response.json()["status"] != "completed":
                raise RuntimeError("Smoke session did not complete.")

            record_id = asyncio.run(_load_record_id(postgres.get_connection_url(), session_id))
            record_meta = client.get(f"/api/ce-records/{record_id}")
            _assert_status(record_meta, 200, f"/api/ce-records/{record_id}")
            pdf = client.get(record_meta.json()["download_url"])
            _assert_status(pdf, 200, record_meta.json()["download_url"])
            if not pdf.headers.get("content-type", "").startswith("application/pdf"):
                raise RuntimeError("Smoke CE record did not return PDF content.")


async def _prepare_database(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with session_factory() as session:
        session.add_all(
            [
                OrgModel(id="org-1", name="Metro CE"),
                UserModel(
                    id="user-1",
                    org_id="org-1",
                    email="pharmacist@example.com",
                    password_hash="hash",
                    role="admin",
                ),
            ]
        )
        await session.commit()
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
        record_id = result.scalar_one().id
    await engine.dispose()
    return record_id


def _assert_ok(response: httpx.Response, path: str) -> None:
    _assert_status(response, 200, path)


def _assert_status(response: httpx.Response, expected: int, path: str) -> None:
    if response.status_code != expected:
        raise RuntimeError(
            f"{path} returned {response.status_code} instead of {expected}: {response.text}"
        )


def _supported_choice_index(options: list[str]) -> int:
    for index, option in enumerate(options):
        if option.startswith("Supported by the source"):
            return index
    raise RuntimeError("Smoke question did not expose a supported choice.")


if __name__ == "__main__":
    raise SystemExit(main())
