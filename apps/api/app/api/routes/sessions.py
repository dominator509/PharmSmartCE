from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Principal, current_user, require_api_rate_limit
from app.api.errors import NotFoundError
from app.config import Settings
from app.repositories.chunk_repo import ChunkRepo
from app.repositories.course_repo import CourseRepo
from app.repositories.models.answers import AnswerModel
from app.repositories.models.ce_records import CERecordModel
from app.repositories.models.questions import QuestionModel
from app.repositories.models.sessions import SessionModel
from app.repositories.question_repo import QuestionRepo
from app.repositories.session_repo import SessionRepo
from app.repositories.source_repo import SourceRepo
from app.services.generation.service import GenerationService
from app.services.ports.storage import StoragePort
from app.services.session.service import SessionService

router = APIRouter(prefix="/api/sessions", dependencies=[Depends(require_api_rate_limit)])
ce_records_router = APIRouter(
    prefix="/api/ce-records", dependencies=[Depends(require_api_rate_limit)]
)


class CitationDTO(BaseModel):
    doc_id: str
    page: int
    span: str
    url: str


class QuestionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    text: str
    options: list[str]
    citation: CitationDTO


class SessionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    course_id: str
    user_id: str
    status: str
    total_questions: int
    answered_questions: int
    score_pct: float | None
    passed: bool | None
    record_id: str | None = None
    questions: list[QuestionDTO]


class AnswerDTO(BaseModel):
    question_id: str
    chosen_index: int = Field(strict=True)


class SessionProgressDTO(BaseModel):
    answered: int
    total: int


class AnswerResultDTO(BaseModel):
    correct: bool
    correct_index: int
    rationale: str
    citation: CitationDTO
    session_progress: SessionProgressDTO
    score_pct: float | None = None
    passed: bool | None = None


class CERecordDTO(BaseModel):
    id: str
    session_id: str
    pdf_storage_key: str
    issued_at: datetime
    download_url: str


class CitationPreviewDTO(BaseModel):
    doc_id: str
    page: int
    span: str
    source_filename: str
    passage: str


def _generation_service(
    session: AsyncSession, storage: StoragePort, settings: Settings
) -> GenerationService:
    return GenerationService(session=session, storage=storage, settings=settings)


def _session_service(session: AsyncSession) -> SessionService:
    return SessionService(session=session)


@router.post("/{course_id}/start", response_model=SessionDTO, status_code=status.HTTP_201_CREATED)
async def start_session(
    course_id: str,
    user: Annotated[Principal, Depends(current_user)],
    request: Request,
) -> SessionDTO:
    session = request.app.state.session_factory()
    storage: StoragePort = request.app.state.storage
    service = _generation_service(session, storage, request.app.state.settings)
    async with session:
        started = await service.start_session(user.id, user.org_id, course_id)
        return _session_dto(started.session, started.questions, 0)


@router.get("/{session_id}/citation", response_model=CitationPreviewDTO)
async def read_citation_preview(
    session_id: str,
    doc_id: str,
    user: Annotated[Principal, Depends(current_user)],
    request: Request,
    page: int = Query(ge=1),
    span: str = Query(min_length=1),
) -> CitationPreviewDTO:
    session_factory = request.app.state.session_factory
    async with session_factory() as db_session:
        session_repo = SessionRepo(db_session)
        session_row = await session_repo.get(session_id)
        if session_row is None:
            raise NotFoundError(f"Session {session_id} not found.")

        course = await CourseRepo(db_session).get(session_row.course_id)
        if course is None or course.org_id != user.org_id:
            raise NotFoundError(f"Session {session_id} not found.")

        source = await SourceRepo(db_session).get(doc_id)
        if source is None or source.course_id != session_row.course_id:
            raise NotFoundError(f"Citation {doc_id} not found.")

        chunks = await ChunkRepo(db_session).list_by_source(doc_id)
        chunk = next((chunk for chunk in chunks if chunk.page == page), None)
        if chunk is None:
            raise NotFoundError(f"Citation {doc_id} page {page} not found.")

        return CitationPreviewDTO(
            doc_id=doc_id,
            page=page,
            span=span,
            source_filename=source.filename,
            passage=chunk.text,
        )


@router.get("/{session_id}", response_model=SessionDTO)
async def read_session(
    session_id: str,
    user: Annotated[Principal, Depends(current_user)],
    request: Request,
) -> SessionDTO:
    session_factory = request.app.state.session_factory
    async with session_factory() as db_session:
        session_repo = SessionRepo(db_session)
        session_row = await session_repo.get(session_id)
        if session_row is None:
            raise NotFoundError(f"Session {session_id} not found.")

        course = await CourseRepo(db_session).get(session_row.course_id)
        if course is None or course.org_id != user.org_id:
            raise NotFoundError(f"Session {session_id} not found.")

        questions = await QuestionRepo(db_session).list_by_session(session_id)
        answered_questions = await _count_answers(db_session, session_id)
        record = await db_session.scalar(
            select(CERecordModel).where(CERecordModel.session_id == session_id)
        )
        record_id = record.id if record is not None else None
        return _session_dto(session_row, questions, answered_questions, record_id)


