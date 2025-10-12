from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from beanie import Document

class MediaType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"

class RoleType(str, Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    TOOL = "tool"

class ModelFeatures(BaseModel):
    """Core features and limitations of the LLM"""
    supports_tools: bool = Field(default=False, description="Whether tools can be used")
    supports_vision: bool = Field(default=False, description="Whether the model can process images")
    supports_streaming: bool = Field(default=True, description="Whether streaming is supported")
    supports_structured_output: bool = Field(default=False, description="Whether structured outputs are supported")
    supported_media: List[MediaType] = Field(
        default=[MediaType.TEXT],
        description="Types of media the model can process"
    )
    
class ModelParameters(BaseModel):
    """Model parameter controls and limitations"""
    # Temperature settings
    temperature_allowed: bool = Field(default=True, description="Whether temperature can be modified")
    temperature_range: Dict[str, float] = Field(
        default={"min": 0.0, "max": 2.0, "default": 0.7},
        description="Temperature range and default when allowed"
    )
    
    # Top P settings
    top_p_allowed: bool = Field(default=True, description="Whether top_p can be modified")
    top_p_range: Dict[str, float] = Field(
        default={"min": 0.0, "max": 1.0, "default": 1.0},
        description="Top P range and default when allowed"
    )
    
    # Token control
    max_tokens_allowed: bool = Field(default=True, description="Whether max tokens can be modified")
    max_tokens_range: Dict[str, int] = Field(
        default={"min": 1, "max": 4096, "default": 2048},
        description="Maximum tokens range and default when allowed"
    )
    
    # Penalty controls
    frequency_penalty_allowed: bool = Field(default=True, description="Whether frequency penalty can be modified")
    frequency_penalty_range: Dict[str, float] = Field(
        default={"min": -2.0, "max": 2.0, "default": 0.0},
        description="Frequency penalty range and default when allowed"
    )
    
    presence_penalty_allowed: bool = Field(default=True, description="Whether presence penalty can be modified")
    presence_penalty_range: Dict[str, float] = Field(
        default={"min": -2.0, "max": 2.0, "default": 0.0},
        description="Presence penalty range and default when allowed"
    )
    
    supports_functions: bool = Field(default=False, description="Function calling support")

class LLMConfig(Document):
    """Complete configuration for an LLM"""
    model_name: str = Field(..., description="Name of the model")
    organization: str = Field(..., description="Organization that provides the model")
    description: str = Field(default="", description="Description of the model's capabilities")
    
    # Core configurations
    features: ModelFeatures
    parameters: ModelParameters = Field(default_factory=ModelParameters)
    
    # Role configuration
    roles_allowed: List[RoleType] = Field(
        default=[RoleType.USER, RoleType.SYSTEM, RoleType.ASSISTANT],
        description="Allowed roles in conversations"
    )
    
    # API configuration
    pricing: Dict[str, float] = Field(
        default={"input": 0.0, "output": 0.0},
        description="Price per 1000 tokens"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True, description="Whether this model is active or deprecated")

    class Settings:
        name = "llm_configs"
        indexes = [
            [("model_name", 1), ("organization", 1), {"unique": True}],
            "organization",
            "is_active"
        ]