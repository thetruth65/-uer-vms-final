from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODEL_PATH: str = "./app/models"
    STORAGE_PATH: str = "./app/storage"
    # CHANGED: Threshold for Cosine Distance (0.4 is standard for Facenet512)
    FACE_MATCH_THRESHOLD: float = 0.4
    NAME_MATCH_THRESHOLD: float = 0.75
    DATABASE_URL: str
    
    class Config:
        env_file = ["../.env", ".env"]
        extra = "ignore"

settings = Settings()