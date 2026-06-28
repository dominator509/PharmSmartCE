from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4
from xml.etree import ElementTree as ET

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.llm import FakeLLM
from app.api.errors import NotFoundError, UnreadyError
from app.config import Settings
from app.domain.entities import Chunk
from app.domain.errors import GroundingError as QuestionGroundingError
from app.domain.errors import InsufficientContextError
from app.observability.metrics import (
    record_citation_overlap,
    record_generation_retry,
    record_grounding_failure,
    record_llm_generation,
)
from app.repositories.course_repo import CourseRepo
from app.repositories.models.questions import QuestionModel
from app.repositories.models.sessions import SessionModel
from app.repositories.models.sources import SourceModel
from app.repositories.question_repo import QuestionRepo
from app.repositories.session_repo import SessionRepo
from app.repositories.source_repo import SourceRepo
from app.services.generation.citation_validator import compute_overlap
from app.services.generation.cost_cap import OpenAICostCap
from app.services.generation.grounded_llm import GroundedLLM
from app.services.generation.injection_detector import InjectionDetector
from app.services.ports.llm import LLMPort
from app.services.ports.storage import StoragePort


@dataclass(slots=True)
class StartedSession:
    session: SessionModel
    questions: list[QuestionModel]
    source: SourceModel


@dataclass(slots=True)
class GenerationService:
    session: AsyncSession
    storage: StoragePort
    settings: Settings | None = None
    local_llm: LLMPort | None = None
    openai_llm: LLMPort | None = None
    cost_cap: OpenAICostCap | None = None

    @property
    def courses(self) -> CourseRepo:
        return CourseRepo(self.session)

    @property
    def sessions(self) -> SessionRepo:
        return SessionRepo(self.session)

    @property
    def sources(self) -> SourceRepo:
        return SourceRepo(self.session)

    @property
    def questions(self) -> QuestionRepo:
        return QuestionRepo(self.session)

    async def start_session(self, user_id: str, org_id: str, course_id: str) -> StartedSession:
        course = await self.courses.get(course_id)
        if course is None:
            raise NotFoundError(f"Course {course_id} not found.")
        if course.org_id != org_id:
            raise NotFoundError(f"Course {course_id} not found.")

        sources = await self.sources.list_by_course(course_id)
        if not sources:
            raise UnreadyError("Course has no uploaded source yet.")

        source = max(sources, key=lambda item: item.created_at or datetime.min.replace(tzinfo=UTC))
        content = await self.storage.load_source(course_id, source.id, source.filename)
        text = _normalize_text(content, source.filename, source.sha256)
        detector = InjectionDetector()
        settings = self.settings or Settings()
        source_flagged = detector.is_flagged(text)

        session_row = SessionModel(
            id=uuid4().hex,
            course_id=course_id,
            user_id=user_id,
            seed=uuid4().hex,
            started_at=datetime.now(UTC),
            completed_at=None,
            score_pct=None,
            passed=None,
        )
        self.session.add(session_row)
        await self.session.flush()

        questions: list[QuestionModel] = []
        flagged_chunks = 0
        total_chunks = 0
        for index, chunk in enumerate(_build_chunks(source.id, text, course.n_questions), start=1):
            total_chunks += 1
            if detector.is_flagged(chunk.text):
                flagged_chunks += 1
                record_grounding_failure("injection_flagged")
                continue
            provider_name, llm = await self._select_llm(settings)
            grounded_llm = GroundedLLM(llm=llm)
            start = perf_counter()
            try:
                generated = grounded_llm.generate_question(chunk)
            except InsufficientContextError:
                record_grounding_failure("refused")
                raise
            except QuestionGroundingError:
                record_grounding_failure("overlap_low")
                raise
            finally:
                record_llm_generation(provider_name, perf_counter() - start)
            question = QuestionModel(
                id=uuid4().hex,
                session_id=session_row.id,
                text=generated.stem,
                options={"choices": list(generated.choices)},
                correct_index=generated.correct_choice_index,
                rationale=generated.rationale,
                source_doc_id=generated.source_doc_id,
                source_page=generated.source_page or index,
                source_span=generated.source_span,
                citation_overlap=compute_overlap(generated.rationale, chunk.text),
            )
            record_citation_overlap(question.citation_overlap)
            self.session.add(question)
            questions.append(question)

        if source_flagged or (total_chunks and flagged_chunks / total_chunks > 0.25):
            source_row = await self.sources.get(source.id)
            if source_row is not None:
                source_row.status = "quarantined"
                source_row.last_error = "Prompt injection detector flagged too many chunks."
            record_generation_retry("exhausted")
            await self.session.commit()
            raise UnreadyError("Source quarantined due to prompt injection detection.")

        await self.session.commit()
        return StartedSession(session=session_row, questions=questions, source=source)

    async def _select_llm(self, settings: Settings) -> tuple[str, LLMPort]:
        local_llm = self.local_llm or FakeLLM()
        if settings.llm_provider != "openai":
            return "fake", local_llm

        cost_cap = self.cost_cap or OpenAICostCap(
            session=self.session,
            monthly_cap_usd=settings.openai_monthly_usd_cap,
        )
        if not await cost_cap.allow():
            return "fake", local_llm

        return "openai", self.openai_llm or local_llm


def _normalize_text(content: bytes, filename: str, sha256_hex: str) -> str:
    if filename.lower().endswith(".docx") or zipfile.is_zipfile(io.BytesIO(content)):
        extracted = _extract_docx_text(content)
        if extracted:
            return extracted
    text = content.decode("utf-8", errors="ignore")
    normalized = " ".join(text.split()).strip()
    if normalized:
        return normalized
    return f"{filename} {sha256_hex}"


def _extract_docx_text(content: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            document = archive.read("word/document.xml")
    except (KeyError, OSError, zipfile.BadZipFile):
        return ""

    try:
        root = ET.fromstring(document)
    except ET.ParseError:
        return ""

    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    text_nodes = [node.text or "" for node in root.findall(".//w:t", namespace)]
    normalized = " ".join(" ".join(text_nodes).split()).strip()
    return normalized


def _build_chunks(doc_id: str, text: str, count: int) -> list[Chunk]:
    if count <= 0:
        return []

    normalized = text.strip() or "Uploaded source material."
    chunk_size = max(1, len(normalized) // count)
    chunks: list[Chunk] = []
    for index in range(count):
        start = index * chunk_size
        end = len(normalized) if index == count - 1 else min(len(normalized), start + chunk_size)
        segment = normalized[start:end].strip() or normalized
        chunks.append(
            Chunk(
                doc_id=doc_id,
                page=index + 1,
                span=f"p{index + 1}:s1-s{max(1, len(segment))}",
                text=segment,
            )
        )
    return chunks
