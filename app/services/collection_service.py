from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime

from app.models.collection import Collection
from app.services.project_service import ProjectService


class CollectionService:
    """Service for managing collection CRUD operations"""
    
    @staticmethod
    async def create_collection(
        project_id: str,
        uid_owner: str,
        name: str,
        description: str = "",
    ) -> Optional[Collection]:
        """Create a collection within a project"""
        # Verify project exists and user owns it
        project = await ProjectService.get_project_by_id(project_id, uid_owner)
        if not project:
            return None
        
        collection = Collection(
            name=name,
            description=description,
            project_id=project_id,
            uid_owner=uid_owner,
            prompts=[],  # Initialize empty prompts list
        )
        
        # Save the collection
        saved_collection = await collection.insert()
        
        # Add collection ID to project's collections list
        await ProjectService.add_collection_to_project(
            project_id, 
            str(saved_collection.id), 
            uid_owner
        )
        
        return saved_collection
    
    @staticmethod
    async def get_collection_by_id(collection_id: str, uid_owner: str) -> Optional[Collection]:
        """Get a specific collection only if user owns it (for modifications)"""
        try:
            return await Collection.find_one(
                Collection.id == PydanticObjectId(collection_id),
                Collection.uid_owner == uid_owner
            )
        except Exception:
            return None
    
    @staticmethod
    async def get_project_collections(project_id: str, uid_owner: str) -> List[Collection]:
        """Get all collections in a project"""
        return await Collection.find(
            Collection.project_id == project_id,
            Collection.uid_owner == uid_owner
        ).sort("-created_at").to_list()
    
    @staticmethod
    async def update_collection(
        collection_id: str,
        uid_owner: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Collection]:
        """Update a collection if user owns it"""
        collection = await CollectionService.get_collection_by_id_owner_only(collection_id, uid_owner)
        if not collection:
            return None
        
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        
        if update_data:
            await collection.update({"$set": update_data})
            return await collection.save()
        
        return collection
    
    @staticmethod
    async def delete_collection(collection_id: str, uid_owner: str) -> bool:
        """Delete a collection and all its prompts"""
        collection = await CollectionService.get_collection_by_id(collection_id, uid_owner)
        if not collection:
            return False
        # Delete the collection
        await collection.delete()
        return True
    
    @staticmethod
    async def delete_collections_by_project(project_id: str, uid_owner: str) -> int:
        """Delete all collections in a project"""
        collections = await Collection.find(
            Collection.project_id == project_id,
            Collection.uid_owner == uid_owner
        ).to_list()
        
        deleted_count = 0
        for collection in collections:
            await collection.delete()
            deleted_count += 1
        
        return deleted_count
    
