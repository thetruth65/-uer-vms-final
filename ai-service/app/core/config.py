from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODEL_PATH: str = "./app/models"
    STORAGE_PATH: str = "./app/storage"
    # CHANGED: Threshold for Cosine Distance (0.4 is standard for Facenet512)
    FACE_MATCH_THRESHOLD: float = 0.4
    NAME_MATCH_THRESHOLD: float = 0.75
    
    class Config:
        env_file = ".env"

settings = Settings()