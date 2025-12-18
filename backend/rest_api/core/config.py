from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]

JWT_SECRET = "gustokashinmuseflycone"
JWT_EXPIRES_MINUTES = 52
JWT_ALGORITHM = "HS256"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Higher School of Poker"
    api_prefix: str = "/api"
    cors_origins: str = ""
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/poker"

    def cors_list(self) -> list[str]:
        if not self.cors_origins.strip():
            return []
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


settings = Settings()
