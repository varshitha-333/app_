"""
Application configuration — values are read from environment variables.
Never hard-code credentials here.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    ENV: str = os.getenv("FLASK_ENV", "production")
    DEBUG: bool = ENV == "development"
    SECRET_KEY: str = os.getenv("SECRET_KEY", os.urandom(32).hex())
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_UPLOAD_MB", 100)) * 1024 * 1024  # bytes

    # CORS
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # Google Drive — choose ONE auth strategy via env vars
    # Strategy A (Service Account JSON file path)
    GOOGLE_SERVICE_ACCOUNT_FILE: str | None = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    # Strategy B (Service Account JSON contents as a string — useful for Docker/cloud)
    GOOGLE_SERVICE_ACCOUNT_JSON: str | None = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    GOOGLE_DRIVE_SCOPES: list[str] = [
        "https://www.googleapis.com/auth/drive",
    ]

    # Upload temp directory
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "/tmp/gdrive_uploads")


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
