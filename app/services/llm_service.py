from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime
from app.models.llm import LLMConfig

class LLMService:
    """Service for managing LLM configuration CRUD operations"""
    
    @staticmethod
    async def create_llm_config(
        model_name: str,
        organization: str,
        description: str = "",
        **kwargs
    ) -> Optional[LLMConfig]:
        """Create a new LLM configuration. Ensures no duplicate model_name + organization combination."""
        
        # Check for existing config with same model_name and organization
        existing = await LLMConfig.find_one({
            "model_name": model_name,
            "organization": organization
        })
        if existing:
            return None

        llm_config = LLMConfig(
            model_name=model_name,
            organization=organization,
            description=description,
            **kwargs
        )

        try:
            return await llm_config.insert()
        except Exception:
            return None
    
    @staticmethod
    async def get_llm_config_by_id(config_id: str) -> Optional[LLMConfig]:
        """Get a specific LLM configuration by ID"""
        try:
            return await LLMConfig.get(PydanticObjectId(config_id))
        except Exception:
            return None
    
    @staticmethod
    async def get_llm_configs(
        organization: Optional[str] = None,
        active_only: bool = True
    ) -> List[LLMConfig]:
        """Get all LLM configurations with optional filtering"""
        query = {}
        if organization:
            query["organization"] = organization
        if active_only:
            query["is_active"] = True
            
        return await LLMConfig.find(query).sort("-created_at").to_list()
    
    @staticmethod
    async def update_llm_config(
        config_id: str,
        **update_data
    ) -> Optional[LLMConfig]:
        """Update an LLM configuration"""
        llm_config = await LLMService.get_llm_config_by_id(config_id)
        if not llm_config:
            return None
            
        # Add updated timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            await llm_config.update({"$set": update_data})
            return await llm_config.save()
        except Exception:
            return None
    
    @staticmethod
    async def delete_llm_config(config_id: str) -> bool:
        """Delete an LLM configuration"""
        llm_config = await LLMService.get_llm_config_by_id(config_id)
        if not llm_config:
            return False
            
        await llm_config.delete()
        return True
