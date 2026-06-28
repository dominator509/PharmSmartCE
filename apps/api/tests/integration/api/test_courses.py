from __future__ import annotations

import asyncio
import io
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine

from app.api.deps import Principal, current_admin, current_user, get_ingest_service
from app.config import Settings
from app.main import create_app
from app.repositories.db import Base
from app.repositories.models.orgs import OrgModel
from testcontainers.postgres import PostgresContainer


class FakeIngestService:
    def __init__(self) -> None:
        self.enqueued: list[str] = []

    async def enqueue(self, source_id: str) -> None:
        self.enqueued.append(source_id)


def test_course_routes_and_upload(tmp_path: Path) -> None:
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
        fake_ingest = FakeIngestService()
        principal = Principal(id="user-1", org_id="org-1", role="admin")
        app.dependency_overrides[current_user] = lambda: principal
        app.dependency_overrides[current_admin] = lambda: principal
        app.dependency_overrides[get_ingest_service] = lambda: fake_ingest

        with TestClient(app) as client:
            empty = client.get("/api/courses")
            assert empty.status_code == 200
            assert empty.json() == {"items": []}

            created = client.post(
                "/api/courses",
                json={"title": "Cardiology CE", "n_questions": 6, "pass_pct": 70},
            )
            assert created.status_code == 201
            course_id = created.json()["id"]

            overlong_title = client.post(
                "/api/courses",
                json={"title": "a" * 256, "n_questions": 6, "pass_pct": 70},
            )
            assert overlong_title.status_code == 422

            fetched = client.get(f"/api/courses/{course_id}")
            assert fetched.status_code == 200
            assert fetched.json()["title"] == "Cardiology CE"

            upload = client.post(
                f"/api/courses/{course_id}/sources",
                files={
                    "file": (
                        "source.pdf",
                        b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
                        "application/pdf; charset=binary",
                    )
                },
            )
            assert upload.status_code == 202
            body = upload.json()
            assert body["course_id"] == course_id
            assert body["filename"] == "source.pdf"
            assert body["status"] == "uploaded"
            assert fake_ingest.enqueued == [body["id"]]
            assert (tmp_path / "uploads" / course_id / body["id"] / "source.pdf").exists()

            blank_name_upload = client.post(
                f"/api/courses/{course_id}/sources",
                files={
                    "file": (
                        "",
                        b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
                        "application/pdf",
                    )
                },
            )
            assert blank_name_upload.status_code == 422

            empty_upload = client.post(
                f"/api/courses/{course_id}/sources",
                files={
                    "file": (
                        "source.pdf",
                        b"",
                        "application/pdf",
                    )
                },
            )
            assert empty_upload.status_code == 422

            path_like_upload = client.post(
                f"/api/courses/{course_id}/sources",
                files={
                    "file": (
                        "nested/evil.pdf",
                        b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
                        "application/pdf",
                    )
                },
            )
            assert path_like_upload.status_code == 422

            reserved_name_upload = client.post(
                f"/api/courses/{course_id}/sources",
                files={
                    "file": (
                        "CON.txt",
                        b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
                        "application/pdf",
                    )
                },
            )
            assert reserved_name_upload.status_code == 422

            trailing_space_upload = client.post(
                f"/api/courses/{course_id}/sources",
                files={
                    "file": (
                        "evil.pdf ",
                        b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
                        "application/pdf",
                    )
                },
            )
            assert trailing_space_upload.status_code == 422

            with_source_list = client.get(f"/api/courses/{course_id}")
            assert with_source_list.status_code == 200
            source_items = with_source_list.json()["sources"]
            assert len(source_items) == 1
            assert source_items[0]["filename"] == "source.pdf"
            assert source_items[0]["status"] == "uploaded"

            docx_upload = client.post(
                f"/api/courses/{course_id}/sources",
                files={
                    "file": (
                        "source.docx",
                        _build_docx_bytes("The kidneys filter blood and remove waste."),
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                },
            )
            assert docx_upload.status_code == 202
            docx_body = docx_upload.json()
            assert docx_body["filename"] == "source.docx"
            assert (tmp_path / "uploads" / course_id / docx_body["id"] / "source.docx").exists()


async def _prepare_database(database_url: str) -> None:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(OrgModel.__table__.insert().values(id="org-1", name="Metro CE"))
    await engine.dispose()


def _build_docx_bytes(text: str) -> bytes:
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr(
            "word/document.xml",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body><w:p><w:r><w:t>"
                f"{text}"
                "</w:t></w:r></w:p></w:body></w:document>"
            ),
        )
    return buffer.getvalue()
