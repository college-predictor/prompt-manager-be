from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime

from app.models.folder import Folder
from app.services.collection_service import CollectionService
from app.services.project_service import ProjectService


class FolderService:
    """Service for managing folder CRUD operations"""
    
    @staticmethod
    async def create_folder(
        project_id: str,
        collection_id: str,
        uid_owner: str,
        name: str,
        parent_folder_id: Optional[str] = None
    ) -> Optional[Folder]:
        """Create a new folder within a collection or another folder"""
        # Verify collection exists and user owns it
        collection = await CollectionService.get_collection_by_id(collection_id)
        if not collection or collection.uid_owner != uid_owner:
            return None
            
        # If parent_folder_id is provided, verify it exists and user owns it
        if parent_folder_id:
            parent_folder = await FolderService.get_folder_by_id(parent_folder_id)
            if not parent_folder or parent_folder.uid_owner != uid_owner:
                return None
        
        folder = Folder(
            name=name,
            collection_id=collection_id,
            project_id=project_id,
            parent_folder_id=parent_folder_id,
            uid_owner=uid_owner
        )
        
        # Save the folder
        saved_folder = await folder.insert()
        
        # If there's a parent folder, add this folder to its subfolders
        if parent_folder_id:
            await FolderService.add_subfolder(parent_folder_id, str(saved_folder.id))
            
        return saved_folder
    
    @staticmethod
    async def get_folder_by_id(folder_id: str) -> Optional[Folder]:
        """Get a specific folder"""
        try:
            return await Folder.find_one(
                Folder.id == PydanticObjectId(folder_id)
            )
        except Exception:
            return None
    
    @staticmethod
    async def get_collection_root_folders(collection_id: str) -> List[Folder]:
        """Get all root-level folders in a collection"""
        return await Folder.find(
            Folder.collection_id == collection_id,
            Folder.parent_folder_id == None
        ).to_list()
    
    @staticmethod
    async def get_subfolder_ids(folder_id: str, uid_owner: str) -> List[Folder]:
        """Get all subfolders of a folder"""
        folder = await FolderService.get_folder_by_id(folder_id)

        return folder.subfolders if folder and folder.uid_owner == uid_owner else []
    
    @staticmethod
    async def add_subfolder(parent_folder_id: str, subfolder_id: str) -> bool:
        """Add a subfolder reference to a parent folder"""
        result = await Folder.find_one(
            Folder.id == PydanticObjectId(parent_folder_id)
        ).update({"$push": {"subfolders": subfolder_id}})
        return result.modified_count > 0
    
    @staticmethod
    async def add_prompt(folder_id: str, prompt_id: str) -> bool:
        """Add a prompt reference to a folder"""
        result = await Folder.find_one(
            Folder.id == PydanticObjectId(folder_id)
        ).update({"$push": {"prompts": prompt_id}})
        return result.modified_count > 0
    
    @staticmethod
    async def update_folder(
        folder_id: str,
        name: Optional[str] = None,
    ) -> Optional[Folder]:
        """Update a folder's details"""
        folder = await FolderService.get_folder_by_id(folder_id)
        if not folder:
            return None

        update_data = {}
        if name is not None:
            update_data["name"] = name

        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await folder.update({"$set": update_data})
            return await FolderService.get_folder_by_id(folder_id)
        return folder
    
    @staticmethod
    async def delete_folder_and_get_ids(folder_id: str) -> list[str]:
        """Delete a folder and return all deleted folder IDs (including subfolders)"""
        folder = await FolderService.get_folder_by_id(folder_id)
        if not folder:
            return []
            
        deleted_ids = [str(folder.id)]  # Add current folder's ID
        
        # Recursively delete all subfolders and collect their IDs
        for subfolder_id in folder.subfolders:
            subfolder_deleted_ids = await FolderService.delete_folder_and_get_ids(subfolder_id)
            deleted_ids.extend(subfolder_deleted_ids)
            
        # Delete the folder itself
        await folder.delete()
        return deleted_ids