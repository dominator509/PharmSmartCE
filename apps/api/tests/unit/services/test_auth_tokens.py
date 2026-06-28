from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC

import pytest

from app.services.auth.tokens import (
    digest_refresh_cookie,
    hash_password,
    issue_access_token,
    mint_refresh_token,
    parse_refresh_cookie,
    refresh_cookie_matches,
    verify_access_token,
    verify_password,
)


def test_password_hash_round_trip() -> None:
    password_hash = hash_password("secretsecret12")

    assert verify_password("secretsecret12", password_hash)
    assert not verify_password("wrongpassword12", password_hash)


def test_access_token_issue_and_verify_round_trip() -> None:
    token, expires_in = issue_access_token(
        secret="local-secret",
        user_id="user-1",
        org_id="org-1",
        role="admin",
        ttl_minutes=15,
    )

    claims = verify_access_token("local-secret", token)

    assert expires_in == 900
    assert claims.user_id == "user-1"
    assert claims.org_id == "org-1"
    assert claims.role == "admin"
    assert claims.expires_at.tzinfo == UTC
    assert claims.jti


def test_access_token_rejects_expired_tokens() -> None:
    token, _ = issue_access_token(
        secret="local-secret",
        user_id="user-1",
        org_id="org-1",
        role="admin",
        ttl_minutes=-1,
    )

    with pytest.raises(ValueError):
        verify_access_token("local-secret", token)


def test_access_token_rejects_missing_claims() -> None:
    token, _ = issue_access_token(
        secret="local-secret",
        user_id="user-1",
        org_id="org-1",
        role="admin",
        ttl_minutes=15,
    )

    header_b64, payload_b64, _ = token.split(".")
    payload = json.loads(_base64url_decode(payload_b64))
    payload.pop("exp")
    tampered_token = _sign_jwt(header_b64, payload, "local-secret")

    with pytest.raises(ValueError):
        verify_access_token("local-secret", tampered_token)


def test_access_token_rejects_non_object_header() -> None:
    payload = {
        "sub": "user-1",
        "org_id": "org-1",
        "role": "admin",
        "iat": 1,
        "exp": 2,
        "jti": "token-id",
    }
    token = _sign_jwt(_base64url_encode(b"[]"), payload, "local-secret")

    with pytest.raises(ValueError):
        verify_access_token("local-secret", token)


def test_refresh_cookie_helpers_round_trip() -> None:
    jti, cookie, digest, _ = mint_refresh_token(secret="local-secret", ttl_days=30)

    parsed_jti, raw = parse_refresh_cookie(cookie)
    assert parsed_jti == jti
    assert raw
    assert digest == digest_refresh_cookie("local-secret", cookie)
    assert refresh_cookie_matches("local-secret", cookie, digest)
    assert not refresh_cookie_matches("local-secret", f"{cookie}x", digest)


def test_parse_refresh_cookie_rejects_invalid_format() -> None:
    with pytest.raises(ValueError):
        parse_refresh_cookie("missing-delimiter")


def _sign_jwt(header_b64: str, payload: dict[str, object], secret: str) -> str:
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_b64}.{payload_b64}.{_base64url_encode(signature)}"


def _base64url_encode(payload: bytes) -> str:
    return base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")


def _base64url_decode(payload: str) -> bytes:
    padding = "=" * (-len(payload) % 4)
    return base64.urlsafe_b64decode(payload + padding)
