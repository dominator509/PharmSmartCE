from __future__ import annotations

import asyncio

import pytest

from app.api.errors import ValidationError
from app.services.course.service import CourseService


def test_create_course_rejects_blank_title() -> None:
    service = CourseService(session=object(), storage=object(), ingest_service=object())

    async def _run() -> None:
        await service.create_course(org_id="org-1", title="   ")

    with pytest.raises(ValidationError):
        asyncio.run(_run())


def test_upload_source_rejects_blank_filename() -> None:
    service = CourseService(session=object(), storage=object(), ingest_service=object())

    async def _run() -> None:
        await service.upload_source(
            course_id="course-1",
            org_id="org-1",
            filename="   ",
            content=b"content",
            max_bytes=100,
        )

    with pytest.raises(ValidationError):
        asyncio.run(_run())
