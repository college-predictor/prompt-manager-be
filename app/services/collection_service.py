from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime

from app.models.project import Collection
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
    async def get_user_collections(uid_owner: str) -> List[Collection]:
        """Get all collections owned by a user"""
        return await Collection.find(
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
        collection = await CollectionService.get_collection_by_id_owner_only(collection_id, uid_owner)
        if not collection:
            return False
        
        # Import here to avoid circular imports
        from app.models.project import Prompt, PromptHistory
        
        # Get all prompts in this collection
        prompts = await Prompt.find(
            Prompt.collection_id == collection_id,
            Prompt.uid_owner == uid_owner
        ).to_list()
        
        # Delete history for each prompt
        for prompt in prompts:
            await PromptHistory.find(
                PromptHistory.prompt_id == str(prompt.id)
            ).delete()
        
        # Delete all prompts in this collection
        await Prompt.find(
            Prompt.collection_id == collection_id,
            Prompt.uid_owner == uid_owner
        ).delete()
        
        # Remove collection ID from project's collections list
        await ProjectService.remove_collection_from_project(
            collection.project_id,
            collection_id,
            uid_owner
        )
        
        # Delete the collection
        await collection.delete()
        return True
    
    @staticmethod
    async def add_prompt_to_collection(collection_id: str, prompt_id: str, uid_owner: str) -> bool:
        """Add a prompt ID to collection's prompts list"""
        collection = await CollectionService.get_collection_by_id_owner_only(collection_id, uid_owner)
        if not collection:
            return False
        
        if prompt_id not in collection.prompts:
            collection.prompts.append(prompt_id)
            await collection.save()
        
        return True
    
    @staticmethod
    async def remove_prompt_from_collection(collection_id: str, prompt_id: str, uid_owner: str) -> bool:
        """Remove a prompt ID from collection's prompts list"""
        collection = await CollectionService.get_collection_by_id_owner_only(collection_id, uid_owner)
        if not collection:
            return False
        
        if prompt_id in collection.prompts:
            collection.prompts.remove(prompt_id)
            await collection.save()
        
        return True
    
    @staticmethod
    async def get_collection_prompts(collection_id: str, uid_owner: str, include_public: bool = False) -> List:
        """Get all prompts in a collection"""
        from app.models.project import Prompt
        
        # First verify collection access
        collection = await CollectionService.get_collection_by_id(collection_id, uid_owner)
        if not collection:
            return []
        
        if include_public:
            return await Prompt.find(
                Prompt.collection_id == collection_id,
                {"$or": [
                    {"uid_owner": uid_owner},
                    {"is_public": True}
                ]}
            ).sort("-created_at").to_list()
        else:
            return await Prompt.find(
                Prompt.collection_id == collection_id,
                Prompt.uid_owner == uid_owner
            ).sort("-created_at").to_list()
    
    @staticmethod
    async def get_collection_stats(collection_id: str, uid_owner: str) -> Optional[dict]:
        """Get statistics for a collection"""
        collection = await CollectionService.get_collection_by_id(collection_id, uid_owner)
        if not collection:
            return None
        
        from app.models.project import Prompt
        
        # Count prompts
        prompts_count = await Prompt.count_documents(
            Prompt.collection_id == collection_id,
            Prompt.uid_owner == uid_owner
        )
        
        # Count public prompts
        public_prompts_count = await Prompt.count_documents(
            Prompt.collection_id == collection_id,
            Prompt.uid_owner == uid_owner,
            Prompt.is_public == True
        )
        
        # Get tags usage
        prompts = await Prompt.find(
            Prompt.collection_id == collection_id,
            Prompt.uid_owner == uid_owner
        ).to_list()
        
        all_tags = []
        for prompt in prompts:
            all_tags.extend(prompt.tags)
        
        # Count tag usage
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            "collection_id": collection_id,
            "collection_name": collection.name,
            "project_id": collection.project_id,
            "prompts_count": prompts_count,
            "public_prompts_count": public_prompts_count,
            "tag_usage": tag_counts,
            "is_public": collection.is_public,
            "created_at": collection.created_at
        }