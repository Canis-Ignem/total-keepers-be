from pydantic_settings import BaseSettings
from typing import Optional

import os


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/total_keeper_db"
    )

    # Redsys payment settings
    REDSYS_SECRET_KEY: str = os.getenv("REDSYS_SECRET_KEY", "your_secret_key_here")
    REDSYS_MERCHANT_CODE: str = os.getenv("REDSYS_MERCHANT_CODE", "your_merchant_code")
    REDSYS_TERMINAL: str = os.getenv("REDSYS_TERMINAL", "001")
    REDSYS_SANDBOX: bool = os.getenv("REDSYS_SANDBOX", "True").lower() in (
        "true",
        "1",
        "t",
    )
    REDSYS_MERCHANT_NAME: str = os.getenv("REDSYS_MERCHANT_NAME", "TOTAL KEEPERS")
    REDSYS_MERCHANT_URL: str = os.getenv(
        "REDSYS_MERCHANT_URL", "http://localhost:8000/api/v1/payments/redsys-callback"
    )

    # Application settings
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "your-secret-key-here-change-in-production"
    )
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "t")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # JWT Authentication settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET", "jwt_secret_key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    # CORS settings
    APP_ALLOWED_ORIGINS: str = os.getenv(
        "APP_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    )
    ALLOWED_ORIGINS: list[str] = APP_ALLOWED_ORIGINS.split(",")

    # Email settings (Gmail SMTP)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() in ("true", "1", "t")
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_FROM_EMAIL: Optional[str] = os.getenv("SMTP_FROM_EMAIL")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Total Keepers")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@totalkeepers.com")
    NOREPLY_EMAIL: str = os.getenv("NOREPLY_EMAIL", "noreply@totalkeepers.com")
    FINANCE_EMAIL: str = os.getenv("FINANCE_EMAIL", "totalkeepersbilbao@gmail.com")

    # Google Gmail API settings (optional)
    GOOGLE_CREDENTIALS_FILE: str = os.getenv(
        "GOOGLE_CREDENTIALS_FILE", "keys/total-keepers-6492ff87b584.json"
    )
    GOOGLE_GMAIL_CLIENT_ID: str = os.getenv("GOOGLE_GMAIL_CLIENT_ID", "")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@totalkeepers.com")

    # Azure Communication Services Email settings
    AZURE_COMMUNICATION_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
    AZURE_EMAIL_SENDER: Optional[str] = os.getenv("AZURE_EMAIL_SENDER")


settings = Settings()
