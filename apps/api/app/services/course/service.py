from __future__ import annotations

import os
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

import magic
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors import NotFoundError, ValidationError
from app.repositories.course_repo import CourseRepo
from app.repositories.models.courses import CourseModel
from app.repositories.models.sources import SourceModel
from app.repositories.source_repo import SourceRepo
from app.services.ingest.service import IngestService
from app.services.ports.storage import StoragePort


@dataclass(slots=True)
class CourseService:
    session: AsyncSession
    storage: StoragePort
    ingest_service: IngestService

    @property
    def courses(self) -> CourseRepo:
        return CourseRepo(self.session)

    @property
    def sources(self) -> SourceRepo:
        return SourceRepo(self.session)

    async def list_courses(self, org_id: str) -> list[CourseModel]:
        return await self.courses.list_by_org(org_id)

    async def get_course(self, course_id: str) -> CourseModel:
        course = await self.courses.get(course_id)
        if course is None:
            raise NotFoundError(f"Course {course_id} not found.")
        return course

    async def list_sources(self, course_id: str) -> list[SourceModel]:
        return await self.sources.list_by_course(course_id)

    async def create_course(
        self,
        org_id: str,
        title: str,
        n_questions: int = 6,
        pass_pct: int = 70,
    ) -> CourseModel:
        if not title.strip():
            raise ValidationError("Course title must not be empty.")
        if len(title) > 255:
            raise ValidationError("Course title must not exceed 255 characters.")
        if n_questions <= 0:
            raise ValidationError("Course must have at least one question.")
        course = CourseModel(
            id=uuid4().hex,
            org_id=org_id,
            title=title,
            n_questions=n_questions,
            pass_pct=pass_pct,
            status="draft",
        )
        course = await self.courses.add(course)
        await self.session.commit()
        return course

    async def upload_source(
        self,
        course_id: str,
        org_id: str,
        filename: str,
        content: bytes,
        max_bytes: int,
        content_type: str | None = None,
    ) -> SourceModel:
        if not filename.strip():
            raise ValidationError("Source filename must not be empty.")
        if len(filename) > 255:
            raise ValidationError("Source filename must not exceed 255 characters.")
        if filename != Path(filename).name or filename in {".", ".."}:
            raise ValidationError("Source filename must not include path separators.")
        if filename.rstrip(" .") != filename:
            raise ValidationError("Source filename must not end with dots or spaces.")
        if os.name == "nt" and _is_windows_reserved_filename(filename):
            raise ValidationError("Source filename must not use reserved Windows names.")
        if not content:
            raise ValidationError("Source file must not be empty.")
        if len(content) > max_bytes:
            raise ValidationError("Source file exceeds the maximum size.")

        mime = _normalize_mime_type(content_type or magic.from_buffer(content[:2048], mime=True))
        is_pdf = mime == "application/pdf" or filename.lower().endswith(".pdf")
        is_docx = (
            mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            or filename.lower().endswith(".docx")
        )
        if not is_pdf and not is_docx:
            raise ValidationError("Source file must be a PDF or DOCX.")

        course = await self.get_course(course_id)
        if course.org_id != org_id:
            raise NotFoundError(f"Course {course_id} not found.")
        source = SourceModel(
            id=uuid4().hex,
            course_id=course_id,
            filename=filename,
            bytes_=len(content),
            sha256=sha256(content).hexdigest(),
            status="uploaded",
            last_error=None,
        )
        await self.sources.add(source)
        await self.session.commit()
        await self.storage.save_source(course_id, source.id, filename, content)
        await self.ingest_service.enqueue(source.id)
        return source


def _normalize_mime_type(value: str | None) -> str:
    if not value:
        return ""
    return value.split(";", 1)[0].strip().lower()


def _is_windows_reserved_filename(filename: str) -> bool:
    stem = filename.split(".", 1)[0].upper()
    return stem in {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
