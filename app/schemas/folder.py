from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .base import BaseSchema


class FolderCreate(BaseModel):
    """Schema for creating a new folder"""
    name: str = Field(..., min_length=1, max_length=100)
    collection_id: str = Field(..., min_length=1)
    project_id: str = Field(..., min_length=1)
    parent_folder_id: Optional[str] = None


class FolderUpdate(BaseModel):
    """Schema for updating a folder"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_folder_id: Optional[str] = None


class FolderResponse(BaseSchema):
    """Schema for folder response"""
    name: str
    collection_id: str
    project_id: str
    parent_folder_id: Optional[str]
    subfolders: List[str] = Field(default_factory=list)
    prompts: List[str] = Field(default_factory=list)
    updated_at: Optional[datetime] = None


class FolderList(BaseModel):
    """Schema for list of folders"""
    folders: List[FolderResponse]
    total: int


class FolderTree(FolderResponse):
    """Schema for nested folder structure"""
    subfolders: List["FolderTree"] = Field(default_factory=list)