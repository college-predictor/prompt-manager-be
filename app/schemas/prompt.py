from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .base import BaseSchema


class PromptHistoryCreate(BaseModel):
    """Schema for creating prompt history"""
    prompt_id: str = Field(..., min_length=1)
    prompt_text: str = Field(..., min_length=1)
    change_message: Optional[str] = Field(None, max_length=200)
    llm_configurations: Optional[dict] = None


class PromptHistoryResponse(BaseModel):
    """Schema for prompt history response"""
    id: Optional[str] = Field(None, alias="_id")
    prompt_id: str
    timestamp: datetime
    prompt_text: str
    change_message: Optional[str]
    llm_configurations: Optional[dict]

    class Config:
        populate_by_name = True


class PromptCreate(BaseModel):
    """Schema for creating a new prompt"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    prompt_text: str = Field(..., min_length=1)
    llm_configurations: Optional[dict] = None
    project_id: str = Field(..., min_length=1)
    collection_id: str = Field(..., min_length=1)
    folder_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class PromptUpdate(BaseModel):
    """Schema for updating a prompt"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    prompt_text: Optional[str] = Field(None, min_length=1)
    llm_configurations: Optional[dict] = None
    folder_id: Optional[str] = None
    tags: Optional[List[str]] = None
    change_message: Optional[str] = Field(None, max_length=200)


class PromptResponse(BaseSchema):
    """Schema for prompt response"""
    title: str
    description: str
    prompt_text: str
    llm_configurations: Optional[dict]
    project_id: str
    collection_id: str
    folder_id: Optional[str]
    tags: List[str]
    updated_at: Optional[datetime]
    change_history: List[str]


class PromptList(BaseModel):
    """Schema for list of prompts"""
    prompts: List[PromptResponse]
    total: int