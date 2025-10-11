from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime


class Prompt(Document):
    """Document for storing prompts within collections"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    prompt_text: str = Field(..., min_length=1)

    # Optional LLM configuration for the prompt
    llm_configurations: Optional[dict] = Field(default=None)
    
    # Hierarchy references
    project_id: str = Field(..., min_length=1)  # Reference to Project._id
    collection_id: str = Field(..., min_length=1)  # Reference to Collection._id
    folder_id: Optional[str] = None  # Reference to Folder._id (None if at collection root)
    uid_owner: str = Field(..., min_length=1)  # Firebase UID (denormalized for fast queries)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # List of PromptHistory._id
    change_history: List[str] = Field(default_factory=list)
    
    class Settings:
        name = "prompts"
        indexes = [
            "uid_owner",
            "project_id", 
            "collection_id",
            "folder_id",
            "tags",
            "created_at",
        ]

class PromptHistory(Document):
    """Separate document for tracking prompt changes"""
    prompt_id: str = Field(..., min_length=1)  # Reference to Prompt._id
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    prompt_text: str = Field(..., min_length=1)
    change_message: Optional[str] = Field(default=None, max_length=200)
    llm_configurations: Optional[dict] = Field(default=None)
    
    class Settings:
        name = "prompt_history"
        indexes = [
            "prompt_id",
            "timestamp",
            ("prompt_id", "uid_owner"),  # Compound index for faster search
        ]