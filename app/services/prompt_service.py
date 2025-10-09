from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime
from app.models.prompt import Prompt, PromptHistory
from app.services.collection_service import CollectionService
from app.services.project_service import ProjectService


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
        # Verify collection exists and user owns it
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
        await CollectionService.add_prompt_id_to_collection(collection_id, str(saved_prompt.id), uid_owner)
        
        return saved_prompt

    @staticmethod    
    async def get_prompt_by_id(prompt_id: str, uid_owner: str) -> Optional[Prompt]:
        """Get a specific prompt only if user owns it (for modifications)""" 
        try:
            return await Prompt.find_one(
                Prompt.id == PydanticObjectId(prompt_id),
                Prompt.uid_owner == uid_owner,
            )
        except Exception:
            return None
    
    @staticmethod
    async def get_collection_prompts(collection_id: str, uid_owner: str) -> List[Prompt]:    
        """Get all prompts in a collection"""
        return await Prompt.find(
            Prompt.collection_id == collection_id,
            Prompt.uid_owner == uid_owner
        ).sort("-created_at").to_list()

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
            # Create prompt history entry
            old_prompt = PromptHistory(
                prompt_id=prompt_id,
                timestamp=prompt.updated_at,
                prompt_text=prompt.prompt_text,
                change_message=change_message,
                uid_owner=uid_owner
            )
            saved_old_prompt = await old_prompt.insert()
            
        
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
            update_data["version_history"] = prompt.version_history.append(str(saved_old_prompt.id))
        
        await prompt.update({"$set": update_data})
        return await prompt.save()

    @staticmethod
    async def delete_prompt(prompt_id: str, uid_owner: str) -> bool:
        """Delete a prompt if user owns it"""
        prompt = await PromptService.get_prompt_by_id(prompt_id, uid_owner)
        if not prompt:
            return False
        
        await CollectionService.remove_prompt_id_from_collection(
            prompt.collection_id,
            prompt_id,
            uid_owner
        )

        # Delete all history entries for this prompt
        await PromptHistory.find(
            PromptHistory.prompt_id == prompt_id
        ).delete()
        
        # Delete the prompt
        await prompt.delete()
        return True        

    @staticmethod
    async def get_prompt_history(prompt_id: str, uid_owner: str) -> Optional[List[PromptHistory]]:
        # Get all history entries for this prompt, sorted by timestamp (newest first)
        history_entries = await PromptHistory.find(
            PromptHistory.prompt_id == prompt_id,
            PromptHistory.uid_owner == uid_owner
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