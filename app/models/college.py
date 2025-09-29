from typing import List, Optional
from beanie import Document
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from enum import Enum

class Address(BaseModel):
    line1: str
    line2: Optional[str]
    city: str
    state: str
    country: str
    pincode: Optional[str]

class Contact(BaseModel):
    phone: Optional[str]
    email: Optional[EmailStr]
    website: Optional[HttpUrl]

class CollegeType(str, Enum):
    PRIVATE = "Private"
    PUBLIC = "Public"
    GOVERNMENT = "Government"

class CollegeCategory(str, Enum):
    ENGINEERING = "Engineering"
    MEDICAL = "Medical"
    ARTS = "Arts"
    SCIENCE = "Science"
    COMMERCE = "Commerce"
    LAW = "Law"
    MANAGEMENT = "Management"
    MULTIDISCIPLINARY = "Multidisciplinary"
    OTHER = "Other"

class CollegeSubCategory(str, Enum):
    IIT = "IIT"
    NIT = "NIT"
    IIIT = "IIIT"
    GFTI = "GFTI"
    AIIMS = "AIIMS"

class CollegeRanking(BaseModel):
    organisation: str
    rank: int
    year: int

class College(Document):
    name: str
    description: Optional[str]
    alias: Optional[str] = None # IITM, NITP
    address: Optional[Address]
    contact: Optional[Contact]
    established_year: Optional[int]
    type: Optional[CollegeType]           # Private, Public, Government
    category: Optional[CollegeCategory]  # Engineering, Medical, Arts, Science, Commerce, Law, Management, Multidisciplinary
    sub_category: Optional[CollegeSubCategory]  # IIT, NIT, IIIT, GFTI, AIIMS
    website: Optional[HttpUrl]
    rankings: Optional[List[CollegeRanking]] = []
    images: Optional[List[HttpUrl]] = []

    tags: Optional[List[str]] = []
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = 0

    class Settings:
        name = "colleges"
        # define custom indexes in app init if desired
