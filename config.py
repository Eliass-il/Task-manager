from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "task-manager"
    database_url: str
    session_cookie_name: str = "taskmanager_session"
    session_ttl_seconds: int = 60*60*24*7
    session_cookie_secure: bool = False

    trusted_origins: tuple[str, ...] = (
        "http://127.0.0.1:8000",
        "http://localhost:8000",   
    )

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
