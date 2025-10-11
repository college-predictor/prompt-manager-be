from typing import List
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.auth_dependency import validate_token

class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app: ASGIApp, 
        public_paths: List[str] = None
    ):
        super().__init__(app)
        self.public_paths = public_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/api/v1/auth/login",  # Add your public endpoints here
        ]

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)

        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(' ')[1]
        
        # Validate token and get user data
        user = await validate_token(token)
        
        # Initialize state with user data
        if not hasattr(request.state, '_state'):
            request.state._state = {}
        request.state._state['user'] = user

        # Continue processing the request
        response = await call_next(request)
        return response