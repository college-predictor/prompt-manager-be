from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from beanie import PydanticObjectId
from app.models.academics import AcademicStream, AcademicCourse
from app.models.faculty import Faculty
from app.schemas.academics import (
    AcademicStreamCreate,
    AcademicStreamUpdate,
    AcademicStreamResponse,
    AcademicStreamListResponse,
    AcademicCourseCreate,
    AcademicCourseUpdate,
    AcademicCourseResponse,
    AcademicCourseListResponse
)

router = APIRouter()

# Academic Stream endpoints
@router.post("/streams/", response_model=AcademicStreamResponse, status_code=201)
async def create_academic_stream(stream_data: AcademicStreamCreate):
    """Create a new academic stream"""
    try:
        stream_dict = stream_data.model_dump()
        stream = AcademicStream(**stream_dict)
        await stream.create()
        
        response_dict = stream.dict()
        response_dict["id"] = str(stream.id)
        return AcademicStreamResponse(**response_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating academic stream: {str(e)}")

@router.get("/streams/", response_model=AcademicStreamListResponse)
async def get_academic_streams(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search by title or code")
):
    """Get list of academic streams with pagination and filters"""
    try:
        skip = (page - 1) * size
        
        # Build query filters
        query_filter = {}
        if search:
            query_filter["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"code": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total = await AcademicStream.find(query_filter).count()
        
        # Get streams with pagination
        streams = await AcademicStream.find(query_filter).skip(skip).limit(size).to_list()
        
        stream_responses = []
        for stream in streams:
            stream_dict = stream.dict()
            stream_dict["id"] = str(stream.id)
            stream_responses.append(AcademicStreamResponse(**stream_dict))
        
        return AcademicStreamListResponse(
            streams=stream_responses,
            total=total,
            page=page,
            size=size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching academic streams: {str(e)}")

@router.get("/streams/{stream_id}", response_model=AcademicStreamResponse)
async def get_academic_stream(stream_id: str):
    """Get a specific academic stream by ID"""
    try:
        if not PydanticObjectId.is_valid(stream_id):
            raise HTTPException(status_code=400, detail="Invalid stream ID")
        
        stream = await AcademicStream.get(PydanticObjectId(stream_id))
        if not stream:
            raise HTTPException(status_code=404, detail="Academic stream not found")
        
        stream_dict = stream.dict()
        stream_dict["id"] = str(stream.id)
        return AcademicStreamResponse(**stream_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching academic stream: {str(e)}")

@router.put("/streams/{stream_id}", response_model=AcademicStreamResponse)
async def update_academic_stream(stream_id: str, stream_data: AcademicStreamUpdate):
    """Update an academic stream"""
    try:
        if not PydanticObjectId.is_valid(stream_id):
            raise HTTPException(status_code=400, detail="Invalid stream ID")
        
        stream = await AcademicStream.get(PydanticObjectId(stream_id))
        if not stream:
            raise HTTPException(status_code=404, detail="Academic stream not found")
        
        # Update only provided fields
        update_data = stream_data.model_dump()
        if update_data:
            await stream.set(update_data)
        
        stream_dict = stream.dict()
        stream_dict["id"] = str(stream.id)
        return AcademicStreamResponse(**stream_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating academic stream: {str(e)}")

@router.delete("/streams/{stream_id}", status_code=204)
async def delete_academic_stream(stream_id: str):
    """Delete an academic stream"""
    try:
        if not PydanticObjectId.is_valid(stream_id):
            raise HTTPException(status_code=400, detail="Invalid stream ID")
        
        stream = await AcademicStream.get(PydanticObjectId(stream_id))
        if not stream:
            raise HTTPException(status_code=404, detail="Academic stream not found")
        
        await stream.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting academic stream: {str(e)}")

# Academic Course endpoints
@router.post("/courses/", response_model=AcademicCourseResponse, status_code=201)
async def create_academic_course(course_data: AcademicCourseCreate):
    """Create a new academic course"""
    try:
        course_dict = course_data.model_dump()
        
        # Handle academic stream linkage
        stream_id = course_dict.pop('academic_stream_id')
        if not PydanticObjectId.is_valid(stream_id):
            raise HTTPException(status_code=400, detail="Invalid academic stream ID")
        
        stream = await AcademicStream.get(PydanticObjectId(stream_id))
        if not stream:
            raise HTTPException(status_code=404, detail="Academic stream not found")
        
        course_dict['academic_stream'] = stream
        
        # Handle faculty linkage if provided
        faculty_id = course_dict.pop('faculty_id', None)
        if faculty_id:
            if not PydanticObjectId.is_valid(faculty_id):
                raise HTTPException(status_code=400, detail="Invalid faculty ID")
            
            faculty = await Faculty.get(PydanticObjectId(faculty_id))
            if not faculty:
                raise HTTPException(status_code=404, detail="Faculty not found")
            
            course_dict['faculty'] = faculty
        
        course = AcademicCourse(**course_dict)
        await course.create()
        
        response_dict = course.dict()
        response_dict["id"] = str(course.id)
        response_dict["academic_stream_id"] = str(course.academic_stream.id)
        response_dict["faculty_id"] = str(course.faculty.id) if course.faculty else None
        
        return AcademicCourseResponse(**response_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating academic course: {str(e)}")

@router.get("/courses/", response_model=AcademicCourseListResponse)
async def get_academic_courses(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search by title or course code"),
    stream_id: Optional[str] = Query(None, description="Filter by academic stream ID"),
    faculty_id: Optional[str] = Query(None, description="Filter by faculty ID"),
    course_level: Optional[str] = Query(None, description="Filter by course level"),
    semester: Optional[int] = Query(None, ge=1, le=12, description="Filter by semester")
):
    """Get list of academic courses with pagination and filters"""
    try:
        skip = (page - 1) * size
        
        # Build query filters
        query_filter = {}
        if search:
            query_filter["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"course_code": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        if stream_id:
            if not PydanticObjectId.is_valid(stream_id):
                raise HTTPException(status_code=400, detail="Invalid stream ID")
            query_filter["academic_stream"] = PydanticObjectId(stream_id)
        if faculty_id:
            if not PydanticObjectId.is_valid(faculty_id):
                raise HTTPException(status_code=400, detail="Invalid faculty ID")
            query_filter["faculty"] = PydanticObjectId(faculty_id)
        if course_level:
            query_filter["course_level"] = course_level
        if semester:
            query_filter["semester"] = semester
        
        # Get total count
        total = await AcademicCourse.find(query_filter).count()
        
        # Get courses with pagination
        courses = await AcademicCourse.find(query_filter).skip(skip).limit(size).to_list()
        
        course_responses = []
        for course in courses:
            course_dict = course.dict()
            course_dict["id"] = str(course.id)
            course_dict["academic_stream_id"] = str(course.academic_stream.id)
            course_dict["faculty_id"] = str(course.faculty.id) if course.faculty else None
            course_responses.append(AcademicCourseResponse(**course_dict))
        
        return AcademicCourseListResponse(
            courses=course_responses,
            total=total,
            page=page,
            size=size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching academic courses: {str(e)}")

@router.get("/courses/{course_id}", response_model=AcademicCourseResponse)
async def get_academic_course(course_id: str):
    """Get a specific academic course by ID"""
    try:
        if not PydanticObjectId.is_valid(course_id):
            raise HTTPException(status_code=400, detail="Invalid course ID")
        
        course = await AcademicCourse.get(PydanticObjectId(course_id))
        if not course:
            raise HTTPException(status_code=404, detail="Academic course not found")
        
        course_dict = course.dict()
        course_dict["id"] = str(course.id)
        course_dict["academic_stream_id"] = str(course.academic_stream.id)
        course_dict["faculty_id"] = str(course.faculty.id) if course.faculty else None
        
        return AcademicCourseResponse(**course_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching academic course: {str(e)}")

@router.put("/courses/{course_id}", response_model=AcademicCourseResponse)
async def update_academic_course(course_id: str, course_data: AcademicCourseUpdate):
    """Update an academic course"""
    try:
        if not PydanticObjectId.is_valid(course_id):
            raise HTTPException(status_code=400, detail="Invalid course ID")
        
        course = await AcademicCourse.get(PydanticObjectId(course_id))
        if not course:
            raise HTTPException(status_code=404, detail="Academic course not found")
        
        # Update only provided fields
        update_data = course_data.model_dump()
        
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
        faculty_id = update_data.pop('faculty_id', None)
        if faculty_id:
            if not PydanticObjectId.is_valid(faculty_id):
                raise HTTPException(status_code=400, detail="Invalid faculty ID")
            
            faculty = await Faculty.get(PydanticObjectId(faculty_id))
            if not faculty:
                raise HTTPException(status_code=404, detail="Faculty not found")
            
            update_data['faculty'] = faculty
        
        if update_data:
            await course.set(update_data)
        
        course_dict = course.dict()
        course_dict["id"] = str(course.id)
        course_dict["academic_stream_id"] = str(course.academic_stream.id)
        course_dict["faculty_id"] = str(course.faculty.id) if course.faculty else None
        
        return AcademicCourseResponse(**course_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating academic course: {str(e)}")

@router.delete("/courses/{course_id}", status_code=204)
async def delete_academic_course(course_id: str):
    """Delete an academic course"""
    try:
        if not PydanticObjectId.is_valid(course_id):
            raise HTTPException(status_code=400, detail="Invalid course ID")
        
        course = await AcademicCourse.get(PydanticObjectId(course_id))
        if not course:
            raise HTTPException(status_code=404, detail="Academic course not found")
        
        await course.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting academic course: {str(e)}")