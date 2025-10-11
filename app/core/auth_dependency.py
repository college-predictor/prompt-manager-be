import json
from typing import Optional
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.firebase_auth import GoogleAuthBackend, AuthFailedException
from app.db.redis import redis

security = HTTPBearer()

REDIS_USER_PREFIX = "user:"
REDIS_USER_EXPIRY = 3600  # 1 hour cache

async def validate_token(token: str) -> dict:
    """
    Validate Firebase token and get user data with Redis caching
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Try to get user data from Redis first
    cache_key = f"{REDIS_USER_PREFIX}{token}"
    cached_user = await redis.get(cache_key)
    
    if cached_user:
        return json.loads(cached_user)
    
    # If not in cache, validate with Firebase
    try:
        auth_backend = GoogleAuthBackend.get_instance()
        user_data = auth_backend.verify_token(token)
        
        # Cache the user data in Redis
        await redis.set(
            cache_key,
            json.dumps(user_data),
            ex=REDIS_USER_EXPIRY
        )
        
        return user_data
        
    except AuthFailedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )