from typing import List, Optional
from pydantic import BaseModel, Field
from beanie import Document, Link
from app.models.college import College
from app.models.academics import AcademicStream
from app.models.faculty import Faculty
from enum import Enum

class AcademicLevel(str, Enum):
    UNDERGRADUATE = "Undergraduate"
    POSTGRADUATE = "Postgraduate"
    DIPLOMA = "Diploma"

class DegreeType(str, Enum):
    BACHELOR = "Bachelor"
    MASTER = "Master"
    PHD = "PhD"

class TeachingMode(str, Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"
    HYBRID = "Hybrid"

class HostelFacility(BaseModel):
    available: bool
    capacity: Optional[int]  # number of students it can accommodate
    fee_per_semester: Optional[float]  # in Rupees
    images: Optional[List[str]] = []
    amenities: Optional[List[str]] = []
    description: Optional[str]
    reviews: Optional[List[str]] = []

# Junction: CollegeAcademicStream (many-to-many + extra fields)
class CollegeJunction(Document):
    college: Link[College]
    academic_stream: Link[AcademicStream]
    academic_level: AcademicLevel
    degree_type: DegreeType 
    teaching_mode: TeachingMode
    fees: float
    faculties: Optional[List[Link[Faculty]]] = []
    hostel_facility: Optional[HostelFacility] = None

    class Settings:
        name = "college_junction"
        # Add indexes for better query performance
        indexes = [
            [("college", 1), ("academic_stream", 1)],  # Compound index for unique college-stream pairs
            "teaching_mode",
            "fees"
        ]