from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "Finance Data API"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite+pysqlite:///./finance.db"

    JWT_SECRET_KEY: str = "change-this-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    RATE_LIMIT_PER_MINUTE: int = Field(default=120, ge=1)
    REPORT_SCHEDULER_ENABLED: bool = True
    REPORT_SCHEDULE_MINUTES: int = Field(default=60, ge=1)
    REPORT_LOOKBACK_DAYS: int = Field(default=1, ge=1, le=365)

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
