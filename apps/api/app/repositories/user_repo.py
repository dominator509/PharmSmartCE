from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.db import AsyncRepository
from app.repositories.models.users import UserModel


class UserRepo(AsyncRepository[UserModel]):
    model = UserModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self.session.scalars(select(UserModel).where(UserModel.email == email))
        return result.first()

    async def list_by_org(self, org_id: str) -> list[UserModel]:
        result = await self.session.scalars(
            select(UserModel).where(UserModel.org_id == org_id).order_by(UserModel.email)
        )
        return list(result)
