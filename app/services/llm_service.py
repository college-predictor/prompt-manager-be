from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime

from app.models.llm import LLMConfig, ModelFeatures, ModelParameters


class LLMService:
    """Service for managing LLM configurations"""
    
    @staticmethod
    async def create_llm_config(
        model_name: str,
        organization: str,
        description: str = "",
        features: Optional[ModelFeatures] = None,
        parameters: Optional[ModelParameters] = None,
        roles_allowed: Optional[List[str]] = None,
        pricing: Optional[dict] = None,
    ) -> Optional[LLMConfig]:
        """Create a new LLM configuration"""
        try:
            # Check if model already exists for the organization
            existing_model = await LLMConfig.find_one(
                LLMConfig.model_name == model_name,
                LLMConfig.organization == organization
            )
            if existing_model:
                return None

            config = LLMConfig(
                model_name=model_name,
                organization=organization,
                description=description,
                features=features or ModelFeatures(),
                parameters=parameters or ModelParameters(),
                roles_allowed=roles_allowed or [],
                pricing=pricing or {"input": 0.0, "output": 0.0},
            )
            
            return await config.insert()
        except Exception:
            return None

    @staticmethod
    async def get_llm_config_by_id(config_id: str) -> Optional[LLMConfig]:
        """Get a specific LLM configuration by ID"""
        try:
            return await LLMConfig.find_one(
                LLMConfig.id == PydanticObjectId(config_id)
            )
        except Exception:
            return None

    @staticmethod
    async def get_llm_config(model_name: str, organization: str) -> Optional[LLMConfig]:
        """Get a specific LLM configuration by model name and organization"""
        try:
            return await LLMConfig.find_one(
                LLMConfig.model_name == model_name,
                LLMConfig.organization == organization
            )
        except Exception:
            return None

    @staticmethod
    async def get_organization_llms(organization: str, include_inactive: bool = False) -> List[LLMConfig]:
        """Get all LLM configurations for an organization"""
        query = [LLMConfig.organization == organization]
        if not include_inactive:
            query.append(LLMConfig.is_active == True)
            
        return await LLMConfig.find(*query).sort("-created_at").to_list()

    @staticmethod
    async def get_all_active_llms() -> List[LLMConfig]:
        """Get all active LLM configurations"""
        return await LLMConfig.find(
            LLMConfig.is_active == True
        ).sort("-created_at").to_list()

    @staticmethod
    async def update_llm_config(
        config_id: str,
        description: Optional[str] = None,
        features: Optional[ModelFeatures] = None,
        parameters: Optional[ModelParameters] = None,
        roles_allowed: Optional[List[str]] = None,
        pricing: Optional[dict] = None,
        is_active: Optional[bool] = None
    ) -> Optional[LLMConfig]:
        """Update an LLM configuration"""
        config = await LLMService.get_llm_config_by_id(config_id)
        if not config:
            return None

        update_data = {"updated_at": datetime.utcnow()}
        
        if description is not None:
            update_data["description"] = description
        if features is not None:
            update_data["features"] = features
        if parameters is not None:
            update_data["parameters"] = parameters
        if roles_allowed is not None:
            update_data["roles_allowed"] = roles_allowed
        if pricing is not None:
            update_data["pricing"] = pricing
        if is_active is not None:
            update_data["is_active"] = is_active

        await config.update({"$set": update_data})
        return await config.save()

    @staticmethod
    async def delete_llm_config(config_id: str) -> bool:
        """Delete an LLM configuration"""
        config = await LLMService.get_llm_config_by_id(config_id)
        if not config:
            return False

        await config.delete()
        return True

    @staticmethod
    async def deactivate_llm_config(config_id: str) -> bool:
        """Deactivate an LLM configuration instead of deleting it"""
        config = await LLMService.get_llm_config_by_id(config_id)
        if not config:
            return False

        await config.update({"$set": {
            "is_active": False,
            "updated_at": datetime.utcnow()
        }})
        return True
