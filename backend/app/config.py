import logging
import secrets

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("skillbridge")

_INSECURE_DEFAULT_KEY = "change-me-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./skillbridge.db"
    # Leave empty (or the old placeholder) and a random key is generated at
    # startup. Set SECRET_KEY in production so logins survive restarts.
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day

    # Comma-separated extra allowed browser origins, e.g.
    # CORS_ORIGINS=https://skillbridge-mvp-zdwk.vercel.app,https://example.com
    cors_origins: str = ""

    # AI engine modes
    ai_mode: str = "mock"  # "mock" | "llm"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    @field_validator("database_url")
    @classmethod
    def _normalise_database_url(cls, value: str) -> str:
        value = (value or "").strip()
        # Some hosts (Heroku-style, Neon, Railway) hand out postgres://, which
        # SQLAlchemy 2.x no longer accepts. It wants postgresql://.
        if value.startswith("postgres://"):
            value = "postgresql://" + value[len("postgres://"):]
        return value

    @model_validator(mode="after")
    def _ensure_secret_key(self):
        if not self.secret_key or self.secret_key == _INSECURE_DEFAULT_KEY:
            # Never sign tokens with a publicly known key.
            self.secret_key = secrets.token_urlsafe(48)
            logger.warning(
                "SECRET_KEY is not set (or is the old placeholder). Using a random "
                "key for this process: everyone will be logged out whenever the "
                "server restarts. Set a SECRET_KEY environment variable to fix this."
            )
        return self


settings = Settings()
