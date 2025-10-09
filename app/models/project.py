from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime


class Project(Document):
    """Document for user projects"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    uid_owner: str = Field(..., min_length=1)  # Firebase UID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    collections: List[str] = Field(default_factory=list)  # List of Collection IDs

    class Settings:
        name = "projects"
        indexes = [
            "uid_owner",
            "created_at",
        ]