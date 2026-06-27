from app.config import get_settings


def test_get_settings_exposes_citation_overlap_threshold() -> None:
    settings = get_settings()

    assert settings.app_env == "local"
    assert settings.log_level == "info"
    assert settings.database_url == "postgresql+asyncpg://app:app@localhost:5432/pharm"
    assert settings.citation_min_overlap_ratio == 0.4
