from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, List
from app.models.faculty import Department

# Department Schemas
class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: Optional[str] = Field(None, max_length=10)

class DepartmentResponse(DepartmentCreate):
    pass

# Faculty Schemas
class FacultyBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = Field(None, max_length=20)  # Prof, Dr, Asst Prof
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=15)
    designation: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    education: Optional[str] = Field(None, max_length=200)
    experience_years: Optional[int] = Field(None, ge=0, le=60)

class FacultyCreate(FacultyBase):
    departments: Optional[List[DepartmentCreate]] = []
    research_interests: Optional[List[str]] = []
    achievements: Optional[List[str]] = []
    publications: Optional[List[str]] = []
    portfolio_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    photo_url: Optional[HttpUrl] = None
    college_id: Optional[str] = None

class FacultyUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=15)
    designation: Optional[str] = Field(None, max_length=100)
    departments: Optional[List[DepartmentCreate]] = None
    bio: Optional[str] = Field(None, max_length=1000)
    research_interests: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    publications: Optional[List[str]] = None
    portfolio_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    photo_url: Optional[HttpUrl] = None
    education: Optional[str] = Field(None, max_length=200)
    experience_years: Optional[int] = Field(None, ge=0, le=60)
    college_id: Optional[str] = None

class FacultyResponse(FacultyBase):
    id: str = Field(alias="_id")
    departments: Optional[List[DepartmentResponse]] = []
    research_interests: Optional[List[str]] = []
    achievements: Optional[List[str]] = []
    publications: Optional[List[str]] = []
    portfolio_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    photo_url: Optional[HttpUrl] = None
    college_id: Optional[str] = None
    
    class Config:
        populate_by_name = True

class FacultyListResponse(BaseModel):
    faculties: List[FacultyResponse]
    total: int
    page: int
    size: int