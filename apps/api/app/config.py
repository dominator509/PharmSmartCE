from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    log_level: str = "info"
    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/pharm"
    citation_min_overlap_ratio: float = 0.4


def get_settings() -> Settings:
    return Settings()
