from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "SumScriptBro API"
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")

    telegram_token: str = Field(default="", alias="TELEGRAM_TOKEN")
    telegram_webhook_secret: str = Field(default="", alias="TELEGRAM_WEBHOOK_SECRET")
    telegram_max_media_size_bytes: int = Field(
        default=50 * 1024 * 1024,
        alias="TELEGRAM_MAX_MEDIA_SIZE_BYTES",
    )
    telegram_max_media_duration_seconds: int = Field(
        default=120 * 60,
        alias="TELEGRAM_MAX_MEDIA_DURATION_SECONDS",
    )
    telegram_large_file_threshold_bytes: int = Field(
        default=20 * 1024 * 1024,
        alias="TELEGRAM_LARGE_FILE_THRESHOLD_BYTES",
    )

    db_dsn: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/sumscriptbro",
        alias="DB_DSN",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    s3_access_key_id: str = Field(default="", alias="S3_ACCESS_KEY_ID")
    s3_secret_access_key: str = Field(default="", alias="S3_SECRET_ACCESS_KEY")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")
    s3_bucket: str = Field(default="sumscriptbro", alias="S3_BUCKET")
    s3_endpoint_url: str = Field(default="", alias="S3_ENDPOINT_URL")

    otlp_endpoint: str = Field(default="http://localhost:4317", alias="OTLP_ENDPOINT")
    otel_service_name: str = Field(default="sumscriptbro-backend", alias="OTEL_SERVICE_NAME")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
