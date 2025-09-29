from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import date
from app.models.scholarship import Gender, Category, ScholarshipType

# Scholarship Schemas
class ScholarshipBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    amount: Optional[float] = Field(None, ge=0)
    amount_range: Optional[List[float]] = Field(None, min_items=2, max_items=2)
    benefit: Optional[str] = Field(None, max_length=200)
    eligible_genders: Optional[List[Gender]] = [Gender.ANY]
    eligible_categories: Optional[List[Category]] = [Category.ANY]
    scholarship_type: Optional[ScholarshipType] = None
    min_percentage: Optional[float] = Field(None, ge=0, le=100)
    min_cgpa: Optional[float] = Field(None, ge=0, le=10)
    max_family_income: Optional[float] = Field(None, ge=0)
    eligibility_criteria: Optional[str] = Field(None, max_length=500)
    application_process: Optional[str] = Field(None, max_length=500)
    deadline: Optional[date] = None
    active: bool = True
    url: Optional[HttpUrl] = None

class ScholarshipCreate(ScholarshipBase):
    college_id: str
    eligible_stream_ids: Optional[List[str]] = []

class ScholarshipUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    amount: Optional[float] = Field(None, ge=0)
    amount_range: Optional[List[float]] = Field(None, min_items=2, max_items=2)
    benefit: Optional[str] = Field(None, max_length=200)
    eligible_genders: Optional[List[Gender]] = None
    eligible_categories: Optional[List[Category]] = None
    scholarship_type: Optional[ScholarshipType] = None
    min_percentage: Optional[float] = Field(None, ge=0, le=100)
    min_cgpa: Optional[float] = Field(None, ge=0, le=10)
    max_family_income: Optional[float] = Field(None, ge=0)
    eligible_stream_ids: Optional[List[str]] = None
    eligibility_criteria: Optional[str] = Field(None, max_length=500)
    application_process: Optional[str] = Field(None, max_length=500)
    deadline: Optional[date] = None
    active: Optional[bool] = None
    url: Optional[HttpUrl] = None
    college_id: Optional[str] = None

class ScholarshipResponse(ScholarshipBase):
    id: str = Field(alias="_id")
    college_id: str
    eligible_stream_ids: Optional[List[str]] = []
    created_at: date
    updated_at: date
    
    class Config:
        populate_by_name = True

class ScholarshipListResponse(BaseModel):
    scholarships: List[ScholarshipResponse]
    total: int
    page: int
    size: int