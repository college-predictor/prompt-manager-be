from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime


class Folder(Document):
    """Document for folders within collections"""
    name: str = Field(..., min_length=1, max_length=100)
    
    # Hierarchy references
    collection_id: str = Field(..., min_length=1)  # Reference to Collection._id
    project_id: str = Field(..., min_length=1)  # Reference to Project._id
    parent_folder_id: Optional[str] = None  # Reference to parent Folder._id (None if at root)
    uid_owner: str = Field(..., min_length=1)  # Firebase UID
    
    # Content references
    subfolders: List[str] = Field(default_factory=list)  # List of Folder._id
    prompts: List[str] = Field(default_factory=list)  # List of Prompt._id
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "folders"
        indexes = [
            "uid_owner",
            "collection_id",
            "project_id",
            "parent_folder_id",
            "created_at",
        ]