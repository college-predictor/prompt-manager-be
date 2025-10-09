from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from app.schemas.prompts_schema import (
    PromptCreate,
    PromptUpdate,
    PromptResponse,
    PromptDetailResponse,
    PromptHistoryResponse,
    PromptSearchRequest,
    RestoreVersionRequest
)
from app.services.prompt_service import PromptService
from app.core.firebase_auth import get_current_user

router = APIRouter()


def prompt_to_response(prompt) -> PromptResponse:
    """Convert Prompt document to PromptResponse"""
    return PromptResponse(
        id=str(prompt.id),
        location=prompt.location,
        uid_owner=prompt.uid_owner,
        title=prompt.title,
        description=prompt.description,
        prompt_text=prompt.prompt_text,
        tags=prompt.tags,
        is_public=prompt.is_public,
        created_at=prompt.created_at,
        updated_at=prompt.updated_at,
        history_count=len(prompt.history)
    )


def prompt_to_detail_response(prompt) -> PromptDetailResponse:
    """Convert Prompt document to PromptDetailResponse with history"""
    return PromptDetailResponse(
        id=str(prompt.id),
        location=prompt.location,
        uid_owner=prompt.uid_owner,
        title=prompt.title,
        description=prompt.description,
        prompt_text=prompt.prompt_text,
        tags=prompt.tags,
        is_public=prompt.is_public,
        created_at=prompt.created_at,
        updated_at=prompt.updated_at,
        history_count=len(prompt.history),
        history=[
            PromptHistoryResponse(
                timestamp=h.timestamp,
                prompt_text=h.prompt_text,
                changed_by=h.changed_by
            ) for h in prompt.history
        ]
    )


@router.post("/", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt_data: PromptCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new prompt"""
    prompt = await PromptService.create_prompt(
        location=prompt_data.location,
        uid_owner=current_user["uid"],
        title=prompt_data.title,
        prompt_text=prompt_data.prompt_text,
        description=prompt_data.description,
        tags=prompt_data.tags,
        is_public=prompt_data.is_public
    )
    return prompt_to_response(prompt)


@router.get("/{prompt_id}", response_model=PromptDetailResponse)
async def get_prompt(
    prompt_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a prompt by ID with full history"""
    prompt = await PromptService.get_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Check access permissions
    if not prompt.is_public and prompt.uid_owner != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return prompt_to_detail_response(prompt)


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: str,
    prompt_data: PromptUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a prompt (will track history if prompt_text changes)"""
    # Check ownership
    existing_prompt = await PromptService.get_prompt_by_id(prompt_id)
    if not existing_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    if existing_prompt.uid_owner != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this prompt")
    
    prompt = await PromptService.update_prompt(
        prompt_id=prompt_id,
        uid_user=current_user["uid"],
        title=prompt_data.title,
        description=prompt_data.description,
        prompt_text=prompt_data.prompt_text,
        tags=prompt_data.tags,
        is_public=prompt_data.is_public
    )
    
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return prompt_to_response(prompt)


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a prompt"""
    # Check ownership
    existing_prompt = await PromptService.get_prompt_by_id(prompt_id)
    if not existing_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    if existing_prompt.uid_owner != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this prompt")
    
    success = await PromptService.delete_prompt(prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")


@router.get("/", response_model=List[PromptResponse])
async def list_my_prompts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: dict = Depends(get_current_user)
):
    """List all prompts owned by the current user"""
    prompts = await PromptService.get_prompts_by_owner(
        uid_owner=current_user["uid"],
        skip=skip,
        limit=limit
    )
    return [prompt_to_response(p) for p in prompts]


@router.get("/location/{location}", response_model=List[PromptResponse])
async def list_prompts_by_location(
    location: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: dict = Depends(get_current_user)
):
    """List prompts by location for the current user"""
    prompts = await PromptService.get_prompts_by_location(
        location=location,
        uid_owner=current_user["uid"],
        skip=skip,
        limit=limit
    )
    return [prompt_to_response(p) for p in prompts]


@router.get("/public/all", response_model=List[PromptResponse])
async def list_public_prompts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500)
):
    """List all public prompts (no authentication required)"""
    prompts = await PromptService.get_public_prompts(skip=skip, limit=limit)
    return [prompt_to_response(p) for p in prompts]


@router.post("/search", response_model=List[PromptResponse])
async def search_prompts(
    search_params: PromptSearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """Search prompts by query and tags"""
    prompts = await PromptService.search_prompts(
        query=search_params.query,
        uid_owner=current_user["uid"],
        tags=search_params.tags,
        skip=search_params.skip,
        limit=search_params.limit
    )
    return [prompt_to_response(p) for p in prompts]


@router.get("/{prompt_id}/history", response_model=List[PromptHistoryResponse])
async def get_prompt_history(
    prompt_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the complete history of a prompt"""
    prompt = await PromptService.get_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Check access permissions
    if not prompt.is_public and prompt.uid_owner != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return [
        PromptHistoryResponse(
            timestamp=h.timestamp,
            prompt_text=h.prompt_text,
            changed_by=h.changed_by
        ) for h in prompt.history
    ]


@router.post("/{prompt_id}/restore", response_model=PromptResponse)
async def restore_prompt_version(
    prompt_id: str,
    restore_data: RestoreVersionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Restore a prompt to a previous version from history"""
    # Check ownership
    existing_prompt = await PromptService.get_prompt_by_id(prompt_id)
    if not existing_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    if existing_prompt.uid_owner != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Not authorized to restore this prompt")
    
    prompt = await PromptService.restore_prompt_version(
        prompt_id=prompt_id,
        history_index=restore_data.history_index,
        uid_user=current_user["uid"]
    )
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Invalid history index")
    
    return prompt_to_response(prompt)
