from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.academics import CourseLevel

# Academic Stream Schemas
class AcademicStreamBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=10)
    description: Optional[str] = Field(None, max_length=1000)

class AcademicStreamCreate(AcademicStreamBase):
    pass

class AcademicStreamUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=10)
    description: Optional[str] = Field(None, max_length=1000)

class AcademicStreamResponse(AcademicStreamBase):
    id: str = Field(alias="_id")
    
    class Config:
        populate_by_name = True

# Academic Course Schemas
class AcademicCourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    course_code: Optional[str] = Field(None, max_length=20)
    description: str = Field(..., min_length=1, max_length=1000)
    course_level: Optional[CourseLevel] = None
    credits: Optional[int] = Field(None, ge=1, le=10)
    semester: Optional[int] = Field(None, ge=1, le=12)

class AcademicCourseCreate(AcademicCourseBase):
    academic_stream_id: str
    faculty_id: Optional[str] = None

class AcademicCourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    course_code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    course_level: Optional[CourseLevel] = None
    credits: Optional[int] = Field(None, ge=1, le=10)
    semester: Optional[int] = Field(None, ge=1, le=12)
    academic_stream_id: Optional[str] = None
    faculty_id: Optional[str] = None

class AcademicCourseResponse(AcademicCourseBase):
    id: str = Field(alias="_id")
    academic_stream_id: str
    faculty_id: Optional[str] = None
    
    class Config:
        populate_by_name = True

class AcademicStreamListResponse(BaseModel):
    streams: List[AcademicStreamResponse]
    total: int
    page: int
    size: int

class AcademicCourseListResponse(BaseModel):
    courses: List[AcademicCourseResponse]
    total: int
    page: int
    size: int