from app.config import get_settings


def test_get_settings_exposes_citation_overlap_threshold() -> None:
    settings = get_settings()

    assert settings.app_env == "local"
    assert settings.log_level == "info"
    assert settings.llm_provider == "fake"
    assert settings.database_url == "postgresql+asyncpg://app:app@localhost:5432/pharm"
    assert settings.jwt_secret == "dev-jwt-secret"
    assert settings.refresh_secret == "dev-refresh-secret"
    assert settings.access_token_ttl_minutes == 15
    assert settings.refresh_token_ttl_days == 30
    assert settings.rate_limit_default == "30/minute"
    assert settings.openai_api_key == ""
    assert settings.openai_model == "gpt-4o-mini"
    assert settings.openai_monthly_usd_cap == 50.0
    assert settings.faiss_index_dir == "var/faiss"
    assert settings.storage_root == "var/uploads"
    assert settings.upload_max_bytes == 52_428_800
    assert settings.citation_min_overlap_ratio == 0.4
