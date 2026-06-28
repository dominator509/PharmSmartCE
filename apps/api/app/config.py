from base64 import b64decode
from binascii import Error as BinasciiError

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    log_level: str = "info"
    image_sha: str = "dev"
    llm_provider: str = "fake"
    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/pharm"
    jwt_secret: str = "dev-jwt-secret"
    refresh_secret: str = "dev-refresh-secret"
    sentry_dsn: str = ""
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30
    rate_limit_default: str = "30/minute"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_monthly_usd_cap: float = 50.0
    faiss_index_dir: str = "var/faiss"
    storage_root: str = "var/uploads"
    upload_max_bytes: int = 52_428_800
    citation_min_overlap_ratio: float = 0.4

    @field_validator("jwt_secret", "refresh_secret")
    @classmethod
    def _validate_secret(cls, value: str, info: ValidationInfo) -> str:
        app_env = str(info.data.get("app_env", "local"))
        if not value:
            raise ValueError("Auth secrets must not be empty.")
        if app_env in {"staging", "prod"}:
            try:
                decoded = b64decode(value, validate=True)
            except (BinasciiError, ValueError) as exc:
                raise ValueError("Auth secrets must be base64-encoded in staging/prod.") from exc
            if len(decoded) < 32:
                raise ValueError("Auth secrets must decode to at least 32 bytes.")
        return value

    @field_validator("access_token_ttl_minutes", "refresh_token_ttl_days")
    @classmethod
    def _validate_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("TTL values must be positive.")
        return value

    @field_validator("llm_provider")
    @classmethod
    def _validate_llm_provider(cls, value: str) -> str:
        if value not in {"llama_cpp", "openai", "fake"}:
            raise ValueError("LLM provider must be llama_cpp, openai, or fake.")
        return value

    @field_validator("openai_api_key")
    @classmethod
    def _validate_openai_api_key(cls, value: str, info: ValidationInfo) -> str:
        llm_provider = str(info.data.get("llm_provider", "fake"))
        if llm_provider == "openai" and not value:
            raise ValueError("OpenAI API key is required when LLM provider is openai.")
        return value

    @field_validator("openai_model")
    @classmethod
    def _validate_openai_model(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("OpenAI model must not be empty.")
        return value

    @field_validator("openai_monthly_usd_cap")
    @classmethod
    def _validate_openai_monthly_usd_cap(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("OpenAI monthly USD cap must be positive.")
        return value

    @field_validator("rate_limit_default")
    @classmethod
    def _validate_rate_limit_default(cls, value: str) -> str:
        if "/" not in value:
            raise ValueError("Rate limit must use '<limit>/<unit>' format.")
        limit_part, unit = value.split("/", 1)
        if not limit_part.isdigit() or int(limit_part) <= 0:
            raise ValueError("Rate limit limit must be positive.")
        if unit not in {"second", "minute", "hour"}:
            raise ValueError("Rate limit unit must be second, minute, or hour.")
        return value


def get_settings() -> Settings:
    return Settings()
