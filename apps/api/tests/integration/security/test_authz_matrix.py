from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from app.api.deps import get_ingest_service
from app.config import Settings
from app.main import create_app
from app.repositories.db import Base
from app.services.auth.tokens import hash_password


class FakeIngestService:
    def __init__(self) -> None:
        self.enqueued: list[str] = []

    async def enqueue(self, source_id: str) -> None:
        self.enqueued.append(source_id)


def test_authz_matrix_admin_member_and_cross_tenant(tmp_path: Path) -> None:
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
                app_env="test",
                database_url=database_url,
                storage_root=str(tmp_path / "uploads"),
                faiss_index_dir=str(tmp_path / "faiss"),
            )
        )
        fake_ingest = FakeIngestService()
        app.dependency_overrides[get_ingest_service] = lambda: fake_ingest

        with TestClient(app, base_url="https://testserver") as client:
            anonymous = client.get("/api/courses")
            assert anonymous.status_code == 401

            admin_token = _login(client, "admin@example.com", "secretsecret12")
            member_token = _login(client, "member@example.com", "membersecret12")
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            member_headers = {"Authorization": f"Bearer {member_token}"}

            member_courses = client.get("/api/courses", headers=member_headers)
            assert member_courses.status_code == 200

            member_create = client.post(
                "/api/courses",
                headers=member_headers,
                json={"title": "Member CE", "n_questions": 6, "pass_pct": 70},
            )
            assert member_create.status_code == 403

            admin_create = client.post(
                "/api/courses",
                headers=admin_headers,
                json={"title": "Cardiology CE", "n_questions": 6, "pass_pct": 70},
            )
            assert admin_create.status_code == 201
            course_id = admin_create.json()["id"]

            member_upload = client.post(
                f"/api/courses/{course_id}/sources",
                headers=member_headers,
                files={
                    "file": (
                        "source.pdf",
                        b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
                        "application/pdf",
                    )
                },
            )
            assert member_upload.status_code == 403

            admin_upload = client.post(
                f"/api/courses/{course_id}/sources",
                headers=admin_headers,
                files={
                    "file": (
                        "source.pdf",
                        b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
                        "application/pdf",
                    )
                },
            )
            assert admin_upload.status_code == 202

            member_session = client.post(f"/api/sessions/{course_id}/start", headers=member_headers)
            assert member_session.status_code == 201

            foreign_course = client.get("/api/courses/foreign-course", headers=admin_headers)
            assert foreign_course.status_code == 404


async def _prepare_database(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                """
                INSERT INTO orgs (id, name)
                VALUES ('org-1', 'Metro CE'),
                       ('org-2', 'North CE')
                """
            )
        )
        await conn.execute(
            text(
                """
                INSERT INTO users (id, org_id, email, password_hash, role)
                VALUES
                  ('admin-1', 'org-1', 'admin@example.com', :admin_hash, 'admin'),
                  ('member-1', 'org-1', 'member@example.com', :member_hash, 'member')
                """
            ),
            {
                "admin_hash": hash_password("secretsecret12"),
                "member_hash": hash_password("membersecret12"),
            },
        )
        await conn.execute(
            text(
                """
                INSERT INTO courses (id, org_id, title, n_questions, pass_pct, status)
                VALUES ('foreign-course', 'org-2', 'Foreign CE', 6, 70, 'draft')
                """
            )
        )
    await engine.dispose()


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]
