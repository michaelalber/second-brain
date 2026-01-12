from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "sqlite+aiosqlite:///./basb.db"
    DEBUG: bool = True
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


settings = Settings()
