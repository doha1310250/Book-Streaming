# config.py
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"

class Settings(BaseSettings):
    # Database
    DATABASE_HOST: str = "127.0.0.1"
    DATABASE_PORT: int = 3306
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = "toor"
    DATABASE_NAME: str = "book-streaming"
    
    # App
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File upload
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    
    class Config:
        env_file = ".env"

    @property
    def images_dir(self) -> Path:
        return IMAGES_DIR

settings = Settings()

# Create images directory if it doesn't exist
IMAGES_DIR.mkdir(exist_ok=True)