from typing import Optional
from app.services.project_service import ProjectService
from app.services.collection_service import CollectionService
from app.services.prompt_service import PromptService
from app.services.folder_service import FolderService

# Export all services
__all__ = [
    'ProjectService',
    'CollectionService', 
    'PromptService',
    'FolderService',
    'DataService'
]


class UserDataManager:
    """
    Unified service class that combines all CRUD operations.
    Provides convenience methods for common cross-service operations.
    """
    def __init__(self, uid_owner: str):
        self.uid_owner = uid_owner
        # Reference to individual services
        self.project_service = ProjectService
        self.collection_service = CollectionService
        self.prompt_service = PromptService
        self.folder_service = FolderService
    
    async def get_user_projects(self):
        """Get all projects for the user"""
        return await self.project_service.get_user_projects(self.uid_owner)
    
    async def get_project_collections(self, project_id: str):
        """Get all collections in a project"""
        return await self.collection_service.get_project_collections(project_id)
    
    async def get_collection_prompts(self, collection_id: str):
        """Get all prompts in a collection"""
        return await self.prompt_service.get_collection_prompts(collection_id)
    
    async def get_prompt_history(self, prompt_id: str):
        """Get version history for a prompt"""
        return await self.prompt_service.get_prompt_history(prompt_id)

    async def delete_project_and_contents(self, project_id: str) -> bool:
        """Delete a project and all its collections and prompts"""
        # First, get all prompts in the project
        await self.prompt_service.delete_prompts_by_project(project_id)
        
        # Second, get all collections in the project
        await self.collection_service.delete_collections_by_project(project_id)
        
        # Finally, delete the project itself
        await self.project_service.delete_project(project_id)

        return True

    async def delete_collection_and_contents(self, collection_id: str) -> bool:
        """Delete a collection and all its prompts"""
        # First, delete all prompts in the collection
        await self.prompt_service.delete_prompts_by_collection(collection_id)
        
        # Then delete the collection itself
        await self.collection_service.delete_collection(collection_id)
        
        return True
    
    async def delete_folder_and_contents(self, folder_id: str) -> list[str]:
        """Delete a folder and all its subfolders and prompts, returning all deleted folder IDs"""
        deleted_folder_ids = await self.folder_service.delete_folder_and_get_ids(folder_id)

        for folder_id in deleted_folder_ids:
            await self.prompt_service.delete_prompts_by_folder_id(folder_id)
