from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./skillbridge.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day

    # AI engine modes
    ai_mode: str = "mock"  # "mock" | "llm"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"


settings = Settings()
