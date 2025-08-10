from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/total_keeper_db"

    # Redsys payment settings
    REDSYS_SECRET_KEY: str = "your_secret_key_here"
    REDSYS_MERCHANT_CODE: str = "your_merchant_code"
    REDSYS_TERMINAL: str = "001"
    REDSYS_SANDBOX: bool = True
    REDSYS_MERCHANT_NAME: str = "Total Keeper"
    REDSYS_MERCHANT_URL: str = "http://localhost:8000/api/v1/payments/callback"

    # Application settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # JWT Authentication settings
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS settings
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Email settings (Gmail SMTP)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_HOST: str = "smtp.gmail.com"  # Keep for backward compatibility
    SMTP_PORT: int = 587
    SMTP_TLS: bool = True
    SMTP_USERNAME: Optional[str] = None
    SMTP_USER: Optional[str] = None  # Keep for backward compatibility
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "Total Keepers"
    EMAIL_FROM: str = "noreply@totalkeepers.com"  # Display address
    NOREPLY_EMAIL: str = "noreply@totalkeepers.com"
    
    # Google Gmail API settings (optional)
    GOOGLE_CREDENTIALS_FILE: str = "keys/total-keepers-6492ff87b584.json"
    GOOGLE_GMAIL_CLIENT_ID: str = ""
    ADMIN_EMAIL: str = "admin@totalkeepers.com"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
