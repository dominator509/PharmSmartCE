from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError

PASSWORD_HASHER = PasswordHasher(
    time_cost=3,
    memory_cost=19_456,
    parallelism=1,
    salt_len=16,
    hash_len=32,
    type=Type.ID,
)


@dataclass(slots=True)
class AccessTokenClaims:
    user_id: str
    org_id: str
    role: str
    expires_at: datetime
    jti: str


def hash_password(password: str) -> str:
    return PASSWORD_HASHER.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return PASSWORD_HASHER.verify(password_hash, password)
    except (InvalidHash, VerificationError, VerifyMismatchError):
        return False


def issue_access_token(
    *,
    secret: str,
    user_id: str,
    org_id: str,
    role: str,
    ttl_minutes: int,
) -> tuple[str, int]:
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=ttl_minutes)
    payload = {
        "sub": user_id,
        "org_id": org_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": uuid4().hex,
    }
    token = _encode_jwt(payload, secret)
    return token, int((expires_at - now).total_seconds())


def verify_access_token(secret: str, token: str) -> AccessTokenClaims:
    payload = _decode_jwt(token, secret)
    expires_at = datetime.fromtimestamp(int(payload["exp"]), tz=UTC)
    if expires_at <= datetime.now(UTC):
        raise ValueError("Access token expired.")
    return AccessTokenClaims(
        user_id=str(payload["sub"]),
        org_id=str(payload["org_id"]),
        role=str(payload["role"]),
        expires_at=expires_at,
        jti=str(payload["jti"]),
    )


def mint_refresh_token(
    *,
    secret: str,
    ttl_days: int,
) -> tuple[str, str, str, datetime]:
    jti = uuid4().hex
    raw = secrets.token_urlsafe(32)
    cookie = f"{jti}.{raw}"
    expires_at = datetime.now(UTC) + timedelta(days=ttl_days)
    digest = digest_refresh_cookie(secret, cookie)
    return jti, cookie, digest, expires_at


def parse_refresh_cookie(cookie: str) -> tuple[str, str]:
    parts = cookie.split(".", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("Invalid refresh cookie.")
    return parts[0], parts[1]


def digest_refresh_cookie(secret: str, cookie: str) -> str:
    return hmac.new(_secret_bytes(secret), cookie.encode("utf-8"), hashlib.sha256).hexdigest()


def refresh_cookie_matches(secret: str, cookie: str, digest: str) -> bool:
    return hmac.compare_digest(digest_refresh_cookie(secret, cookie), digest)


def _encode_jwt(payload: dict[str, Any], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_bytes = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_bytes = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_bytes}.{payload_bytes}".encode("ascii")
    signature = hmac.new(_secret_bytes(secret), signing_input, hashlib.sha256).digest()
    return f"{header_bytes}.{payload_bytes}.{_base64url_encode(signature)}"


def _decode_jwt(token: str, secret: str) -> dict[str, Any]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as exc:
        raise ValueError("Invalid access token.") from exc

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected_signature = hmac.new(_secret_bytes(secret), signing_input, hashlib.sha256).digest()
    actual_signature = _base64url_decode(signature_b64)
    if not hmac.compare_digest(expected_signature, actual_signature):
        raise ValueError("Invalid access token.")

    header = json.loads(_base64url_decode(header_b64))
    if header.get("alg") != "HS256":
        raise ValueError("Invalid access token.")

    payload = json.loads(_base64url_decode(payload_b64))
    if not isinstance(payload, dict):
        raise ValueError("Invalid access token.")
    return payload


def _secret_bytes(secret: str) -> bytes:
    try:
        return base64.b64decode(secret, validate=True)
    except (binascii.Error, ValueError):
        return secret.encode("utf-8")


def _base64url_encode(payload: bytes) -> str:
    return base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")


def _base64url_decode(payload: str) -> bytes:
    padding = "=" * (-len(payload) % 4)
    return base64.urlsafe_b64decode(payload + padding)
