from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, List
from app.models.college import CollegeType, CollegeCategory, CollegeSubCategory, Address, Contact, CollegeRanking

# Address Schemas
class AddressCreate(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    country: str
    pincode: Optional[str] = None

class AddressResponse(AddressCreate):
    pass

# Contact Schemas
class ContactCreate(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None

class ContactResponse(ContactCreate):
    pass

# College Ranking Schemas
class CollegeRankingCreate(BaseModel):
    organisation: str
    rank: int
    year: int

class CollegeRankingResponse(CollegeRankingCreate):
    pass

# College Schemas
class CollegeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    alias: Optional[str] = None
    established_year: Optional[int] = Field(None, ge=1800, le=2030)
    type: Optional[CollegeType] = None
    category: Optional[CollegeCategory] = None
    sub_category: Optional[CollegeSubCategory] = None
    website: Optional[HttpUrl] = None
    tags: Optional[List[str]] = []

class CollegeCreate(CollegeBase):
    address: Optional[AddressCreate] = None
    contact: Optional[ContactCreate] = None
    rankings: Optional[List[CollegeRankingCreate]] = []
    images: Optional[List[HttpUrl]] = []

class CollegeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    alias: Optional[str] = None
    established_year: Optional[int] = Field(None, ge=1800, le=2030)
    type: Optional[CollegeType] = None
    category: Optional[CollegeCategory] = None
    sub_category: Optional[CollegeSubCategory] = None
    website: Optional[HttpUrl] = None
    address: Optional[AddressCreate] = None
    contact: Optional[ContactCreate] = None
    rankings: Optional[List[CollegeRankingCreate]] = []
    images: Optional[List[HttpUrl]] = []
    tags: Optional[List[str]] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)

class CollegeResponse(CollegeBase):
    id: str = Field(alias="_id")
    address: Optional[AddressResponse] = None
    contact: Optional[ContactResponse] = None
    rankings: Optional[List[CollegeRankingResponse]] = []
    images: Optional[List[HttpUrl]] = []
    rating: Optional[float] = None
    review_count: Optional[int] = None
    
    class Config:
        populate_by_name = True

class CollegeListResponse(BaseModel):
    colleges: List[CollegeResponse]
    total: int
    page: int
    size: int