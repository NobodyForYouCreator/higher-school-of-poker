from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Higher School of Poker"
    api_prefix: str = "/api"

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/poker"

    def cors_list(self) -> list[str]:
        if not self.cors_origins.strip():
            return []
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


settings = Settings()