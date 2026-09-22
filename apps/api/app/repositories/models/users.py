from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.repositories.db import Base, CreatedAtMixin


class UserModel(Base, CreatedAtMixin):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role in ('admin', 'member')", name="ck_users_role"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    org_id: Mapped[str] = mapped_column(String, ForeignKey("orgs.id"), nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
