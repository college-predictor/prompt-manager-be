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

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", None)
    
    FIREBASE_SA_FILE: str = os.getenv("FIREBASE_SA_FILE")

settings = Settings()
