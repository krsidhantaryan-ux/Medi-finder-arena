"""
Configuration management using Pydantic Settings.
Reads environment variables with type validation and sensible defaults.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 5000

    # Security
    SECRET_KEY: str = "medfinder-enterprise-secret-key-2026"
    JWT_SECRET_KEY: str = "jwt-secret-token-key-medifinder-2026"
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 120
    JWT_REFRESH_TOKEN_EXPIRES_DAYS: int = 30

    # MongoDB settings
    MONGODB_URI: str = "mongodb://localhost:27017/medifinder"
    MONGODB_DB_NAME: str = "medifinder"
    MONGODB_MAX_POOL_SIZE: int = 50
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = 2000

    # System Admin
    ADMIN_USER: str = "admin"
    ADMIN_PASS: str = "Admin@MediFinder2026!"

    # Uploads
    UPLOAD_FOLDER: str = str(Path(__file__).resolve().parent / "static" / "uploads")
    MAX_CONTENT_LENGTH: int = 8 * 1024 * 1024  # 8 MB
    ALLOWED_IMAGE_EXTENSIONS: set = {"png", "jpg", "jpeg", "webp", "gif"}
    ALLOWED_DOC_EXTENSIONS: set = {"png", "jpg", "jpeg", "webp", "pdf"}

    # Geolocation & Business Defaults (Patna, Bihar)
    DEFAULT_LAT: float = 25.6110
    DEFAULT_LNG: float = 85.1430
    DEFAULT_SEARCH_RADIUS_KM: float = 15.0

    # Reservation hold window
    HOLD_WINDOW_HOURS: int = 2


settings = Settings()
