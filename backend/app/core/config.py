from pydantic_settings import BaseSettings, SettingsConfigDict

from pathlib import Path


class Settings(BaseSettings):
    database_url: str

    s3_endpoint_url: str
    s3_access_key_id: str
    s3_secret_access_key: str
    s3_bucket: str = "shop-products"
    s3_region: str = "us-east-1"

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        env_file=Path(__file__).resolve().parents[3] / ".env",
    )


settings = Settings()