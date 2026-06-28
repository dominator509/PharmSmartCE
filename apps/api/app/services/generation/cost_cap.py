from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.observability.metrics import (
    record_openai_cap_reached,
    record_openai_cap_warn_80,
    set_openai_monthly_spend,
)
from app.repositories.openai_cost_repo import OpenAICostRepo


@dataclass(slots=True)
class OpenAICostCap:
    session: AsyncSession
    monthly_cap_usd: float

    def __post_init__(self) -> None:
        if self.monthly_cap_usd <= 0:
            raise ValueError("OpenAI monthly cap must be positive.")

    @property
    def repo(self) -> OpenAICostRepo:
        return OpenAICostRepo(self.session)

    async def allow(self) -> bool:
        year_month = datetime.now(UTC).strftime("%Y-%m")
        ledger = await self.repo.get_by_year_month(year_month)
        spend = float(ledger.usd) if ledger is not None else 0.0
        set_openai_monthly_spend(year_month, spend)

        if spend >= self.monthly_cap_usd:
            record_openai_cap_reached()
            return False
        if spend >= self.monthly_cap_usd * 0.8:
            record_openai_cap_warn_80()
        return True
