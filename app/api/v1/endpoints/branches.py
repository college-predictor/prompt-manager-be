from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from beanie import PydanticObjectId
from app.models.junction import CollegeJunction
from app.models.college import College
from app.models.academics import AcademicStream
from app.models.faculty import Faculty
from app.schemas.junction import (
    CollegeJunctionCreate,
    CollegeJunctionUpdate,
    CollegeJunctionResponse,
    CollegeJunctionListResponse
)

router = APIRouter()

@router.post("/", response_model=CollegeJunctionResponse, status_code=201)
async def create_college_branch(branch_data: CollegeJunctionCreate):
    """Create a new college branch (college-stream junction)"""
    try:
        branch_dict = branch_data.model_dump()
        
        # Handle college linkage
        college_id = branch_dict.pop('college_id')
        if not PydanticObjectId.is_valid(college_id):
            raise HTTPException(status_code=400, detail="Invalid college ID")
        
        college = await College.get(PydanticObjectId(college_id))
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        
        branch_dict['college'] = college
        
        # Handle academic stream linkage
        stream_id = branch_dict.pop('academic_stream_id')
        if not PydanticObjectId.is_valid(stream_id):
            raise HTTPException(status_code=400, detail="Invalid academic stream ID")
        
        stream = await AcademicStream.get(PydanticObjectId(stream_id))
        if not stream:
            raise HTTPException(status_code=404, detail="Academic stream not found")
        
        branch_dict['academic_stream'] = stream
        
        # Handle faculty linkage if provided
        faculty_ids = branch_dict.pop('faculty_ids', [])
        faculties = []
        for faculty_id in faculty_ids:
            if not PydanticObjectId.is_valid(faculty_id):
                raise HTTPException(status_code=400, detail=f"Invalid faculty ID: {faculty_id}")
            
            faculty = await Faculty.get(PydanticObjectId(faculty_id))
            if not faculty:
                raise HTTPException(status_code=404, detail=f"Faculty not found: {faculty_id}")
            
            faculties.append(faculty)
        
        branch_dict['faculties'] = faculties
        
        # Check for existing college-stream combination
        existing_branch = await CollegeJunction.find_one({
            "college": college.id,
            "academic_stream": stream.id,
            "academic_level": branch_dict["academic_level"],
            "degree_type": branch_dict["degree_type"]
        })
        
        if existing_branch:
            raise HTTPException(
                status_code=400, 
                detail="A branch with this college, stream, academic level, and degree type already exists"
            )
        
        branch = CollegeJunction(**branch_dict)
        await branch.create()
        
        response_dict = branch.dict()
        response_dict["id"] = str(branch.id)
        response_dict["college_id"] = str(branch.college.id)
        response_dict["academic_stream_id"] = str(branch.academic_stream.id)
        response_dict["faculty_ids"] = [str(faculty.id) for faculty in branch.faculties] if branch.faculties else []
        
        return CollegeJunctionResponse(**response_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating college branch: {str(e)}")

@router.get("/", response_model=CollegeJunctionListResponse)
async def get_college_branches(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    college_id: Optional[str] = Query(None, description="Filter by college ID"),
    stream_id: Optional[str] = Query(None, description="Filter by academic stream ID"),
    academic_level: Optional[str] = Query(None, description="Filter by academic level"),
    degree_type: Optional[str] = Query(None, description="Filter by degree type"),
    teaching_mode: Optional[str] = Query(None, description="Filter by teaching mode"),
    min_fees: Optional[float] = Query(None, ge=0, description="Minimum fees"),
    max_fees: Optional[float] = Query(None, ge=0, description="Maximum fees")
):
    """Get list of college branches with pagination and filters"""
    try:
        skip = (page - 1) * size
        
        # Build query filters
        query_filter = {}
        if college_id:
            if not PydanticObjectId.is_valid(college_id):
                raise HTTPException(status_code=400, detail="Invalid college ID")
            query_filter["college"] = PydanticObjectId(college_id)
        if stream_id:
            if not PydanticObjectId.is_valid(stream_id):
                raise HTTPException(status_code=400, detail="Invalid stream ID")
            query_filter["academic_stream"] = PydanticObjectId(stream_id)
        if academic_level:
            query_filter["academic_level"] = academic_level
        if degree_type:
            query_filter["degree_type"] = degree_type
        if teaching_mode:
            query_filter["teaching_mode"] = teaching_mode
        if min_fees is not None:
            query_filter["fees"] = {"$gte": min_fees}
        if max_fees is not None:
            if "fees" in query_filter:
                query_filter["fees"]["$lte"] = max_fees
            else:
                query_filter["fees"] = {"$lte": max_fees}
        
        # Get total count
        total = await CollegeJunction.find(query_filter).count()
        
        # Get branches with pagination
        branches = await CollegeJunction.find(query_filter).skip(skip).limit(size).to_list()
        
        branch_responses = []
        for branch in branches:
            branch_dict = branch.dict()
            branch_dict["id"] = str(branch.id)
            branch_dict["college_id"] = str(branch.college.id)
            branch_dict["academic_stream_id"] = str(branch.academic_stream.id)
            branch_dict["faculty_ids"] = [str(faculty.id) for faculty in branch.faculties] if branch.faculties else []
            branch_responses.append(CollegeJunctionResponse(**branch_dict))
        
        return CollegeJunctionListResponse(
            branches=branch_responses,
            total=total,
            page=page,
            size=size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching college branches: {str(e)}")

@router.get("/{branch_id}", response_model=CollegeJunctionResponse)
async def get_college_branch(branch_id: str):
    """Get a specific college branch by ID"""
    try:
        if not PydanticObjectId.is_valid(branch_id):
            raise HTTPException(status_code=400, detail="Invalid branch ID")
        
        branch = await CollegeJunction.get(PydanticObjectId(branch_id))
        if not branch:
            raise HTTPException(status_code=404, detail="College branch not found")
        
        branch_dict = branch.dict()
        branch_dict["id"] = str(branch.id)
        branch_dict["college_id"] = str(branch.college.id)
        branch_dict["academic_stream_id"] = str(branch.academic_stream.id)
        branch_dict["faculty_ids"] = [str(faculty.id) for faculty in branch.faculties] if branch.faculties else []
        
        return CollegeJunctionResponse(**branch_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching college branch: {str(e)}")

@router.put("/{branch_id}", response_model=CollegeJunctionResponse)
async def update_college_branch(branch_id: str, branch_data: CollegeJunctionUpdate):
    """Update a college branch"""
    try:
        if not PydanticObjectId.is_valid(branch_id):
            raise HTTPException(status_code=400, detail="Invalid branch ID")
        
        branch = await CollegeJunction.get(PydanticObjectId(branch_id))
        if not branch:
            raise HTTPException(status_code=404, detail="College branch not found")
        
        # Update only provided fields
        update_data = branch_data.model_dump()
        
        # Handle college linkage if provided
        college_id = update_data.pop('college_id', None)
        if college_id:
            if not PydanticObjectId.is_valid(college_id):
                raise HTTPException(status_code=400, detail="Invalid college ID")
            
            college = await College.get(PydanticObjectId(college_id))
            if not college:
                raise HTTPException(status_code=404, detail="College not found")
            
            update_data['college'] = college
        
        # Handle academic stream linkage if provided
        stream_id = update_data.pop('academic_stream_id', None)
        if stream_id:
            if not PydanticObjectId.is_valid(stream_id):
                raise HTTPException(status_code=400, detail="Invalid academic stream ID")
            
            stream = await AcademicStream.get(PydanticObjectId(stream_id))
            if not stream:
                raise HTTPException(status_code=404, detail="Academic stream not found")
            
            update_data['academic_stream'] = stream
        
        # Handle faculty linkage if provided
        faculty_ids = update_data.pop('faculty_ids', None)
        if faculty_ids is not None:
            faculties = []
            for faculty_id in faculty_ids:
                if not PydanticObjectId.is_valid(faculty_id):
                    raise HTTPException(status_code=400, detail=f"Invalid faculty ID: {faculty_id}")
                
                faculty = await Faculty.get(PydanticObjectId(faculty_id))
                if not faculty:
                    raise HTTPException(status_code=404, detail=f"Faculty not found: {faculty_id}")
                
                faculties.append(faculty)
            
            update_data['faculties'] = faculties
        
        if update_data:
            await branch.set(update_data)
        
        branch_dict = branch.dict()
        branch_dict["id"] = str(branch.id)
        branch_dict["college_id"] = str(branch.college.id)
        branch_dict["academic_stream_id"] = str(branch.academic_stream.id)
        branch_dict["faculty_ids"] = [str(faculty.id) for faculty in branch.faculties] if branch.faculties else []
        
        return CollegeJunctionResponse(**branch_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating college branch: {str(e)}")

@router.delete("/{branch_id}", status_code=204)
async def delete_college_branch(branch_id: str):
    """Delete a college branch"""
    try:
        if not PydanticObjectId.is_valid(branch_id):
            raise HTTPException(status_code=400, detail="Invalid branch ID")
        
        branch = await CollegeJunction.get(PydanticObjectId(branch_id))
        if not branch:
            raise HTTPException(status_code=404, detail="College branch not found")
        
        await branch.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting college branch: {str(e)}")

@router.get("/college/{college_id}", response_model=CollegeJunctionListResponse)
async def get_branches_by_college(
    college_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size")
):
    """Get all branches for a specific college"""
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
        total = await CollegeJunction.find(query_filter).count()
        
        # Get branches with pagination
        branches = await CollegeJunction.find(query_filter).skip(skip).limit(size).to_list()
        
        branch_responses = []
        for branch in branches:
            branch_dict = branch.dict()
            branch_dict["id"] = str(branch.id)
            branch_dict["college_id"] = str(branch.college.id)
            branch_dict["academic_stream_id"] = str(branch.academic_stream.id)
            branch_dict["faculty_ids"] = [str(faculty.id) for faculty in branch.faculties] if branch.faculties else []
            branch_responses.append(CollegeJunctionResponse(**branch_dict))
        
        return CollegeJunctionListResponse(
            branches=branch_responses,
            total=total,
            page=page,
            size=size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching college branches: {str(e)}")

@router.get("/stream/{stream_id}", response_model=CollegeJunctionListResponse)
async def get_branches_by_stream(
    stream_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size")
):
    """Get all branches for a specific academic stream"""
    try:
        if not PydanticObjectId.is_valid(stream_id):
            raise HTTPException(status_code=400, detail="Invalid stream ID")
        
        # Check if stream exists
        stream = await AcademicStream.get(PydanticObjectId(stream_id))
        if not stream:
            raise HTTPException(status_code=404, detail="Academic stream not found")
        
        skip = (page - 1) * size
        query_filter = {"academic_stream": PydanticObjectId(stream_id)}
        
        # Get total count
        total = await CollegeJunction.find(query_filter).count()
        
        # Get branches with pagination
        branches = await CollegeJunction.find(query_filter).skip(skip).limit(size).to_list()
        
        branch_responses = []
        for branch in branches:
            branch_dict = branch.dict()
            branch_dict["id"] = str(branch.id)
            branch_dict["college_id"] = str(branch.college.id)
            branch_dict["academic_stream_id"] = str(branch.academic_stream.id)
            branch_dict["faculty_ids"] = [str(faculty.id) for faculty in branch.faculties] if branch.faculties else []
            branch_responses.append(CollegeJunctionResponse(**branch_dict))
        
        return CollegeJunctionListResponse(
            branches=branch_responses,
            total=total,
            page=page,
            size=size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stream branches: {str(e)}")