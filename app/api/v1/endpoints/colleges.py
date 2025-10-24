from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Optional
from beanie import PydanticObjectId
from app.models.college import College
from app.schemas.base import BaseResponseSchema
from app.services.college_service import CollegeService

router = APIRouter()


@router.get(
    "/",
    response_model=BaseResponseSchema,
    summary="Get list of colleges",
    description="Retrieve colleges with optional filtering, sorting, and pagination"
)
async def get_colleges(
    search: Optional[str] = Query(
        None,
        description="Search by college name (case-insensitive)",
        min_length=2,
        max_length=100
    ),
    state: Optional[str] = Query(
        None,
        description="Filter by state (e.g., Delhi, Karnataka, Maharashtra)"
    ),
    type: Optional[str] = Query(
        None,
        description="Filter by college type (Public or Private)"
    ),
    category: Optional[str] = Query(
        None,
        description="Filter by category (e.g., Engineering, Medical, Management)"
    ),
    sort_by: Optional[str] = Query(
        None,
        description="Sort by field",
        pattern="^(ranking|rating|fees|placement)$",
        alias="sortBy"
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number (starts from 1)"
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of items per page (max 100)"
    ),
) -> BaseResponseSchema:
    """
    Get colleges with optional filters and pagination.
    """
    try:
        print("query params:", {
            "search": search,
            "state": state,
            "type": type,
            "category": category,
            "sort_by": sort_by,
            "page": page,
            "limit": limit
        })
        # Build query filters
        query = {}
        
        if search:
            search = search.strip()
            query["name"] = {"$regex": search, "$options": "i"}
        
        if state:
            query["state"] = state.strip()
        
        if type:
            valid_types = ["Public", "Private"]
            if type not in valid_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid type. Must be one of: {', '.join(valid_types)}"
                )
            query["type"] = type
        
        if category:
            query["category"] = category.strip()
        
        # Build sort criteria
        sort_criteria = None
        if sort_by:
            sort_fields = {
                "ranking": "ranking",
                "rating": "rating",
                "fees": "fees",
                "placement": "placement",
            }
            sort_field = sort_fields.get(sort_by)
            sort_order = -1  # Descending order
            sort_criteria = [(sort_field, sort_order)]
        
        # Fetch colleges from service
        colleges_data = await CollegeService.get_colleges(
            query=query,
            sort_criteria=sort_criteria,
            page=page,
            page_size=limit
        )
        
        return BaseResponseSchema(
            success=True,
            message="Colleges retrieved successfully",
            data=colleges_data.model_dump()
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching colleges"
        )


@router.get(
    "/{college_id}",
    response_model=BaseResponseSchema,
    summary="Get college by ID"
)
async def get_college_by_id(college_id: str) -> BaseResponseSchema:
    """Get detailed information about a specific college."""
    try:
        college = await CollegeService.get_college_by_id(college_id)
        
        if not college:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"College with ID {college_id} not found"
            )
        
        return BaseResponseSchema(
            success=True,
            message="College retrieved successfully",
            data=college
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the college"
        )


@router.get(
    "/filters/states",
    response_model=BaseResponseSchema,
    summary="Get available states"
)
async def get_states() -> BaseResponseSchema:
    """Get list of all states that have colleges."""
    try:
        states = await CollegeService.get_unique_states()
        
        return BaseResponseSchema(
            success=True,
            message="States retrieved successfully",
            data={"states": states}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching states"
        )


@router.get(
    "/filters/categories",
    response_model=BaseResponseSchema,
    summary="Get available categories"
)
async def get_categories() -> BaseResponseSchema:
    """Get list of all college categories."""
    try:
        categories = await CollegeService.get_unique_categories()
        
        return BaseResponseSchema(
            success=True,
            message="Categories retrieved successfully",
            data={"categories": categories}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching categories"
        )