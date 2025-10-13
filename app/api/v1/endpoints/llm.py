from fastapi import APIRouter, HTTPException, status
from typing import Optional

from app.schemas.llm import (
    LLMConfigCreate,
    LLMConfigUpdate,
    LLMConfigResponse,
    LLMConfigList
)
from app.services.llm_service import LLMService

router = APIRouter()

@router.post("/llm-configs", response_model=LLMConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_llm_config(config: LLMConfigCreate):
    """Create a new LLM configuration"""
    llm_config = await LLMService.create_llm_config(
        model_name=config.model_name,
        organization=config.organization,
        description=config.description,
        features=config.features,
        parameters=config.parameters or {},
        roles_allowed=config.roles_allowed,
        pricing=config.pricing,
        is_active=config.is_active
    )
    
    if not llm_config:
        raise HTTPException(
            status_code=400,
            detail="LLM configuration with this model name and organization already exists"
        )
    
    return {**llm_config.dict(), "_id": str(llm_config.id)}

@router.get("/llm-configs", response_model=LLMConfigList)
async def list_llm_configs(organization: Optional[str] = None, include_inactive: bool = False):
    """List all LLM configurations with optional filtering"""
    configs = await LLMService.get_llm_configs(
        organization=organization,
        active_only=not include_inactive
    )
    
    # Convert ObjectId to string for each config
    configs = [{**config.dict(), "_id": str(config.id)} for config in configs]
    return {"llms": configs, "total": len(configs)}

@router.get("/llm-configs/{config_id}", response_model=LLMConfigResponse)
async def get_llm_config(config_id: str):
    """Get a specific LLM configuration"""
    config = await LLMService.get_llm_config_by_id(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="LLM configuration not found")
    
    return {**config.dict(), "_id": str(config.id)}

@router.put("/llm-configs/{config_id}", response_model=LLMConfigResponse)
async def update_llm_config(config_id: str, config_update: LLMConfigUpdate):
    """Update an LLM configuration"""
    update_data = config_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update data provided")
    
    updated_config = await LLMService.update_llm_config(config_id, **update_data)
    if not updated_config:
        raise HTTPException(status_code=404, detail="LLM configuration not found")
    
    return {**updated_config.dict(), "_id": str(updated_config.id)}

@router.delete("/llm-configs/{config_id}", status_code=status.HTTP_200_OK)
async def delete_llm_config(config_id: str):
    """Delete an LLM configuration"""
    deleted = await LLMService.delete_llm_config(config_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="LLM configuration not found")
    
    return {
        "message": "LLM configuration deleted successfully",
        "config_id": config_id
    }
