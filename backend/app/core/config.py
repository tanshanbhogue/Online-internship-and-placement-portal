import secrets
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings. Environment variables (or backend/.env) override the defaults below.

    Tests: change a value with ``monkeypatch.setattr(settings, "NAME", value)`` (the object is
    mutable), or set env vars and call ``get_settings.cache_clear()`` to rebuild it.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./portal.db"
    # No committed default (SEC-24). Empty in development => a random per-process key is generated.
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    LOGIN_MAX_FAILURES: int = 5
    LOGIN_WINDOW_MINUTES: int = 15
    RESUME_STORAGE_DIR: str = "./storage/resumes"
    RESUME_MAX_BYTES: int = 5 * 1024 * 1024
    PRACTICE_DEFAULT_QUESTION_COUNT: int = 10
    CORS_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:5173"]
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, value):
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    @field_validator("COOKIE_SAMESITE", mode="before")
    @classmethod
    def _lower_samesite(cls, value):
        return value.lower() if isinstance(value, str) else value

    @model_validator(mode="after")
    def _require_secret_outside_development(self):
        if not self.SECRET_KEY:
            if self.APP_ENV.lower() != "development":
                raise ValueError("SECRET_KEY must be set when APP_ENV is not 'development'")
            self.SECRET_KEY = secrets.token_urlsafe(48)
        return self

    def __repr__(self) -> str:  # never print secrets
        return f"Settings(APP_ENV={self.APP_ENV!r})"

    __str__ = __repr__


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
