from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from beanie import PydanticObjectId
from app.models.faculty import Faculty
from app.models.college import College
from app.schemas.faculty import (
    FacultyCreate, 
    FacultyUpdate, 
    FacultyResponse, 
    FacultyListResponse
)

router = APIRouter()

@router.post("/", response_model=FacultyResponse, status_code=201)
async def create_faculty(faculty_data: FacultyCreate):
    """Create a new faculty member"""
    try:
        faculty_dict = faculty_data.model_dump()
        
        # Handle college linkage if provided
        college_id = faculty_dict.pop('college_id', None)
        if college_id:
            if not PydanticObjectId.is_valid(college_id):
                raise HTTPException(status_code=400, detail="Invalid college ID")
            
            college = await College.get(PydanticObjectId(college_id))
            if not college:
                raise HTTPException(status_code=404, detail="College not found")
            
            faculty_dict['college'] = college
        
        faculty = Faculty(**faculty_dict)
        await faculty.create()
        
        response_dict = faculty.dict()
        response_dict["id"] = str(faculty.id)
        response_dict["college_id"] = str(faculty.college.id) if faculty.college else None
        
        return FacultyResponse(**response_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating faculty: {str(e)}")

@router.get("/", response_model=FacultyListResponse)
async def get_faculties(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search by name"),
    college_id: Optional[str] = Query(None, description="Filter by college ID"),
    designation: Optional[str] = Query(None, description="Filter by designation"),
    department: Optional[str] = Query(None, description="Filter by department")
):
    """Get list of faculty members with pagination and filters"""
    try:
        skip = (page - 1) * size
        
        # Build query filters
        query_filter = {}
        if search:
            query_filter["$or"] = [
                {"first_name": {"$regex": search, "$options": "i"}},
                {"last_name": {"$regex": search, "$options": "i"}},
                {"title": {"$regex": search, "$options": "i"}}
            ]
        if college_id:
            if not PydanticObjectId.is_valid(college_id):
                raise HTTPException(status_code=400, detail="Invalid college ID")
            query_filter["college"] = PydanticObjectId(college_id)
        if designation:
            query_filter["designation"] = {"$regex": designation, "$options": "i"}
        if department:
            query_filter["departments.name"] = {"$regex": department, "$options": "i"}
        
        # Get total count
        total = await Faculty.find(query_filter).count()
        
        # Get faculties with pagination
        faculties = await Faculty.find(query_filter).skip(skip).limit(size).to_list()
        
        faculty_responses = []
        for faculty in faculties:
            faculty_dict = faculty.dict()
            faculty_dict["id"] = str(faculty.id)
            faculty_dict["college_id"] = str(faculty.college.id) if faculty.college else None
            faculty_responses.append(FacultyResponse(**faculty_dict))
        
        return FacultyListResponse(
            faculties=faculty_responses,
            total=total,
            page=page,
            size=size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching faculties: {str(e)}")

@router.get("/{faculty_id}", response_model=FacultyResponse)
async def get_faculty(faculty_id: str):
    """Get a specific faculty member by ID"""
    try:
        if not PydanticObjectId.is_valid(faculty_id):
            raise HTTPException(status_code=400, detail="Invalid faculty ID")
        
        faculty = await Faculty.get(PydanticObjectId(faculty_id))
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")
        
        faculty_dict = faculty.dict()
        faculty_dict["id"] = str(faculty.id)
        faculty_dict["college_id"] = str(faculty.college.id) if faculty.college else None
        
        return FacultyResponse(**faculty_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching faculty: {str(e)}")

@router.put("/{faculty_id}", response_model=FacultyResponse)
async def update_faculty(faculty_id: str, faculty_data: FacultyUpdate):
    """Update a faculty member"""
    try:
        if not PydanticObjectId.is_valid(faculty_id):
            raise HTTPException(status_code=400, detail="Invalid faculty ID")
        
        faculty = await Faculty.get(PydanticObjectId(faculty_id))
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")
        
        # Update only provided fields
        update_data = faculty_data.model_dump()
        
        # Handle college linkage if provided
        college_id = update_data.pop('college_id', None)
        if college_id:
            if not PydanticObjectId.is_valid(college_id):
                raise HTTPException(status_code=400, detail="Invalid college ID")
            
            college = await College.get(PydanticObjectId(college_id))
            if not college:
                raise HTTPException(status_code=404, detail="College not found")
            
            update_data['college'] = college
        
        if update_data:
            await faculty.set(update_data)
        
        faculty_dict = faculty.dict()
        faculty_dict["id"] = str(faculty.id)
        faculty_dict["college_id"] = str(faculty.college.id) if faculty.college else None
        
        return FacultyResponse(**faculty_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating faculty: {str(e)}")

@router.delete("/{faculty_id}", status_code=204)
async def delete_faculty(faculty_id: str):
    """Delete a faculty member"""
    try:
        if not PydanticObjectId.is_valid(faculty_id):
            raise HTTPException(status_code=400, detail="Invalid faculty ID")
        
        faculty = await Faculty.get(PydanticObjectId(faculty_id))
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")
        
        await faculty.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting faculty: {str(e)}")

@router.get("/college/{college_id}", response_model=FacultyListResponse)
async def get_faculties_by_college(
    college_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size")
):
    """Get all faculty members for a specific college"""
    try:
        if not PydanticObjectId.is_valid(college_id):
            raise HTTPException(status_code=400, detail="Invalid college ID")
        
        # Check if college exists
        college = await College.get(PydanticObjectId(college_id))
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        
        skip = (page - 1) * size
        query_filter = {"college": PydanticObjectId(college_id)}
        
        # Get total count
        total = await Faculty.find(query_filter).count()
        
        # Get faculties with pagination
        faculties = await Faculty.find(query_filter).skip(skip).limit(size).to_list()
        
        faculty_responses = []
        for faculty in faculties:
            faculty_dict = faculty.dict()
            faculty_dict["id"] = str(faculty.id)
            faculty_dict["college_id"] = str(faculty.college.id) if faculty.college else None
            faculty_responses.append(FacultyResponse(**faculty_dict))
        
        return FacultyListResponse(
            faculties=faculty_responses,
            total=total,
            page=page,
            size=size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching college faculties: {str(e)}")