@router.post("/{session_id}/answers", response_model=AnswerResultDTO)
async def record_answer(
    session_id: str,
    payload: AnswerDTO,
    user: Annotated[Principal, Depends(current_user)],
    request: Request,
) -> AnswerResultDTO:
    session_factory = request.app.state.session_factory
    async with session_factory() as db_session:
        session_repo = SessionRepo(db_session)
        session_row = await session_repo.get(session_id)
        if session_row is None:
            raise NotFoundError(f"Session {session_id} not found.")

        course = await CourseRepo(db_session).get(session_row.course_id)
        if course is None or course.org_id != user.org_id:
            raise NotFoundError(f"Session {session_id} not found.")

        service = _session_service(db_session)
        recorded = await service.record_answer(
            session_id,
            payload.question_id,
            payload.chosen_index,
        )
        session_row = recorded.session
        question = recorded.question

        return AnswerResultDTO(
            correct=recorded.answer.correct,
            correct_index=question.correct_index,
            rationale=question.rationale,
            citation=CitationDTO(
                doc_id=question.source_doc_id,
                page=question.source_page,
                span=question.source_span,
                url=_citation_url(
                    session_row.id,
                    question.source_doc_id,
                    question.source_page,
                    question.source_span,
                ),
            ),
            session_progress=SessionProgressDTO(
                answered=recorded.answered_questions,
                total=recorded.total_questions,
            ),
            score_pct=float(session_row.score_pct) if session_row.score_pct is not None else None,
            passed=session_row.passed,
        )


@ce_records_router.get("/{record_id}", response_model=CERecordDTO)
async def get_ce_record(
    record_id: str,
    user: Annotated[Principal, Depends(current_user)],
    request: Request,
) -> CERecordDTO:
    session_factory = request.app.state.session_factory
    async with session_factory() as db_session:
        record = await db_session.scalar(select(CERecordModel).where(CERecordModel.id == record_id))
        if record is None:
            raise NotFoundError(f"CE record {record_id} not found.")

        session_row = await db_session.get(SessionModel, record.session_id)
        if session_row is None:
            raise NotFoundError(f"CE record {record_id} not found.")

        course = await CourseRepo(db_session).get(session_row.course_id)
        if course is None or course.org_id != user.org_id:
            raise NotFoundError(f"CE record {record_id} not found.")

        return CERecordDTO(
            id=record.id,
            session_id=record.session_id,
            pdf_storage_key=record.pdf_storage_key,
            issued_at=record.issued_at,
            download_url=f"/api/ce-records/{record.id}/download",
        )


@ce_records_router.get("/{record_id}/download")
async def download_ce_record(
    record_id: str,
    user: Annotated[Principal, Depends(current_user)],
    request: Request,
) -> Response:
    session_factory = request.app.state.session_factory
    async with session_factory() as db_session:
        record = await db_session.scalar(select(CERecordModel).where(CERecordModel.id == record_id))
        if record is None:
            raise NotFoundError(f"CE record {record_id} not found.")

        session_row = await db_session.get(SessionModel, record.session_id)
        if session_row is None:
            raise NotFoundError(f"CE record {record_id} not found.")

        course = await CourseRepo(db_session).get(session_row.course_id)
        if course is None or course.org_id != user.org_id:
            raise NotFoundError(f"CE record {record_id} not found.")

        return Response(content=_pdf_bytes(record.id), media_type="application/pdf")


def _session_dto(
    session_row: SessionModel,
    questions: list[QuestionModel],
    answered_questions: int,
    record_id: str | None = None,
) -> SessionDTO:
        return SessionDTO(
        id=session_row.id,
        course_id=session_row.course_id,
        user_id=session_row.user_id,
        status="completed" if session_row.completed_at is not None else "in_progress",
        total_questions=len(questions),
        answered_questions=answered_questions,
        score_pct=float(session_row.score_pct) if session_row.score_pct is not None else None,
        passed=session_row.passed,
        record_id=record_id,
        questions=[
            QuestionDTO(
                id=question.id,
                text=question.text,
                options=_question_choices(question.options),
                citation=CitationDTO(
                    doc_id=question.source_doc_id,
                    page=question.source_page,
                    span=question.source_span,
                    url=_citation_url(
                        session_row.id,
                        question.source_doc_id,
                        question.source_page,
                        question.source_span,
                    ),
                ),
            )
            for question in questions
        ],
    )


def _citation_url(session_id: str, doc_id: str, page: int, span: str) -> str:
    return f"/sessions/{session_id}?cite={doc_id}:{page}:{span}"


def _question_choices(options: dict[str, object]) -> list[str]:
    choices = options.get("choices")
    if (
        not isinstance(choices, list)
        or not choices
        or not all(isinstance(choice, str) and choice.strip() for choice in choices)
    ):
        raise ValueError("Question options must include string choices.")
    return choices


async def _count_answers(session: AsyncSession, session_id: str) -> int:
    result = await session.scalar(
        select(func.count(AnswerModel.id))
        .select_from(AnswerModel)
        .join(QuestionModel, QuestionModel.id == AnswerModel.question_id)
        .where(QuestionModel.session_id == session_id)
    )
    return int(result or 0)


def _pdf_bytes(record_id: str) -> bytes:
    body = (
        "%PDF-1.4\n"
        "1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
        "2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
        "3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>endobj\n"
        f"4 0 obj<< /Length 44 >>stream\nPharmSmartCE record {record_id}\nendstream\nendobj\n"
        "xref\n0 5\n0000000000 65535 f \n"
        "trailer<< /Root 1 0 R /Size 5 >>\nstartxref\n0\n%%EOF\n"
    )
    return body.encode("utf-8")
