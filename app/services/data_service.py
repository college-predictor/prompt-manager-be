from typing import Optional
from app.services.project_service import ProjectService
from app.services.collection_service import CollectionService
from app.services.prompt_service import PromptService

# Export all services
__all__ = [
    'ProjectService',
    'CollectionService', 
    'PromptService',
    'DataService'
]


class DataService:
    """
    Unified service class that combines all CRUD operations.
    Provides convenience methods for common cross-service operations.
    """
    
    # Reference to individual services
    projects = ProjectService
    collections = CollectionService
    prompts = PromptService
    
    @staticmethod
    async def get_user_overview(uid_owner: str) -> dict:
        """Get complete overview of user's data"""
        projects = await ProjectService.get_user_projects(uid_owner)
        
        total_collections = 0
        total_prompts = 0
        total_public_prompts = 0
        
        project_details = []
        
        for project in projects:
            project_stats = await ProjectService.get_project_stats(str(project.id), uid_owner)
            
            if project_stats:
                total_collections += project_stats['collections_count']
                total_prompts += project_stats['prompts_count']
                total_public_prompts += project_stats['public_prompts_count']
                
                project_details.append(project_stats)
        
        return {
            "user_id": uid_owner,
            "summary": {
                "total_projects": len(projects),
                "total_collections": total_collections,
                "total_prompts": total_prompts,
                "total_public_prompts": total_public_prompts
            },
            "projects": project_details
        }
    
    @staticmethod
    async def search_all(
        uid_owner: str,
        query: str,
        include_public: bool = True
    ) -> dict:
        """Search across all user's data"""
        
        # Search projects, collections, and prompts in parallel
        projects = await ProjectService.get_user_projects(uid_owner)
        filtered_projects = [
            p for p in projects 
            if query.lower() in p.name.lower() or query.lower() in p.description.lower()
        ]
        
        collections = await CollectionService.search_collections(
            uid_owner, query, include_public
        )
        
        prompts = await PromptService.search_prompts(
            uid_owner, query, include_public=include_public
        )
        
        return {
            "query": query,
            "results": {
                "projects": filtered_projects,
                "collections": collections,
                "prompts": prompts
            },
            "counts": {
                "projects": len(filtered_projects),
                "collections": len(collections),
                "prompts": len(prompts),
                "total": len(filtered_projects) + len(collections) + len(prompts)
            }
        }
    
    @staticmethod
    async def get_hierarchy(uid_owner: str, project_id: str) -> dict:
        """Get complete hierarchical view of a project"""
        project = await ProjectService.get_project_by_id(project_id, uid_owner)
        if not project:
            return {}
        
        collections = await CollectionService.get_project_collections(project_id, uid_owner)
        
        project_data = {
            "project": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at
            },
            "collections": []
        }
        
        for collection in collections:
            prompts = await CollectionService.get_collection_prompts(str(collection.id), uid_owner)
            
            collection_data = {
                "id": str(collection.id),
                "name": collection.name,
                "description": collection.description,
                "created_at": collection.created_at,
                "prompts": [
                    {
                        "id": str(prompt.id),
                        "title": prompt.title,
                        "description": prompt.description,
                        "current_version": prompt.current_version,
                        "tags": prompt.tags,
                        "created_at": prompt.created_at,
                        "updated_at": prompt.updated_at
                    }
                    for prompt in prompts
                ]
            }
            
            project_data["collections"].append(collection_data)
        
        return project_data
    
    @staticmethod
    async def bulk_delete_project(uid_owner: str, project_id: str) -> dict:
        """Delete a project and return detailed information about what was deleted"""
        
        # Get project info before deletion
        project = await ProjectService.get_project_by_id(project_id, uid_owner)
        if not project:
            return {"error": "Project not found or access denied"}
        
        # Count what will be deleted
        collections = await CollectionService.get_project_collections(project_id, uid_owner)
        
        total_prompts = 0
        total_history_entries = 0
        
        for collection in collections:
            prompts = await CollectionService.get_collection_prompts(str(collection.id), uid_owner)
            total_prompts += len(prompts)
            
            # Count history entries
            from app.models.project import PromptHistory
            for prompt in prompts:
                history_count = await PromptHistory.count_documents(
                    PromptHistory.prompt_id == str(prompt.id)
                )
                total_history_entries += history_count
        
        # Perform the deletion
        success = await ProjectService.delete_project(project_id, uid_owner)
        
        if success:
            return {
                "success": True,
                "deleted": {
                    "project_name": project.name,
                    "collections_count": len(collections),
                    "prompts_count": total_prompts,
                    "history_entries_count": total_history_entries
                }
            }
        else:
            return {"error": "Failed to delete project"}
    
    @staticmethod
    async def duplicate_prompt(
        uid_owner: str,
        prompt_id: str,
        target_collection_id: str,
        new_title: Optional[str] = None
    ) -> Optional[dict]:
        """Duplicate a prompt to another collection"""
        
        # Get the original prompt
        original_prompt = await PromptService.get_prompt_by_id(prompt_id, uid_owner)
        if not original_prompt:
            return None
        
        # Get target collection
        target_collection = await CollectionService.get_collection_by_id_owner_only(target_collection_id, uid_owner)
        if not target_collection:
            return None
        
        # Create new prompt
        new_prompt = await PromptService.create_prompt(
            project_id=target_collection.project_id,
            collection_id=target_collection_id,
            uid_owner=uid_owner,
            title=new_title or f"{original_prompt.title} (Copy)",
            prompt_text=original_prompt.prompt_text,
            description=original_prompt.description,
            tags=original_prompt.tags.copy(),
        )
        
        return {
            "original_prompt_id": prompt_id,
            "new_prompt_id": str(new_prompt.id),
            "new_prompt_title": new_prompt.title,
            "target_collection": target_collection.name
        }