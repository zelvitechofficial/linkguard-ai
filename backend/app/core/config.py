from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "URL Threat Detection API"
    DEBUG: bool = False
    DATABASE_URL: str = ""
    CLERK_JWT_PUBLIC_KEY: str = ""
    CLERK_JWKS_URL: str = ""
    CLERK_API_KEY: str = ""
    CLERK_SECRET_KEY: str = ""
    CLERK_WEBHOOK_SECRET: str = ""
    ADMIN_EMAIL: str = ""
    DAILY_SCAN_LIMIT: int = 10
    DAILY_CHATBOT_LIMIT: int = 10
    GEMINI_API_KEY: str = ""
    # Use a string that we split manually to be safe with all environments
    ALLOWED_ORIGINS: str = "*"


settings = Settings()
