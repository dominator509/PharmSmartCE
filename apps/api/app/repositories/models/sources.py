from __future__ import annotations

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.repositories.db import Base, CreatedAtMixin


class SourceModel(Base, CreatedAtMixin):
    __tablename__ = "sources"
    __table_args__ = (
        CheckConstraint(
            "status in ('uploaded', 'ingesting', 'ready', 'failed', 'quarantined')",
            name="ck_sources_status",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    course_id: Mapped[str] = mapped_column(
        String, ForeignKey("courses.id"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    bytes_: Mapped[int] = mapped_column("bytes", BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text)
