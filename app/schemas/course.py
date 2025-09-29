from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.academics import CourseLevel, CourseStatus, Lesson

# Course Schemas
class CourseBase(BaseModel):
    title: str
    description: str
    category: str
    subcategory: Optional[str] = None
    level: CourseLevel
    price: float = 0.0
    discount_price: Optional[float] = None
    tags: List[str] = []
    requirements: List[str] = []
    what_you_learn: List[str] = []

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    level: Optional[CourseLevel] = None
    status: Optional[CourseStatus] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    thumbnail: Optional[str] = None
    preview_video: Optional[str] = None
    tags: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    what_you_learn: Optional[List[str]] = None

class CourseResponse(CourseBase):
    id: str = Field(alias="_id")
    instructor_id: str
    instructor_name: Optional[str] = None
    status: CourseStatus
    thumbnail: Optional[str] = None
    preview_video: Optional[str] = None
    duration: Optional[int] = None
    lessons: List[Lesson] = []
    enrolled_students: List[str] = []
    rating: float
    review_count: int
    
    class Config:
        populate_by_name = True

# Lesson Schemas
class LessonCreate(BaseModel):
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = None
    order: int
    materials: List[str] = []

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = None
    order: Optional[int] = None
    materials: Optional[List[str]] = None

# Enrollment Schema
class EnrollmentRequest(BaseModel):
    course_id: str