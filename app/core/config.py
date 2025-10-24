from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv(".env")  # load environment variables from .env file

class Settings(BaseModel):
    # Database
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "college-predictor")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
    # Application
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # File Upload
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads/")

    # Firebase
    SA_KEY_FILE: str = os.getenv("FIREBASE_SA_FILE", "secrets/serviceAccountKey.json")

settings = Settings()
