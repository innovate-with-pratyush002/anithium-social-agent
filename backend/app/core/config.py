from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Anithium Social Agent"
    app_env: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(min_length=32)
    cors_origins: list[str] = ["http://localhost:3000"]
    database_url: str = "postgresql+asyncpg://anithium:change-me@localhost:5432/anithium"
    log_level: str = "INFO"
    access_token_expire_minutes: int = Field(default=1440, ge=5, le=10080)

    research_ingestion_interval_minutes: int = Field(default=60, ge=5, le=1440)
    research_analysis_interval_minutes: int = Field(default=30, ge=5, le=1440)
    research_ingestion_max_items_per_source: int = Field(default=20, ge=1, le=50)
    research_analysis_max_items: int = Field(default=10, ge=1, le=20)

    ai_provider: Literal["groq", "openai", "gemini"] = "groq"

    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-20b"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
