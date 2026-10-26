from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    s3_endpoint_url: str
    s3_access_key_id: str
    s3_secret_access_key: str
    s3_bucket: str = "shop-products"
    s3_region: str = "us-east-1"

    telegram_bot_token: str | None = None
    telegram_admin_ids: str = ""
    telegram_webapp_url: str = ""
    telegram_webhook_secret: str = ""


    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        env_file=Path(__file__).resolve().parents[3] / ".env",
    )


settings = Settings()