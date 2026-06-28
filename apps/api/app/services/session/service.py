from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors import ConflictError, NotFoundError
from app.repositories.course_repo import CourseRepo
from app.repositories.models.answers import AnswerModel
from app.repositories.models.ce_records import CERecordModel
from app.repositories.models.questions import QuestionModel
from app.repositories.models.sessions import SessionModel
from app.repositories.question_repo import QuestionRepo
from app.repositories.session_repo import SessionRepo


@dataclass(slots=True)
class RecordedAnswer:
    answer: AnswerModel
    question: QuestionModel
    session: SessionModel
    total_questions: int
    answered_questions: int
    correct_questions: int


@dataclass(slots=True)
class SessionService:
    session: AsyncSession

    @property
    def courses(self) -> CourseRepo:
        return CourseRepo(self.session)

    @property
    def sessions(self) -> SessionRepo:
        return SessionRepo(self.session)

    @property
    def questions(self) -> QuestionRepo:
        return QuestionRepo(self.session)

    async def record_answer(
        self,
        session_id: str,
        question_id: str,
        chosen_index: int,
    ) -> RecordedAnswer:
        session_row = await self.sessions.get(session_id)
        if session_row is None:
            raise NotFoundError(f"Session {session_id} not found.")

        question = await self.questions.get(question_id)
        if question is None or question.session_id != session_id:
            raise NotFoundError(f"Question {question_id} not found.")

        duplicate = await self.session.scalar(
            select(AnswerModel).where(AnswerModel.question_id == question_id)
        )
        if duplicate is not None:
            raise ConflictError("Answer already recorded for this question.")

        answer = AnswerModel(
            id=uuid4().hex,
            question_id=question_id,
            chosen_index=chosen_index,
            correct=chosen_index == question.correct_index,
            answered_at=datetime.now(UTC),
        )
        self.session.add(answer)
        await self.session.flush()

        total_questions = await self._count_questions(session_id)
        answered_questions = await self._count_answers(session_id)
        correct_questions = await self._count_correct_answers(session_id)

        course = await self.courses.get(session_row.course_id)
        if course is None:
            raise NotFoundError(f"Course {session_row.course_id} not found.")

        if total_questions and answered_questions >= total_questions:
            score_pct = round(correct_questions / total_questions * 100, 2)
            session_row.completed_at = datetime.now(UTC)
            session_row.score_pct = score_pct
            session_row.passed = score_pct >= course.pass_pct
            self.session.add(
                CERecordModel(
                    id=uuid4().hex,
                    session_id=session_row.id,
                    pdf_storage_key=f"records/{session_row.id}.pdf",
                    issued_at=datetime.now(UTC),
                )
            )

        await self.session.commit()
        return RecordedAnswer(
            answer=answer,
            question=question,
            session=session_row,
            total_questions=total_questions,
            answered_questions=answered_questions,
            correct_questions=correct_questions,
        )

    async def _count_questions(self, session_id: str) -> int:
        result = await self.session.scalar(
            select(func.count(QuestionModel.id)).where(QuestionModel.session_id == session_id)
        )
        return int(result or 0)

    async def _count_answers(self, session_id: str) -> int:
        result = await self.session.scalar(
            select(func.count(AnswerModel.id))
            .select_from(AnswerModel)
            .join(QuestionModel, QuestionModel.id == AnswerModel.question_id)
            .where(QuestionModel.session_id == session_id)
        )
        return int(result or 0)

    async def _count_correct_answers(self, session_id: str) -> int:
        result = await self.session.scalar(
            select(func.count(AnswerModel.id))
            .select_from(AnswerModel)
            .join(QuestionModel, QuestionModel.id == AnswerModel.question_id)
            .where(QuestionModel.session_id == session_id)
            .where(AnswerModel.correct.is_(True))
        )
        return int(result or 0)
