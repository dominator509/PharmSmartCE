from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.db import AsyncRepository
from app.repositories.models.courses import CourseModel


class CourseRepo(AsyncRepository[CourseModel]):
    model = CourseModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_org(self, org_id: str) -> list[CourseModel]:
        result = await self.session.scalars(
            select(CourseModel).where(CourseModel.org_id == org_id).order_by(CourseModel.title)
        )
        return list(result)
