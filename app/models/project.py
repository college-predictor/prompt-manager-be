from beanie import Document
from pydantic import Field
from datetime import datetime

class Project(Document):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    uid_owner: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "projects"
        indexes = [
            {"fields": ["uid_owner"]},
            {"fields": ["created_at"]},
            {"fields": ["name", "uid_owner"], "unique": True},
        ]
