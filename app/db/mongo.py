from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models.project import Project
from app.models.collection import Collection
from app.models.folder import Folder
from app.models.prompt import Prompt, PromptHistory

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection and initialize Beanie."""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.database = mongodb.client[settings.DATABASE_NAME]
    
    # Initialize Beanie with all document models
    await init_beanie(
        database=mongodb.database,
        document_models=[
            Project,
            Collection,
            Folder,
            Prompt,
            PromptHistory
        ]
    )

async def close_mongo_connection():
    """Close database connection."""
    if mongodb.client:
        mongodb.client.close()

def get_database():
    """Get database instance."""
    return mongodb.database
