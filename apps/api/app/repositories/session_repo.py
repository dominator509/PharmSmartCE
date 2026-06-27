from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.db import AsyncRepository
from app.repositories.models.sessions import SessionModel


class SessionRepo(AsyncRepository[SessionModel]):
    model = SessionModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_user_course(self, user_id: str, course_id: str) -> list[SessionModel]:
        result = await self.session.scalars(
            select(SessionModel)
            .where(SessionModel.user_id == user_id)
            .where(SessionModel.course_id == course_id)
            .order_by(SessionModel.started_at.desc())
        )
        return list(result)
