from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.db import AsyncRepository
from app.repositories.models.openai_cost_ledger import OpenAICostLedgerModel


class OpenAICostRepo(AsyncRepository[OpenAICostLedgerModel]):
    model = OpenAICostLedgerModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_year_month(self, year_month: str) -> OpenAICostLedgerModel | None:
        result = await self.session.scalars(
            select(OpenAICostLedgerModel).where(OpenAICostLedgerModel.year_month == year_month)
        )
        return result.first()
