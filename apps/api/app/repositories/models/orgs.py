from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.repositories.db import Base, CreatedAtMixin


class OrgModel(Base, CreatedAtMixin):
    __tablename__ = "orgs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
