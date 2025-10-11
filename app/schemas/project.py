from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    uid_owner: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: str = Field(None, alias="_id")
    name: str
    description: str


class ProjectList(BaseModel):
    """Schema for list of projects"""
    projects: List[ProjectResponse]
    total: int