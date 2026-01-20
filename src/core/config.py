"""
Application configuration loaded from environment variables.

Uses Pydantic Settings for type-safe configuration management.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # Application
    APP_NAME: str = "Polymarket Trading Bot"
    DEBUG: bool = False

    # Server
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    # CLOB API Configuration
    POLYGON_WALLET_PRIVATE_KEY: str = ""
    CLOB_API_URL: str = "https://clob.polymarket.com"

    # L2 API Credentials (optional - auto-generated from private key)
    CLOB_API_KEY: str = ""
    CLOB_API_SECRET: str = ""
    CLOB_API_PASSPHRASE: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Settings: Application configuration instance.
    """
    return Settings()
