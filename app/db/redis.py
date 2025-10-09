from redis.asyncio import Redis
from app.config import settings

# Create Redis client
redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
