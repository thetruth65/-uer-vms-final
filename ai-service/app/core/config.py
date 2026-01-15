from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODEL_PATH: str = "/app/models"
    STORAGE_PATH: str = "/app/storage"
    FACE_MATCH_THRESHOLD: float = 0.85  # Lower = more strict
    NAME_MATCH_THRESHOLD: float = 0.75
    
    class Config:
        env_file = ".env"

settings = Settings()