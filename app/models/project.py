from beanie import Document, Link
from pydantic import Field
from datetime import datetime
from app.models.llm import LLMConfig
from typing import Optional

class Project(Document):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    uid_owner: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    llms: dict = Field(default={})  # Mapping of role to LLMConfig ID

    class Settings:
        name = "projects"
        indexes = [
            "uid_owner",
            "created_at",
            ("name", "uid_owner") 
        ]
