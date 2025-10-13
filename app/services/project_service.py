from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime

from app.models.project import Project


class ProjectService:
    """Service for managing project CRUD operations"""
    
    @staticmethod
    async def create_project(uid_owner: str, name: str, description: str = "") -> Optional[Project]:
        """Create a new project for a user. Do not allow duplicate names per user (compound index (name, uid_owner) exists)."""
        # check for existing project with same name for this user
        existing = await Project.find_one((Project.uid_owner == uid_owner), (Project.name == name))
        if existing:
            return None

        project = Project(
            name=name,
            description=description,
            uid_owner=uid_owner,
        )

        try:
            return await project.insert()
        except Exception:
            # In case of a race condition where the unique index rejects the insert,
            # return None to indicate failure to create.
            return None
    
    @staticmethod
    async def get_project_by_id(uid_owner: str, project_id: str) -> Optional[Project]:
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
        uid_owner: str,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[Project]:
        """Update a project if user owns it"""
        project = await ProjectService.get_project_by_id(uid_owner, project_id)
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
    async def delete_project(uid_owner: str, project_id: str) -> bool:
        """Delete a project and all its collections and prompts"""
        project = await ProjectService.get_project_by_id(
            uid_owner=uid_owner,
            project_id=project_id
        )
        if not project:
            return False

        await project.delete()
        return True
