from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Inter Reels API"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./inter.db"
    cors_origins: str = "http://127.0.0.1:8080,http://localhost:8080,https://inter-1xr.pages.dev"
    media_root: Path = Path("/data/media")
    seed_demo_data: bool = True

    apify_enabled: bool = False
    apify_token: SecretStr | None = None
    apify_actor_id: str | None = None
    apify_poll_interval_seconds: int = 5

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return self.database_url

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def apify_ready(self) -> bool:
        return bool(self.apify_enabled and self.apify_token and self.apify_actor_id)


@lru_cache
def get_settings() -> Settings:
    return Settings()

