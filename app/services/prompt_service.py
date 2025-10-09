from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime
from app.models.prompt import Prompt, PromptHistory





class PromptService:
    """Service for managing prompt CRUD operations with history tracking"""

    @staticmethod
    async def create_prompt(
        project_id: str,
        collection_id: str,
        uid_owner: str,
        title: str,
        prompt_text: str,
        description: str = "",
        tags: List[str] = None,
    ) -> Optional[Prompt]:
        """Create a new prompt within a collection"""
        # Import here to avoid circular imports
        from app.services.collection_service import CollectionService
        
        # Verify collection exists and user owns it
        collection = await CollectionService.get_collection_by_id(collection_id, uid_owner)
        if not collection or collection.project_id != project_id:
            return None
        
        # Only allow creation if user owns the collection
        if collection.uid_owner != uid_owner:
            return None
        
        # Create initial version number
        initial_version = "1.0"
        
        prompt = Prompt(
            title=title,
            description=description,
            prompt_text=prompt_text,
            project_id=project_id,
            collection_id=collection_id,
            uid_owner=uid_owner,
            tags=tags or [],
            version_history=[]  # Start with initial version
        )
        
        # Save the prompt
        saved_prompt = await prompt.insert()
        return saved_prompt

    @staticmethod    
    async def get_prompt_by_id(prompt_id: str, uid_owner: str) -> Optional[Prompt]:
        """Get a specific prompt only if user owns it (for modifications)""" 
        try:
            return await Prompt.find_one(
                Prompt.id == PydanticObjectId(prompt_id)
            )
        except Exception:
            return None

    @staticmethod
    async def get_user_prompts(uid_owner: str) -> List[Prompt]:
        """Get all prompts owned by a user"""
        return await Prompt.find(
            Prompt.uid_owner == uid_owner
        ).sort("-created_at").to_list()

    @staticmethod
    async def update_prompt(        
        prompt_id: str,
        uid_owner: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        prompt_text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        change_message: Optional[str] = None
    ) -> Optional[Prompt]:
        """Update a prompt if user owns it and track history"""
        prompt = await PromptService.get_prompt_by_id(prompt_id, uid_owner)
        if not prompt:
            return None
        
        # Check if prompt_text is being changed
        text_changed = prompt_text is not None and prompt_text != prompt.prompt_text
        
        # If text changed, create history entry before updating
        if text_changed:
            # Generate new version number
            new_version = PromptService._generate_new_version(
                prompt.version_history[-1] if prompt.version_history else "1.0"
            )
            
            # Create history entry for the new version
            await PromptService._create_history_entry(
                prompt_id=prompt_id,
                prompt_text=prompt_text,
                version=new_version,
                change_message=change_message or f"Updated to version {new_version}"
            )
            
            # Update version tracking
            if new_version not in prompt.version_history:
                prompt.version_history.append(new_version)
        
        # Update fields
        update_data = {"updated_at": datetime.utcnow()}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if prompt_text is not None:
            update_data["prompt_text"] = prompt_text
        if tags is not None:
            update_data["tags"] = tags
        
        # Update version info if text changed
        if text_changed:
            update_data["version_history"] = prompt.version_history
        
        await prompt.update({"$set": update_data})
        return await prompt.save()

    @staticmethod
    async def delete_prompt(prompt_id: str, uid_owner: str) -> bool:
        """Delete a prompt if user owns it"""
        prompt = await PromptService.get_prompt_by_id(prompt_id, uid_owner)
        if not prompt:
            return False
        
        # Delete all history entries for this prompt
        await PromptHistory.find(
            PromptHistory.prompt_id == prompt_id
        ).delete()
        
        # Delete the prompt
        await prompt.delete()
        return True        

    @staticmethod
    async def get_prompt_history(prompt_id: str, uid_owner: str) -> Optional[List[PromptHistory]]:
        """Get history of a prompt if user owns it"""
        prompt = await PromptService.get_prompt_by_id(prompt_id, uid_owner)
        if not prompt:
            return None
        
        # Get all history entries for this prompt, sorted by timestamp (newest first)
        history_entries = await PromptHistory.find(
            PromptHistory.prompt_id == prompt_id
        ).sort("-timestamp").to_list()
        
        return history_entries

    @staticmethod
    async def get_prompt_version(
        prompt_id: str,
        version: str,
        uid_owner: str
    ) -> Optional[PromptHistory]:
        """Get a specific version of a prompt"""
        # Verify user owns the prompt
        prompt = await PromptService.get_prompt_by_id(prompt_id, uid_owner)
        if not prompt:
            return None
        
        # Get the specific version
        return await PromptHistory.find_one(
            PromptHistory.prompt_id == prompt_id,
            PromptHistory.version == version
        )