from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.db import AsyncRepository
from app.repositories.models.sources import SourceModel


class SourceRepo(AsyncRepository[SourceModel]):
    model = SourceModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_course(self, course_id: str) -> list[SourceModel]:
        result = await self.session.scalars(
            select(SourceModel)
            .where(SourceModel.course_id == course_id)
            .order_by(SourceModel.filename)
        )
        return list(result)
