from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime

from app.models.project import Project


class ProjectService:
    """Service for managing project CRUD operations"""
    
    @staticmethod
    async def create_project(uid_owner: str, name: str, description: str = "") -> Project:
        """Create a new project for a user"""
        project = Project(
            name=name,
            description=description,
            uid_owner=uid_owner,
            collections=[]  # Initialize empty collections list
        )
        return await project.insert()
    
    @staticmethod
    async def get_project_by_id(project_id: str, uid_owner: str) -> Optional[Project]:
        """Get a specific project if user owns it"""
        try:
            return await Project.find_one(
                Project.id == PydanticObjectId(project_id),
                Project.uid_owner == uid_owner
            )
        except Exception:
            return None
    
    @staticmethod
    async def get_user_projects(uid_owner: str) -> List[Project]:
        """Get all projects for a user"""
        return await Project.find(
            Project.uid_owner == uid_owner
        ).sort("-created_at").to_list()
    
    @staticmethod
    async def update_project(
        project_id: str,
        uid_owner: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[Project]:
        """Update a project if user owns it"""
        project = await ProjectService.get_project_by_id(project_id, uid_owner)
        if not project:
            return None
        
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        
        if update_data:
            await project.update({"$set": update_data})
            return await project.save()
        
        return project
    
    @staticmethod
    async def delete_project(project_id: str, uid_owner: str) -> bool:
        """Delete a project and all its collections and prompts"""
        project = await ProjectService.get_project_by_id(project_id, uid_owner)
        if not project:
            return False
        
        # Import here to avoid circular imports
        from app.models.project import Collection, Prompt, PromptHistory
        
        # Get all collections in this project
        collections = await Collection.find(
            Collection.project_id == project_id,
            Collection.uid_owner == uid_owner
        ).to_list()
        
        # Delete all prompts and their history in this project
        for collection in collections:
            collection_id = str(collection.id)
            
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
        
        # Delete all collections in this project
        await Collection.find(
            Collection.project_id == project_id,
            Collection.uid_owner == uid_owner
        ).delete()
        
        # Delete the project
        await project.delete()
        return True
    
    @staticmethod
    async def add_collection_to_project(project_id: str, collection_id: str, uid_owner: str) -> bool:
        """Add a collection ID to project's collections list"""
        project = await ProjectService.get_project_by_id(project_id, uid_owner)
        if not project:
            return False
        
        if collection_id not in project.collections:
            project.collections.append(collection_id)
            await project.save()
        
        return True
    
    @staticmethod
    async def remove_collection_from_project(project_id: str, collection_id: str, uid_owner: str) -> bool:
        """Remove a collection ID from project's collections list"""
        project = await ProjectService.get_project_by_id(project_id, uid_owner)
        if not project:
            return False
        
        if collection_id in project.collections:
            project.collections.remove(collection_id)
            await project.save()
        
        return True
    
    @staticmethod
    async def get_project_stats(project_id: str, uid_owner: str) -> Optional[dict]:
        """Get statistics for a project"""
        project = await ProjectService.get_project_by_id(project_id, uid_owner)
        if not project:
            return None
        
        from app.models.project import Collection, Prompt
        
        # Count collections
        collections_count = await Collection.count_documents(
            Collection.project_id == project_id,
            Collection.uid_owner == uid_owner
        )
        
        # Count prompts
        prompts_count = await Prompt.count_documents(
            Prompt.project_id == project_id,
            Prompt.uid_owner == uid_owner
        )
        
        # Count public prompts
        public_prompts_count = await Prompt.count_documents(
            Prompt.project_id == project_id,
            Prompt.uid_owner == uid_owner,
        )
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "collections_count": collections_count,
            "prompts_count": prompts_count,
            "public_prompts_count": public_prompts_count,
            "created_at": project.created_at
        }