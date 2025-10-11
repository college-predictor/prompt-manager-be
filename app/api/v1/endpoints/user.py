from fastapi import APIRouter, Request, HTTPException, status
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectList
from app.services.data_service import UserDataManager, ProjectService


router = APIRouter()

user_data_manager = UserDataManager()

# Project endpoints
@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(request: Request, project: ProjectCreate):
    """Create a new project"""
    project.uid_owner = request.state.user['uid']
    return await ProjectService.create_project(**project.model_dump_json())

@router.get("/projects", response_model=List[ProjectList])
async def list_projects(request: Request):
    """List all projects owned by the user"""
    if not hasattr(request.state, '_state') or 'user' not in request.state._state:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    return await ProjectService.get_user_projects(uid_owner=request.state._state['user']['uid'])

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(request: Request, project_id: str):
    """Get a specific project"""
    project = await ProjectService.get_project_by_id(project_id)
    if not project or project.uid_owner != request.state.user['uid']:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(request: Request, project_id: str, project_update: ProjectUpdate):
    """Update a project"""
    project = await ProjectService.get_project_by_id(project_id)
    if not project or project.uid_owner != request.state.user['uid']:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_project = await ProjectService.update_project(
        project_id,
        name=project_update.name,
        description=project_update.description
    )
    if not updated_project:
        raise HTTPException(status_code=400, detail="Failed to update project")
    
    return updated_project

@router.delete("/projects/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(request: Request, project_id: str):
    """Delete a project and all its associated collections, folders, and prompts"""
    try:
        # First verify project exists and user owns it
        project = await ProjectService.get_project_by_id(project_id)
        if not project or project.uid_owner != request.state.user['uid']:
            raise HTTPException(status_code=404, detail="Project not found")

        # Delete project and all contents
        deleted = await user_data_manager.delete_project_and_contents(
            project_id=project_id, 
            uid_owner=request.state.user['uid']
        )
        
        if not deleted:
            raise HTTPException(
                status_code=500, 
                detail="Failed to delete project and its contents"
            )
            
        return {
            "message": "Project and all its contents deleted successfully",
            "project_id": project_id
        }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting the project: {str(e)}"
        )