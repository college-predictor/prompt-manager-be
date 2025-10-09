from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime


class Collection(Document):
    """Document for collections within projects"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    project_id: str = Field(..., min_length=1)  # Reference to Project._id
    uid_owner: str = Field(..., min_length=1)  # Firebase UID (denormalized for queries)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    prompts: List[str] = Field(default_factory=list)  # List of Prompt IDs

    class Settings:
        name = "collections"
        indexes = [
            "uid_owner",
            "project_id",
            "created_at",
        ]
