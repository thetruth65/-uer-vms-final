# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import validator

class Settings(BaseSettings):
    # State Configuration
    STATE_ID: str = "STATE_A"
    STATE_NAME: str = "Maharashtra"
    
    # Database
    DATABASE_URL: str
    BLOCKCHAIN_URL: str = "" # Optional default to prevent crash
    
    # Services
    AI_SERVICE_URL: str
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
    CORS_ORIGINS: list = ["*"] # Allow all for Render
    
    # Config to read .env
    model_config = SettingsConfigDict(
        env_file=["../.env", ".env"],
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # --- NEW VALIDATOR TO FIX RENDER URLS ---
    @validator("AI_SERVICE_URL", "BLOCKCHAIN_SERVICE_URL", "PEER_BACKEND_URL", pre=True)
    def fix_url_scheme(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith("http"):
            # On Render Internal Network, services run on port 10000 by default, 
            # but usually port 80/443 mapping handles it. 
            # We assume https for external or http for internal.
            # Safe bet for internal render links is http://{host}
            return f"http://{v}"
        return v

settings = Settings()