from __future__ import annotations

from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.repositories.db import Base, CreatedAtMixin


class QuestionModel(Base, CreatedAtMixin):
    __tablename__ = "questions"
    __table_args__ = (
        CheckConstraint(
            "citation_overlap >= 0 and citation_overlap <= 1",
            name="ck_questions_citation_overlap",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String, ForeignKey("sessions.id"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    correct_index: Mapped[int] = mapped_column(Integer, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    source_doc_id: Mapped[str] = mapped_column(String, ForeignKey("sources.id"), nullable=False)
    source_page: Mapped[int] = mapped_column(Integer, nullable=False)
    source_span: Mapped[str] = mapped_column(Text, nullable=False)
    citation_overlap: Mapped[float] = mapped_column(Numeric, nullable=False)
