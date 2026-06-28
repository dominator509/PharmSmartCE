from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.db import AsyncRepository
from app.repositories.models.refresh_tokens import RefreshTokenModel


class RefreshTokenRepo(AsyncRepository[RefreshTokenModel]):
    model = RefreshTokenModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_user(self, user_id: str) -> list[RefreshTokenModel]:
        result = await self.session.scalars(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .order_by(RefreshTokenModel.expires_at)
        )
        return list(result)

    async def revoke(
        self,
        jti: str,
        replaced_by_jti: str | None = None,
    ) -> RefreshTokenModel | None:
        token = await self.get(jti)
        if token is None:
            return None
        token.revoked_at = datetime.now(UTC)
        token.replaced_by_jti = replaced_by_jti
        await self.session.flush()
        return token

    async def revoke_all_for_user(self, user_id: str) -> list[RefreshTokenModel]:
        tokens = await self.get_by_user(user_id)
        now = datetime.now(UTC)
        for token in tokens:
            token.revoked_at = token.revoked_at or now
        await self.session.flush()
        return tokens
