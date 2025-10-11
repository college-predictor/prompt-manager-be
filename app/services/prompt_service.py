from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime
from app.models.prompt import Prompt, PromptHistory
from app.services.collection_service import CollectionService
from app.services.project_service import ProjectService
from app.services.folder_service import FolderService


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
        folder_id: Optional[str] = None,
    ) -> Optional[Prompt]:
        """Create a new prompt within a collection or folder"""
        # Verify collection exists and user owns it
        collection = await CollectionService.get_collection_by_id(collection_id)
        if not collection or collection.uid_owner != uid_owner:
            return None
            
        # If folder_id is provided, verify it exists and user owns it
        if folder_id:
            folder = await FolderService.get_folder_by_id(folder_id)
            if not folder or folder.uid_owner != uid_owner:
                return None
                
        prompt = Prompt(
            title=title,
            description=description,
            prompt_text=prompt_text,
            project_id=project_id,
            collection_id=collection_id,
            uid_owner=uid_owner,
            tags=tags or [],
            folder_id=folder_id,
            version_history=[]  # Start with initial version
        )
        # Save the prompt
        saved_prompt = await prompt.insert()
        
        # Add prompt reference to folder if specified, otherwise to collection
        if folder_id:
            await FolderService.add_prompt(folder_id, str(saved_prompt.id))
        else:
            await CollectionService.add_prompt_id_to_collection(collection_id, str(saved_prompt.id), uid_owner)
        
        return saved_prompt

    @staticmethod    
    async def get_prompt_by_id(prompt_id: str) -> Optional[Prompt]:
        """Get a specific prompt only if user owns it (for modifications)""" 
        try:
            return await Prompt.find_one(
                Prompt.id == PydanticObjectId(prompt_id)
            )
        except Exception:
            return None
    
    @staticmethod
    async def get_collection_prompts(collection_id: str) -> List[Prompt]:    
        """Get all prompts in a collection"""
        return await Prompt.find(
            Prompt.collection_id == collection_id
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
        title: Optional[str] = None,
        description: Optional[str] = None,
        prompt_text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        change_message: Optional[str] = None
    ) -> Optional[Prompt]:
        """Update a prompt if user owns it and track history"""
        prompt = await PromptService.get_prompt_by_id(prompt_id)
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
                change_message=change_message
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
            update_data["change_history"] = prompt.change_history.append(str(saved_old_prompt.id))
        
        await prompt.update({"$set": update_data})
        return await prompt.save()

    @staticmethod
    async def get_prompt_history_by_id(history_id: str) -> Optional[List[PromptHistory]]:
        # Get all history entries for this prompt, sorted by timestamp (newest first)
        history_entries = await PromptHistory.find(
            PromptHistory.prompt_id == history_id
        ).sort("-timestamp").to_list()
        
        return history_entries

    @staticmethod
    async def get_prompt_history(
        prompt_id: str,
        version: str
    ) -> Optional[PromptHistory]:
        """Get a specific version of a prompt"""
        # Verify user owns the prompt
        prompt = await PromptService.get_prompt_by_id(prompt_id)
        if not prompt:
            return None
        
        # Get the specific version
        return await PromptHistory.find_one(
            PromptHistory.prompt_id == prompt_id,
            PromptHistory.version == version
        )

    @staticmethod
    async def delete_prompt(prompt_id: str) -> bool:
        """Delete a prompt if user owns it, including all history versions"""
        # Delete the prompt
        await Prompt.find_one(
            Prompt.id == PydanticObjectId(prompt_id)
        ).delete

        # Delete all history versions for this prompt
        await PromptHistory.find(
            PromptHistory.prompt_id == prompt_id
        ).delete()

        return True
    
    @staticmethod
    async def delete_prompts_by_collection(collection_id: str) -> int:
        """Delete all prompts in a collection if user owns them, including all history versions"""
        prompts = await PromptService.get_collection_prompts(collection_id)
        deleted_count = 0
        for prompt in prompts:
            # Delete all history versions for this prompt
            await PromptHistory.find(
                PromptHistory.prompt_id == str(prompt.id)
            ).delete()
            
            # Delete the prompt
            await prompt.delete()
            deleted_count += 1
        return deleted_count
    
    @staticmethod
    async def delete_prompts_by_project(project_id: str) -> int:
        """Delete all prompts in a project if user owns them, including all history versions"""
        # Get all prompts in the project first
        all_prompts = await Prompt.find(
            Prompt.project_id == project_id
        ).to_list()
        
        if not all_prompts:
            return 0
        
        # Extract all prompt IDs for bulk history deletion
        prompt_ids = [str(prompt.id) for prompt in all_prompts]
        
        # Delete all history entries for all prompts in one operation
        await PromptHistory.find(
            PromptHistory.prompt_id.in_(prompt_ids),
        ).delete()
        
        # Delete all prompts
        deleted_count = 0
        for prompt in all_prompts:
            await prompt.delete()
            deleted_count += 1
            
        return deleted_count
    
    async def delete_prompts_by_folder_id(self, folder_id: str) -> int:
        """Delete all prompts in a folder if user owns them, including all history versions"""
        prompts = await Prompt.find(
            Prompt.folder_id == folder_id
        ).to_list()
        
        deleted_count = 0
        for prompt in prompts:
            # Delete all history versions for this prompt
            await PromptHistory.find(
                PromptHistory.prompt_id == str(prompt.id)
            ).delete()
            
            # Delete the prompt
            await prompt.delete()
            deleted_count += 1
        return deleted_count