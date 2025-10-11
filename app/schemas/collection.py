from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CollectionCreate(BaseModel):
    """Schema for creating a new collection"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    project_id: str = Field(..., min_length=1)


class CollectionUpdate(BaseModel):
    """Schema for updating a collection"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CollectionResponse(BaseSchema):
    """Schema for collection response"""
    name: str
    description: str
    project_id: str


class CollectionList(BaseModel):
    """Schema for list of collections"""
    collections: List[CollectionResponse]
    total: int