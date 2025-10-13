from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.llm import MediaType, RoleType, ModelFeatures, ModelParameters

class LLMConfigCreate(BaseModel):
    """Schema for creating a new LLM configuration"""
    model_name: str = Field(..., description="Name of the model")
    organization: str = Field(..., description="Organization that provides the model")
    description: str = Field(default="", description="Description of the model's capabilities")
    features: ModelFeatures
    parameters: Optional[ModelParameters] = None
    roles_allowed: Optional[List[RoleType]] = None
    pricing: Optional[Dict[str, float]] = None
    is_active: Optional[bool] = True

class LLMConfigUpdate(BaseModel):
    """Schema for updating an LLM configuration"""
    model_name: Optional[str] = None
    organization: Optional[str] = None
    description: Optional[str] = None
    features: Optional[ModelFeatures] = None
    parameters: Optional[ModelParameters] = None
    roles_allowed: Optional[List[RoleType]] = None
    pricing: Optional[Dict[str, float]] = None
    is_active: Optional[bool] = None

class LLMConfigResponse(BaseModel):
    """Schema for LLM configuration response"""
    id: str = Field(..., alias="_id")
    model_name: str
    organization: str
    description: str
    features: ModelFeatures
    parameters: ModelParameters
    roles_allowed: List[RoleType]
    pricing: Dict[str, float]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class LLMConfigList(BaseModel):
    """Schema for list of LLM configurations"""
    llms: List[LLMConfigResponse]
    total: int
