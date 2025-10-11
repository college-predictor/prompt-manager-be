from fastapi import APIRouter
from app.api.v1.endpoints import (
    prompts,
)

api_router = APIRouter()

api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])


