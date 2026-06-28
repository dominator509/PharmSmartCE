from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    Principal,
    current_admin,
    current_user,
    get_ingest_service,
    get_session,
    get_settings,
    get_storage,
    require_api_rate_limit,
)
from app.config import Settings
from app.services.course.service import CourseService
from app.services.ingest.service import IngestService
from app.services.ports.storage import StoragePort

router = APIRouter(prefix="/api/courses", dependencies=[Depends(require_api_rate_limit)])


class CourseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    title: str
    n_questions: int
    pass_pct: int
    status: str
    created_at: datetime


class CourseListDTO(BaseModel):
    items: list[CourseDTO]


class CourseCreateDTO(BaseModel):
    title: str = Field(strict=True, min_length=1, max_length=255, pattern=r".*\S.*")
    n_questions: int = Field(default=6, strict=True)
    pass_pct: int = Field(default=70, strict=True, ge=50, le=100)


class SourceDTO(BaseModel):
    id: str
    course_id: str
    filename: str = Field(max_length=255)
    bytes: int
    sha256: str
    status: str
    created_at: datetime


class CourseDetailDTO(CourseDTO):
    sources: list[SourceDTO] = Field(default_factory=list)


def _course_service(
    session: AsyncSession,
    storage: StoragePort,
    ingest_service: IngestService,
) -> CourseService:
    return CourseService(session=session, storage=storage, ingest_service=ingest_service)


@router.get("", response_model=CourseListDTO)
async def list_courses(
    user: Annotated[Principal, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    storage: Annotated[StoragePort, Depends(get_storage)],
    ingest_service: Annotated[IngestService, Depends(get_ingest_service)],
) -> CourseListDTO:
    service = _course_service(session, storage, ingest_service)
    courses = await service.list_courses(user.org_id)
    return CourseListDTO(items=[CourseDTO.model_validate(course) for course in courses])


@router.get("/{course_id}", response_model=CourseDetailDTO)
async def get_course(
    course_id: str,
    user: Annotated[Principal, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    storage: Annotated[StoragePort, Depends(get_storage)],
    ingest_service: Annotated[IngestService, Depends(get_ingest_service)],
) -> CourseDetailDTO:
    service = _course_service(session, storage, ingest_service)
    course = await service.get_course(course_id)
    if course.org_id != user.org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    sources = await service.list_sources(course_id)
    return CourseDetailDTO(
        id=course.id,
        org_id=course.org_id,
        title=course.title,
        n_questions=course.n_questions,
        pass_pct=course.pass_pct,
        status=course.status,
        created_at=course.created_at,
        sources=[
            SourceDTO(
                id=source.id,
                course_id=source.course_id,
                filename=source.filename,
                bytes=source.bytes_,
                sha256=source.sha256,
                status=source.status,
                created_at=source.created_at,
            )
            for source in sources
        ],
    )


@router.post("", response_model=CourseDTO, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreateDTO,
    admin: Annotated[Principal, Depends(current_admin)],
    session: Annotated[AsyncSession, Depends(get_session)],
    storage: Annotated[StoragePort, Depends(get_storage)],
    ingest_service: Annotated[IngestService, Depends(get_ingest_service)],
) -> CourseDTO:
    service = _course_service(session, storage, ingest_service)
    course = await service.create_course(
        org_id=admin.org_id,
        title=payload.title,
        n_questions=payload.n_questions,
        pass_pct=payload.pass_pct,
    )
    return CourseDTO.model_validate(course)


@router.post("/{course_id}/sources", response_model=SourceDTO, status_code=status.HTTP_202_ACCEPTED)
async def upload_source(
    course_id: str,
    file: Annotated[UploadFile, File(...)],
    admin: Annotated[Principal, Depends(current_admin)],
    session: Annotated[AsyncSession, Depends(get_session)],
    storage: Annotated[StoragePort, Depends(get_storage)],
    ingest_service: Annotated[IngestService, Depends(get_ingest_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> SourceDTO:
    if file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Missing file.",
        )
    content = await file.read()

    service = _course_service(session, storage, ingest_service)
    source = await service.upload_source(
        course_id,
        admin.org_id,
        file.filename,
        content,
        settings.upload_max_bytes,
        file.content_type,
    )
    return SourceDTO(
        id=source.id,
        course_id=source.course_id,
        filename=source.filename,
        bytes=source.bytes_,
        sha256=source.sha256,
        status=source.status,
        created_at=source.created_at,
    )
