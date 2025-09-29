from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from beanie import PydanticObjectId
from app.models.college import College
from app.schemas.college import (
    CollegeCreate, 
    CollegeUpdate, 
    CollegeResponse, 
    CollegeListResponse
)

router = APIRouter()

@router.post("/", response_model=CollegeResponse, status_code=201)
async def create_college(college_data: CollegeCreate):
    """Create a new college"""
    try:
        college_dict = college_data.model_dump()
        college = College(**college_dict)
        await college.create()
        return CollegeResponse(
            id=str(college.id),
            **college_dict
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating college: {str(e)}")

@router.get("/", response_model=CollegeListResponse)
async def get_colleges(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, description="Filter by type"),
    state: Optional[str] = Query(None, description="Filter by state")
):
    """Get list of colleges with pagination and filters"""
    try:
        skip = (page - 1) * size
        
        # Build query filters
        query_filter = {}
        if search:
            query_filter["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        if category:
            query_filter["category"] = category
        if type:
            query_filter["type"] = type
        if state:
            query_filter["address.state"] = {"$regex": state, "$options": "i"}
        
        # Get total count
        total = await College.find(query_filter).count()
        
        # Get colleges with pagination
        colleges = await College.find(query_filter).skip(skip).limit(size).to_list()
        
        college_responses = []
        for college in colleges:
            college_dict = college.dict()
            college_dict["id"] = str(college.id)
            college_responses.append(CollegeResponse(**college_dict))
        
        return CollegeListResponse(
            colleges=college_responses,
            total=total,
            page=page,
            size=size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching colleges: {str(e)}")

@router.get("/{college_id}", response_model=CollegeResponse)
async def get_college(college_id: str):
    """Get a specific college by ID"""
    try:
        if not PydanticObjectId.is_valid(college_id):
            raise HTTPException(status_code=400, detail="Invalid college ID")
        
        college = await College.get(PydanticObjectId(college_id))
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        
        college_dict = college.dict()
        college_dict["id"] = str(college.id)
        return CollegeResponse(**college_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching college: {str(e)}")

@router.put("/{college_id}", response_model=CollegeResponse)
async def update_college(college_id: str, college_data: CollegeUpdate):
    """Update a college"""
    try:
        if not PydanticObjectId.is_valid(college_id):
            raise HTTPException(status_code=400, detail="Invalid college ID")
        
        college = await College.get(PydanticObjectId(college_id))
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        
        # Update only provided fields
        update_data = college_data.model_dump()
        if update_data:
            await college.set(update_data)
        
        college_dict = college.dict()
        college_dict["id"] = str(college.id)
        return CollegeResponse(**college_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating college: {str(e)}")

@router.delete("/{college_id}", status_code=204)
async def delete_college(college_id: str):
    """Delete a college"""
    try:
        if not PydanticObjectId.is_valid(college_id):
            raise HTTPException(status_code=400, detail="Invalid college ID")
        
        college = await College.get(PydanticObjectId(college_id))
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        
        await college.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting college: {str(e)}")

@router.get("/{college_id}/stats")
async def get_college_stats(college_id: str):
    """Get college statistics"""
    try:
        if not PydanticObjectId.is_valid(college_id):
            raise HTTPException(status_code=400, detail="Invalid college ID")
        
        college = await College.get(PydanticObjectId(college_id))
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        
        # TODO: Add logic to get associated faculties, branches, scholarships count
        return {
            "college_id": college_id,
            "faculty_count": 0,  # Will be implemented when faculty endpoint is linked
            "branch_count": 0,   # Will be implemented when junction endpoint is linked
            "scholarship_count": 0  # Will be implemented when scholarship endpoint is linked
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching college stats: {str(e)}")