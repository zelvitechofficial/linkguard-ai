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
    GEMINI_API_KEY: str = ""
    # Use a string that we split manually to be safe with all environments
    ALLOWED_ORIGINS: str = "*"

    def validate_setup(self):
        """Perform basic validation of the environment setup."""
        if not self.DATABASE_URL:
            logger.error("DATABASE_URL is not set!")
        if not self.CLERK_JWKS_URL:
            logger.error("CLERK_JWKS_URL is not set!")
        if not self.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. Chatbot will not function.")

    @property
    def CLERK_SECRET_KEY_ROBUST(self) -> str:
        """Returns the secret key, falling back to CLERK_API_KEY if it contains the secret value."""
        if self.CLERK_SECRET_KEY and self.CLERK_SECRET_KEY.startswith("sk_"):
            return self.CLERK_SECRET_KEY
        if self.CLERK_API_KEY and self.CLERK_API_KEY.startswith("sk_"):
            return self.CLERK_API_KEY
        return self.CLERK_SECRET_KEY or self.CLERK_API_KEY


settings = Settings()
