from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.db import AsyncRepository
from app.repositories.models.questions import QuestionModel


class QuestionRepo(AsyncRepository[QuestionModel]):
    model = QuestionModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_session(self, session_id: str) -> list[QuestionModel]:
        result = await self.session.scalars(
            select(QuestionModel)
            .where(QuestionModel.session_id == session_id)
            .order_by(QuestionModel.id)
        )
        return list(result)
