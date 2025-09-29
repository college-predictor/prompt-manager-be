from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from beanie import PydanticObjectId
from app.models.scholarship import Scholarship
from app.models.college import College
from app.models.academics import AcademicStream
from app.schemas.scholarship import (
    ScholarshipCreate,
    ScholarshipUpdate,
    ScholarshipResponse,
    ScholarshipListResponse
)

router = APIRouter()

@router.post("/", response_model=ScholarshipResponse, status_code=201)
async def create_scholarship(scholarship_data: ScholarshipCreate):
    """Create a new scholarship"""
    try:
        scholarship_dict = scholarship_data.model_dump()
        
        # Handle college linkage
        college_id = scholarship_dict.pop('college_id')
        if not PydanticObjectId.is_valid(college_id):
            raise HTTPException(status_code=400, detail="Invalid college ID")
        
        college = await College.get(PydanticObjectId(college_id))
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        
        scholarship_dict['college'] = college
        
        # Handle eligible streams linkage if provided
        stream_ids = scholarship_dict.pop('eligible_stream_ids', [])
        eligible_streams = []
        for stream_id in stream_ids:
            if not PydanticObjectId.is_valid(stream_id):
                raise HTTPException(status_code=400, detail=f"Invalid stream ID: {stream_id}")
            
            stream = await AcademicStream.get(PydanticObjectId(stream_id))
            if not stream:
                raise HTTPException(status_code=404, detail=f"Academic stream not found: {stream_id}")
            
            eligible_streams.append(stream)
        
        scholarship_dict['eligible_streams'] = eligible_streams
        
        scholarship = Scholarship(**scholarship_dict)
        await scholarship.create()
        
        response_dict = scholarship.dict()
        response_dict["id"] = str(scholarship.id)
        response_dict["college_id"] = str(scholarship.college.id)
        response_dict["eligible_stream_ids"] = [str(stream.id) for stream in scholarship.eligible_streams] if scholarship.eligible_streams else []
        
        return ScholarshipResponse(**response_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating scholarship: {str(e)}")

@router.get("/", response_model=ScholarshipListResponse)
async def get_scholarships(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search by title or description"),
    college_id: Optional[str] = Query(None, description="Filter by college ID"),
    scholarship_type: Optional[str] = Query(None, description="Filter by scholarship type"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum scholarship amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum scholarship amount")
):
    """Get list of scholarships with pagination and filters"""
    try:
        skip = (page - 1) * size
        
        # Build query filters
        query_filter = {}
        if search:
            query_filter["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        if college_id:
            if not PydanticObjectId.is_valid(college_id):
                raise HTTPException(status_code=400, detail="Invalid college ID")
            query_filter["college"] = PydanticObjectId(college_id)
        if scholarship_type:
            query_filter["scholarship_type"] = scholarship_type
        if active is not None:
            query_filter["active"] = active
        if min_amount is not None:
            query_filter["amount"] = {"$gte": min_amount}
        if max_amount is not None:
            if "amount" in query_filter:
                query_filter["amount"]["$lte"] = max_amount
            else:
                query_filter["amount"] = {"$lte": max_amount}
        
        # Get total count
        total = await Scholarship.find(query_filter).count()
        
        # Get scholarships with pagination
        scholarships = await Scholarship.find(query_filter).skip(skip).limit(size).to_list()
        
        scholarship_responses = []
        for scholarship in scholarships:
            scholarship_dict = scholarship.dict()
            scholarship_dict["id"] = str(scholarship.id)
            scholarship_dict["college_id"] = str(scholarship.college.id)
            scholarship_dict["eligible_stream_ids"] = [str(stream.id) for stream in scholarship.eligible_streams] if scholarship.eligible_streams else []
            scholarship_responses.append(ScholarshipResponse(**scholarship_dict))
        
        return ScholarshipListResponse(
            scholarships=scholarship_responses,
            total=total,
            page=page,
            size=size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scholarships: {str(e)}")

@router.get("/{scholarship_id}", response_model=ScholarshipResponse)
async def get_scholarship(scholarship_id: str):
    """Get a specific scholarship by ID"""
    try:
        if not PydanticObjectId.is_valid(scholarship_id):
            raise HTTPException(status_code=400, detail="Invalid scholarship ID")
        
        scholarship = await Scholarship.get(PydanticObjectId(scholarship_id))
        if not scholarship:
            raise HTTPException(status_code=404, detail="Scholarship not found")
        
        scholarship_dict = scholarship.dict()
        scholarship_dict["id"] = str(scholarship.id)
        scholarship_dict["college_id"] = str(scholarship.college.id)
        scholarship_dict["eligible_stream_ids"] = [str(stream.id) for stream in scholarship.eligible_streams] if scholarship.eligible_streams else []
        
        return ScholarshipResponse(**scholarship_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scholarship: {str(e)}")

@router.put("/{scholarship_id}", response_model=ScholarshipResponse)
async def update_scholarship(scholarship_id: str, scholarship_data: ScholarshipUpdate):
    """Update a scholarship"""
    try:
        if not PydanticObjectId.is_valid(scholarship_id):
            raise HTTPException(status_code=400, detail="Invalid scholarship ID")
        
        scholarship = await Scholarship.get(PydanticObjectId(scholarship_id))
        if not scholarship:
            raise HTTPException(status_code=404, detail="Scholarship not found")
        
        # Update only provided fields
        update_data = scholarship_data.model_dump()
        
        # Handle college linkage if provided
        college_id = update_data.pop('college_id', None)
        if college_id:
            if not PydanticObjectId.is_valid(college_id):
                raise HTTPException(status_code=400, detail="Invalid college ID")
            
            college = await College.get(PydanticObjectId(college_id))
            if not college:
                raise HTTPException(status_code=404, detail="College not found")
            
            update_data['college'] = college
        
        # Handle eligible streams linkage if provided
        stream_ids = update_data.pop('eligible_stream_ids', None)
        if stream_ids is not None:
            eligible_streams = []
            for stream_id in stream_ids:
                if not PydanticObjectId.is_valid(stream_id):
                    raise HTTPException(status_code=400, detail=f"Invalid stream ID: {stream_id}")
                
                stream = await AcademicStream.get(PydanticObjectId(stream_id))
                if not stream:
                    raise HTTPException(status_code=404, detail=f"Academic stream not found: {stream_id}")
                
                eligible_streams.append(stream)
            
            update_data['eligible_streams'] = eligible_streams
        
        if update_data:
            await scholarship.set(update_data)
        
        scholarship_dict = scholarship.dict()
        scholarship_dict["id"] = str(scholarship.id)
        scholarship_dict["college_id"] = str(scholarship.college.id)
        scholarship_dict["eligible_stream_ids"] = [str(stream.id) for stream in scholarship.eligible_streams] if scholarship.eligible_streams else []
        
        return ScholarshipResponse(**scholarship_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating scholarship: {str(e)}")

@router.delete("/{scholarship_id}", status_code=204)
async def delete_scholarship(scholarship_id: str):
    """Delete a scholarship"""
    try:
        if not PydanticObjectId.is_valid(scholarship_id):
            raise HTTPException(status_code=400, detail="Invalid scholarship ID")
        
        scholarship = await Scholarship.get(PydanticObjectId(scholarship_id))
        if not scholarship:
            raise HTTPException(status_code=404, detail="Scholarship not found")
        
        await scholarship.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting scholarship: {str(e)}")

@router.get("/college/{college_id}", response_model=ScholarshipListResponse)
async def get_scholarships_by_college(
    college_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    active: Optional[bool] = Query(True, description="Filter by active status")
):
    """Get all scholarships for a specific college"""
    try:
        if not PydanticObjectId.is_valid(college_id):
            raise HTTPException(status_code=400, detail="Invalid college ID")
        
        # Check if college exists
        college = await College.get(PydanticObjectId(college_id))
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        
        skip = (page - 1) * size
        query_filter = {"college": PydanticObjectId(college_id)}
        if active is not None:
            query_filter["active"] = active
        
        # Get total count
        total = await Scholarship.find(query_filter).count()
        
        # Get scholarships with pagination
        scholarships = await Scholarship.find(query_filter).skip(skip).limit(size).to_list()
        
        scholarship_responses = []
        for scholarship in scholarships:
            scholarship_dict = scholarship.dict()
            scholarship_dict["id"] = str(scholarship.id)
            scholarship_dict["college_id"] = str(scholarship.college.id)
            scholarship_dict["eligible_stream_ids"] = [str(stream.id) for stream in scholarship.eligible_streams] if scholarship.eligible_streams else []
            scholarship_responses.append(ScholarshipResponse(**scholarship_dict))
        
        return ScholarshipListResponse(
            scholarships=scholarship_responses,
            total=total,
            page=page,
            size=size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching college scholarships: {str(e)}")

@router.post("/{scholarship_id}/toggle-status")
async def toggle_scholarship_status(scholarship_id: str):
    """Toggle scholarship active status"""
    try:
        if not PydanticObjectId.is_valid(scholarship_id):
            raise HTTPException(status_code=400, detail="Invalid scholarship ID")
        
        scholarship = await Scholarship.get(PydanticObjectId(scholarship_id))
        if not scholarship:
            raise HTTPException(status_code=404, detail="Scholarship not found")
        
        await scholarship.set({"active": not scholarship.active})
        
        return {"message": f"Scholarship status updated to {'active' if scholarship.active else 'inactive'}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling scholarship status: {str(e)}")