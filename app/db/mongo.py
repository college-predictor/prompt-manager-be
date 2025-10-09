from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection and initialize Beanie."""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.database = mongodb.client[settings.DATABASE_NAME]
    
    # Initialize Beanie with all document models
    await init_beanie(database=mongodb.database)
    
async def close_mongo_connection():
    """Close database connection."""
    if mongodb.client:
        mongodb.client.close()

def get_database():
    """Get database instance."""
    return mongodb.database
