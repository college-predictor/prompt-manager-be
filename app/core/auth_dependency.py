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
    print("\n[Auth] ====== Token Validation Started ======")
    print(f"[Auth] Token length: {len(token) if token else 0}")
    
    if not token:
        print("[Auth] ERROR: Empty token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Try to get user data from Redis first
    cache_key = f"{REDIS_USER_PREFIX}{token}"
    print(f"[Auth] Checking Redis cache with key: {cache_key}")
    cached_user = await redis.get(cache_key)
    print(f"[Auth] Redis cache hit: {bool(cached_user)}")
    
    if cached_user:
        print("[Auth] Using cached user data from Redis")
        return json.loads(cached_user)
    
    print("[Auth] No cache found, validating with Firebase")
    # If not in cache, validate with Firebase
    try:
        auth_backend = GoogleAuthBackend.get_instance()
        print("[Auth] Firebase instance initialized")
        user_data = auth_backend.verify_token(token)
        print(f"[Auth] Firebase validation successful. User: {user_data.get('email')}")
        
        # Cache the user data in Redis
        await redis.set(
            cache_key,
            json.dumps(user_data),
            ex=REDIS_USER_EXPIRY
        )
        print("[Auth] User data cached in Redis")
        
        return user_data
        
    except AuthFailedException as e:
        print(f"[Auth] ERROR: Firebase validation failed - {str(e)}")
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