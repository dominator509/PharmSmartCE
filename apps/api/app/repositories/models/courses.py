from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.repositories.db import Base, CreatedAtMixin


class CourseModel(Base, CreatedAtMixin):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("status in ('draft', 'ready')", name="ck_courses_status"),
        CheckConstraint("pass_pct >= 50 and pass_pct <= 100", name="ck_courses_pass_pct"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    org_id: Mapped[str] = mapped_column(String, ForeignKey("orgs.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    n_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=6)
    pass_pct: Mapped[int] = mapped_column(Integer, nullable=False, default=70)
    status: Mapped[str] = mapped_column(String, nullable=False)
