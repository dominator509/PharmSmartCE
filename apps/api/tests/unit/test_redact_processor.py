from __future__ import annotations

from app.observability.logging import RedactProcessor


def test_redact_processor_scrubs_sensitive_keys_recursively() -> None:
    processor = RedactProcessor()
    payload = {
        "user": "alice",
        "password": "secret",
        "nested": {"authorization": "Bearer token", "safe": "value"},
        "items": [{"api_key": "abc123"}, "ok"],
    }

    redacted = processor(None, "info", payload)

    assert redacted["password"] == "[REDACTED]"
    assert redacted["nested"]["authorization"] == "[REDACTED]"
    assert redacted["items"][0]["api_key"] == "[REDACTED]"
    assert redacted["user"] == "alice"
