# config/settings.py   (or just settings.py)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # These will be read from environment variables or .env file
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "nonprofit_990"
    db_user: str
    db_password: str

    # Optional: you can add more settings later (SECRET_KEY, etc.)
    # app_name: str = "Dark Money API"

    model_config = SettingsConfigDict(
        env_file=".env",              # automatically load from .env
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",               # ignore extra env vars
    )


# Singleton / cached instance (recommended pattern)
settings = Settings()