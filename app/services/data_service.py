from typing import Optional
from app.services.project_service import ProjectService
from app.services.collection_service import CollectionService
from app.services.prompt_service import PromptService, PromptHistory

# Export all services
__all__ = [
    'ProjectService',
    'CollectionService', 
    'PromptService',
    'DataService'
]


class UserDataManager:
    """
    Unified service class that combines all CRUD operations.
    Provides convenience methods for common cross-service operations.
    """
    
    # Reference to individual services
    projects = ProjectService
    collections = CollectionService
    prompts = PromptService
    prompts_history = PromptService  # Using PromptService for history operations as well

