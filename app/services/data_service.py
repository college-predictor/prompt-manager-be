from typing import List, Optional
from app.services.project_service import ProjectService
from app.services.collection_service import CollectionService
from app.services.prompt_service import PromptService
from app.services.folder_service import FolderService
from app.models.project import Project
from app.models.collection import Collection
from app.models.folder import Folder
from app.models.prompt import Prompt, PromptHistory

# Export all services
__all__ = [
    'ProjectService',
    'CollectionService', 
    'PromptService',
    'FolderService',
    'UserDataManager',
]


class UserDataManager:
    """
    Unified service class that combines all CRUD operations.
    Provides convenience methods for common cross-service operations.
    """
    
    # Project operations
    @staticmethod
    async def create_project(uid_owner: str, name: str, description: str = "") -> Project:
        """Create a new project"""
        return await ProjectService.create_project(uid_owner=uid_owner, name=name, description=description)

    @staticmethod
    async def get_user_projects(uid_owner: str) -> List[Project]:
        """Get all projects for the user"""
        return await ProjectService.get_user_projects(uid_owner)
    
    @staticmethod
    async def get_project(project_id: str, uid_owner: str) -> Optional[Project]:
        """Get a specific project if user owns it"""
        return await ProjectService.get_project_by_id(project_id, uid_owner)

    @staticmethod
    async def update_project(project_id: str, uid_owner: str, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Project]:
        """Update a project if user owns it"""
        return await ProjectService.update_project(project_id, uid_owner, name, description)

    # Collection operations
    @staticmethod
    async def create_collection(project_id: str, uid_owner: str, name: str, description: str = "") -> Optional[Collection]:
        """Create a new collection in a project"""
        return await CollectionService.create_collection(project_id, uid_owner, name, description)
    
    @staticmethod
    async def get_project_collections(project_id: str) -> List[Collection]:
        """Get all collections in a project"""
        return await CollectionService.get_project_collections(project_id)
    
    @staticmethod
    async def get_collection(collection_id: str, uid_owner: str) -> Optional[Collection]:
        """Get a specific collection if user owns it"""
        return await CollectionService.get_collection_by_id(collection_id, uid_owner)
    
    @staticmethod
    async def update_collection(collection_id: str, uid_owner: str, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Collection]:
        """Update a collection if user owns it"""
        return await CollectionService.update_collection(collection_id, uid_owner, name, description)

    # Folder operations
    @staticmethod
    async def create_folder(project_id: str, collection_id: str, uid_owner: str, name: str, parent_folder_id: Optional[str] = None) -> Optional[Folder]:
        """Create a new folder"""
        return await FolderService.create_folder(project_id, collection_id, uid_owner, name, parent_folder_id)
    
    @staticmethod
    async def get_folder(folder_id: str, uid_owner: str) -> Optional[Folder]:
        """Get a specific folder if user owns it"""
        return await FolderService.get_folder_by_id(folder_id, uid_owner)
    
    @staticmethod
    async def get_collection_root_folders(collection_id: str) -> List[Folder]:
        """Get all root folders in a collection"""
        return await FolderService.get_collection_root_folders(collection_id)
    
    @staticmethod
    async def update_folder(folder_id: str, uid_owner: str, name: Optional[str] = None) -> Optional[Folder]:
        """Update a folder if user owns it"""
        return await FolderService.update_folder(folder_id, uid_owner, name)
    
    # Prompt operations
    @staticmethod
    async def create_prompt(project_id: str, collection_id: str, uid_owner: str, title: str, prompt_text: str, description: str = "", tags: List[str] = None, folder_id: Optional[str] = None) -> Optional[Prompt]:
        """Create a new prompt"""
        return await PromptService.create_prompt(project_id, collection_id, uid_owner, title, prompt_text, description, tags, folder_id)
    
    @staticmethod
    async def get_prompt(prompt_id: str, uid_owner: str) -> Optional[Prompt]:
        """Get a specific prompt if user owns it"""
        return await PromptService.get_prompt_by_id(prompt_id, uid_owner)
    
    @staticmethod
    async def get_collection_prompts(collection_id: str) -> List[Prompt]:
        """Get all prompts in a collection"""
        return await PromptService.get_collection_prompts(collection_id)
    
    @staticmethod
    async def get_prompt_history(prompt_id: str) -> Optional[List[PromptHistory]]:
        """Get version history for a prompt"""
        return await PromptService.get_prompt_history_by_id(prompt_id)
    
    @staticmethod
    async def update_prompt(prompt_id: str, uid_owner: str, title: Optional[str] = None, description: Optional[str] = None, prompt_text: Optional[str] = None, tags: Optional[List[str]] = None, change_message: Optional[str] = None) -> Optional[Prompt]:
        """Update a prompt if user owns it"""
        return await PromptService.update_prompt(prompt_id, uid_owner, title, description, prompt_text, tags, change_message)

    # Delete operations with cascading
    @staticmethod
    async def delete_project_and_contents(project_id: str, uid_owner: str) -> bool:
        """Delete a project and all its collections and prompts"""
        # First verify project exists and user owns it
        project = await ProjectService.get_project_by_id(project_id, uid_owner)
        if not project:
            return False

        # Delete all prompts in the project
        await PromptService.delete_prompts_by_project(project_id)
        
        # Delete all collections in the project
        await CollectionService.delete_collections_by_project(project_id)
        
        # Delete the project itself
        await ProjectService.delete_project(project_id, uid_owner)
        return True

    @staticmethod
    async def delete_collection_and_contents(collection_id: str, uid_owner: str) -> bool:
        """Delete a collection and all its prompts"""
        # Verify collection exists and user owns it
        collection = await CollectionService.get_collection_by_id(collection_id, uid_owner)
        if not collection:
            return False

        # Delete all prompts in the collection
        await PromptService.delete_prompts_by_collection(collection_id)
        
        # Delete the collection itself
        await CollectionService.delete_collection(collection_id, uid_owner)
        return True
    
    @staticmethod
    async def delete_folder_and_contents(folder_id: str, uid_owner: str) -> list[str]:
        """Delete a folder and all its subfolders and prompts, returning all deleted folder IDs"""
        # Verify folder exists and user owns it
        folder = await FolderService.get_folder_by_id(folder_id, uid_owner)
        if not folder:
            return []

        # Delete folder and get all deleted folder IDs
        deleted_folder_ids = await FolderService.delete_folder_and_get_ids(folder_id, uid_owner)
        
        # Delete all prompts in each deleted folder
        for folder_id in deleted_folder_ids:
            await PromptService.delete_prompts_by_folder_id(folder_id)
            
        return deleted_folder_ids
