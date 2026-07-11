from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Vietnamese IT Job Insights"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/job_insights"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LOG_LEVEL: str = "INFO"
    GEMINI_API_KEY: str = ""

    # Support reading from .env in either current directory or parent directory
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
