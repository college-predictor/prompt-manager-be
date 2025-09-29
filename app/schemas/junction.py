from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.junction import AcademicLevel, DegreeType, TeachingMode, HostelFacility

# Hostel Facility Schemas
class HostelFacilityCreate(BaseModel):
    available: bool
    capacity: Optional[int] = Field(None, ge=1)
    fee_per_semester: Optional[float] = Field(None, ge=0)
    images: Optional[List[str]] = []
    amenities: Optional[List[str]] = []
    description: Optional[str] = Field(None, max_length=500)
    reviews: Optional[List[str]] = []

class HostelFacilityResponse(HostelFacilityCreate):
    pass

# College Junction (Branch) Schemas
class CollegeJunctionBase(BaseModel):
    academic_level: AcademicLevel
    degree_type: DegreeType
    teaching_mode: TeachingMode
    fees: float = Field(..., ge=0)

class CollegeJunctionCreate(CollegeJunctionBase):
    college_id: str
    academic_stream_id: str
    faculty_ids: Optional[List[str]] = []
    hostel_facility: Optional[HostelFacilityCreate] = None

class CollegeJunctionUpdate(BaseModel):
    academic_level: Optional[AcademicLevel] = None
    degree_type: Optional[DegreeType] = None
    teaching_mode: Optional[TeachingMode] = None
    fees: Optional[float] = Field(None, ge=0)
    college_id: Optional[str] = None
    academic_stream_id: Optional[str] = None
    faculty_ids: Optional[List[str]] = None
    hostel_facility: Optional[HostelFacilityCreate] = None

class CollegeJunctionResponse(CollegeJunctionBase):
    id: str = Field(alias="_id")
    college_id: str
    academic_stream_id: str
    faculty_ids: Optional[List[str]] = []
    hostel_facility: Optional[HostelFacilityResponse] = None
    
    class Config:
        populate_by_name = True

class CollegeJunctionListResponse(BaseModel):
    branches: List[CollegeJunctionResponse]
    total: int
    page: int
    size: int