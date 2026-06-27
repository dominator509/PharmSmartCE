from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.db import AsyncRepository
from app.repositories.models.chunks import ChunkModel


class ChunkRepo(AsyncRepository[ChunkModel]):
    model = ChunkModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_source(self, source_id: str) -> list[ChunkModel]:
        result = await self.session.scalars(
            select(ChunkModel).where(ChunkModel.source_id == source_id).order_by(ChunkModel.page)
        )
        return list(result)
