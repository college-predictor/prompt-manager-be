from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from app.models.llm import MediaType, RoleType


class ModelFeaturesSchema(BaseModel):
    """Schema for model features"""
    supports_tools: bool = Field(default=False)
    supports_vision: bool = Field(default=False)
    supports_streaming: bool = Field(default=True)
    supports_structured_output: bool = Field(default=False)
    supported_media: List[MediaType] = Field(default=[MediaType.TEXT])


class ModelParametersSchema(BaseModel):
    """Schema for model parameters"""
    temperature_allowed: bool = Field(default=True)
    temperature_range: Dict[str, float] = Field(
        default={"min": 0.0, "max": 2.0, "default": 0.7}
    )
    top_p_allowed: bool = Field(default=True)
    top_p_range: Dict[str, float] = Field(
        default={"min": 0.0, "max": 1.0, "default": 1.0}
    )
    max_tokens_allowed: bool = Field(default=True)
    max_tokens_range: Dict[str, int] = Field(
        default={"min": 1, "max": 4096, "default": 2048}
    )
    frequency_penalty_allowed: bool = Field(default=True)
    frequency_penalty_range: Dict[str, float] = Field(
        default={"min": -2.0, "max": 2.0, "default": 0.0}
    )
    presence_penalty_allowed: bool = Field(default=True)
    presence_penalty_range: Dict[str, float] = Field(
        default={"min": -2.0, "max": 2.0, "default": 0.0}
    )
    supports_functions: bool = Field(default=False)


class LLMConfigCreate(BaseModel):
    """Schema for creating a new LLM configuration"""
    model_name: str = Field(..., description="Name of the model")
    organization: str = Field(..., description="Organization that provides the model")
    description: str = Field(default="", description="Description of the model's capabilities")
    version: str = Field(default="1.0.0", description="Model version")
    features: Optional[ModelFeaturesSchema] = None
    parameters: Optional[ModelParametersSchema] = None
    roles_allowed: List[RoleType] = Field(
        default=[RoleType.USER, RoleType.SYSTEM, RoleType.ASSISTANT]
    )
    pricing: Dict[str, float] = Field(
        default={"input": 0.0, "output": 0.0}
    )


class LLMConfigUpdate(BaseModel):
    """Schema for updating an LLM configuration"""
    description: Optional[str] = None
    version: Optional[str] = None
    features: Optional[ModelFeaturesSchema] = None
    parameters: Optional[ModelParametersSchema] = None
    roles_allowed: Optional[List[RoleType]] = None
    pricing: Optional[Dict[str, float]] = None
    is_active: Optional[bool] = None


class LLMConfigResponse(BaseModel):
    """Schema for LLM configuration response"""
    id: str = Field(None, alias="_id")
    model_name: str
    organization: str
    description: str
    version: str
    features: ModelFeaturesSchema
    parameters: ModelParametersSchema
    roles_allowed: List[RoleType]
    pricing: Dict[str, float]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        populate_by_name = True
