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
