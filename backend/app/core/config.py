# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # State Configuration
    STATE_ID: str = "STATE_A"
    STATE_NAME: str = "Maharashtra"
    
    # Database
    DATABASE_URL: str
    BLOCKCHAIN_URL: str
    
    # Services
    AI_SERVICE_URL: str
    # [NEW] Added this field so Pydantic can read it
    BLOCKCHAIN_SERVICE_URL: str
    PEER_BACKEND_URL: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Storage
    PHOTO_STORAGE_PATH: str = "./storage/photos"
    MAX_PHOTO_SIZE_MB: int = 5
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Config to read .env and ignore extra variables
    model_config = SettingsConfigDict(
        env_file=["../.env", ".env"],
        env_file_encoding="utf-8",
        extra="ignore"  # This prevents crashes if .env has extra variables
    )

settings = Settings()