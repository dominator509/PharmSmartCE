from __future__ import annotations

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.repositories.db import Base, UpdatedAtMixin


class OpenAICostLedgerModel(Base, UpdatedAtMixin):
    __tablename__ = "openai_cost_ledger"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    year_month: Mapped[str] = mapped_column(String(7), nullable=False)
    usd: Mapped[float] = mapped_column(Numeric, nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False)
