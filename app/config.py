from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env file

class Settings(BaseModel):
    # Database
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "prompt_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
    # Application
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Firebase Client Configuration
    FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY")
    FIREBASE_AUTH_DOMAIN: str = os.getenv("FIREBASE_AUTH_DOMAIN")
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_STORAGE_BUCKET: str = os.getenv("FIREBASE_STORAGE_BUCKET")
    FIREBASE_MESSAGING_SENDER_ID: str = os.getenv("FIREBASE_MESSAGING_SENDER_ID")
    FIREBASE_APP_ID: str = os.getenv("FIREBASE_APP_ID")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    

    
    FIREBASE_SA_FILE: str = os.getenv("FIREBASE_SA_FILE")

settings = Settings()
