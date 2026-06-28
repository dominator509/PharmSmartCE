from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors import AuthError, ConflictError
from app.config import Settings
from app.repositories.models.orgs import OrgModel
from app.repositories.models.refresh_tokens import RefreshTokenModel
from app.repositories.models.users import UserModel
from app.repositories.refresh_token_repo import RefreshTokenRepo
from app.repositories.user_repo import UserRepo
from app.services.auth.tokens import (
    hash_password,
    issue_access_token,
    mint_refresh_token,
    parse_refresh_cookie,
    refresh_cookie_matches,
    verify_password,
)


@dataclass(slots=True)
class AuthResult:
    access_token: str
    expires_in: int
    refresh_cookie: str
    refresh_token: RefreshTokenModel
    user: UserModel


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)

    @property
    def refresh_tokens(self) -> RefreshTokenRepo:
        return RefreshTokenRepo(self.session)

    async def register(self, email: str, password: str) -> UserModel:
        existing = await self.users.get_by_email(email)
        if existing is not None:
            raise ConflictError("Email already registered.")

        org = OrgModel(id=uuid4().hex, name=f"Org {uuid4().hex[:8]}")
        user = UserModel(
            id=uuid4().hex,
            org_id=org.id,
            email=email,
            password_hash=hash_password(password),
            role="admin",
        )
        self.session.add(org)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def login(self, email: str, password: str) -> AuthResult:
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthError("Invalid email or password.")
        return await self._issue_session(user)

    async def refresh(self, refresh_cookie: str) -> AuthResult:
        token = await self._load_refresh_token(refresh_cookie)
        user = await self._load_user(token.user_id)

        if token.revoked_at is not None:
            await self.refresh_tokens.revoke_all_for_user(user.id)
            await self.session.commit()
            raise AuthError("Invalid refresh token.")

        jti, _ = parse_refresh_cookie(refresh_cookie)
        if token.jti != jti or not refresh_cookie_matches(
            self.settings.refresh_secret,
            refresh_cookie,
            token.token_sha256,
        ):
            await self.refresh_tokens.revoke_all_for_user(user.id)
            await self.session.commit()
            raise AuthError("Invalid refresh token.")

        new_jti, new_cookie, new_digest, expires_at = mint_refresh_token(
            secret=self.settings.refresh_secret,
            ttl_days=self.settings.refresh_token_ttl_days,
        )
        refreshed = RefreshTokenModel(
            jti=new_jti,
            user_id=user.id,
            token_sha256=new_digest,
            expires_at=expires_at,
            revoked_at=None,
            replaced_by_jti=None,
        )
        self.session.add(refreshed)
        await self.session.flush()
        token.revoked_at = datetime.now(UTC)
        token.replaced_by_jti = new_jti
        access_token, expires_in = issue_access_token(
            secret=self.settings.jwt_secret,
            user_id=user.id,
            org_id=user.org_id,
            role=user.role,
            ttl_minutes=self.settings.access_token_ttl_minutes,
        )
        await self.session.commit()
        return AuthResult(
            access_token=access_token,
            expires_in=expires_in,
            refresh_cookie=new_cookie,
            refresh_token=refreshed,
            user=user,
        )

    async def logout(self, refresh_cookie: str) -> None:
        token = await self._load_refresh_token(refresh_cookie)
        if token.revoked_at is not None:
            await self.refresh_tokens.revoke_all_for_user(token.user_id)
            await self.session.commit()
            raise AuthError("Invalid refresh token.")

        if not refresh_cookie_matches(
            self.settings.refresh_secret,
            refresh_cookie,
            token.token_sha256,
        ):
            await self.refresh_tokens.revoke_all_for_user(token.user_id)
            await self.session.commit()
            raise AuthError("Invalid refresh token.")

        await self.refresh_tokens.revoke(token.jti)
        await self.session.commit()

    async def _issue_session(self, user: UserModel) -> AuthResult:
        jti, refresh_cookie, digest, expires_at = mint_refresh_token(
            secret=self.settings.refresh_secret,
            ttl_days=self.settings.refresh_token_ttl_days,
        )
        refresh_token = RefreshTokenModel(
            jti=jti,
            user_id=user.id,
            token_sha256=digest,
            expires_at=expires_at,
            revoked_at=None,
            replaced_by_jti=None,
        )
        self.session.add(refresh_token)
        access_token, expires_in = issue_access_token(
            secret=self.settings.jwt_secret,
            user_id=user.id,
            org_id=user.org_id,
            role=user.role,
            ttl_minutes=self.settings.access_token_ttl_minutes,
        )
        await self.session.commit()
        return AuthResult(
            access_token=access_token,
            expires_in=expires_in,
            refresh_cookie=refresh_cookie,
            refresh_token=refresh_token,
            user=user,
        )

    async def _load_refresh_token(self, refresh_cookie: str) -> RefreshTokenModel:
        try:
            jti, _ = parse_refresh_cookie(refresh_cookie)
        except ValueError as exc:
            raise AuthError("Invalid refresh token.") from exc
        token = await self.refresh_tokens.get(jti)
        if token is None:
            raise AuthError("Invalid refresh token.")
        return token

    async def _load_user(self, user_id: str) -> UserModel:
        user = await self.users.get(user_id)
        if user is None:
            raise AuthError("Invalid refresh token.")
        return user
