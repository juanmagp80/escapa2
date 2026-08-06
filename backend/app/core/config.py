"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed access to environment configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = "Escapa2 Radar API"
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    app_debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    database_url: str = Field(
        default="postgresql+psycopg://escapa2:escapa2@localhost:5432/escapa2",
        validation_alias="DATABASE_URL",
    )
    persistence_backend: str = Field(
        default="memory",
        validation_alias="PERSISTENCE_BACKEND",
    )
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:8080"],
        validation_alias="CORS_ALLOWED_ORIGINS",
    )

    gemini_enabled: bool = Field(default=False, validation_alias="GEMINI_ENABLED")
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.6-flash", validation_alias="GEMINI_MODEL")
    gemini_timeout_seconds: float = Field(default=30.0, validation_alias="GEMINI_TIMEOUT_SECONDS")
    gemini_max_requests_per_user_day: int = Field(
        default=20, validation_alias="GEMINI_MAX_REQUESTS_PER_USER_DAY"
    )

    scheduler_enabled: bool = Field(default=False, validation_alias="SCHEDULER_ENABLED")
    scheduler_interval_seconds: float = Field(
        default=60.0, validation_alias="SCHEDULER_INTERVAL_SECONDS"
    )

    amadeus_enabled: bool = Field(default=False, validation_alias="AMADEUS_ENABLED")
    amadeus_client_id: str = Field(default="", validation_alias="AMADEUS_CLIENT_ID")
    amadeus_client_secret: str = Field(default="", validation_alias="AMADEUS_CLIENT_SECRET")
    amadeus_base_url: str = Field(
        default="https://test.api.amadeus.com", validation_alias="AMADEUS_BASE_URL"
    )
    amadeus_timeout_seconds: float = Field(default=15.0, validation_alias="AMADEUS_TIMEOUT_SECONDS")

    firebase_enabled: bool = Field(default=False, validation_alias="FIREBASE_ENABLED")
    firebase_project_id: str = Field(default="", validation_alias="FIREBASE_PROJECT_ID")
    firebase_credentials_file: str = Field(default="", validation_alias="FIREBASE_CREDENTIALS_FILE")
    firebase_credentials_json: str = Field(default="", validation_alias="FIREBASE_CREDENTIALS_JSON")

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def uses_sql_persistence(self) -> bool:
        return self.persistence_backend == "sql"

    def validate_provider_credentials(self) -> None:
        """Fail fast when a provider is enabled without its credentials."""
        if self.amadeus_enabled and not (self.amadeus_client_id and self.amadeus_client_secret):
            raise RuntimeError(
                "AMADEUS_ENABLED=true requires AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET"
            )
        if self.firebase_enabled and not (
            self.firebase_credentials_file or self.firebase_credentials_json
        ):
            raise RuntimeError(
                "FIREBASE_ENABLED=true requires FIREBASE_CREDENTIALS_FILE "
                "or FIREBASE_CREDENTIALS_JSON (service account JSON)"
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()
