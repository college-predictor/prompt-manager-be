from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime


# Nested schemas for Create Request
class CoordinatesCreate(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None


class AddressCreate(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: str
    state: str
    country: str = "India"
    pincode: Optional[str] = None
    coordinates: Optional[CoordinatesCreate] = None


class ContactCreate(BaseModel):
    phone: Optional[List[str]] = []
    email: Optional[List[EmailStr]] = []
    website: Optional[HttpUrl] = None
    admission_helpline: Optional[str] = None


class RatingsCreate(BaseModel):
    overall: Optional[float] = Field(None, ge=0, le=5)
    academics: Optional[float] = Field(None, ge=0, le=5)
    infrastructure: Optional[float] = Field(None, ge=0, le=5)
    faculty: Optional[float] = Field(None, ge=0, le=5)
    placement: Optional[float] = Field(None, ge=0, le=5)
    hostel_life: Optional[float] = Field(None, ge=0, le=5)
    social_life: Optional[float] = Field(None, ge=0, le=5)
    total_reviews: int = 0


class CollegeRankingCreate(BaseModel):
    organisation: str
    rank: int
    year: int
    category: Optional[str] = None


class FeesCreate(BaseModel):
    tuition: Optional[str] = None
    hostel: Optional[str] = None
    other: Optional[str] = None
    total: Optional[str] = None
    currency: str = "INR"


class PlacementCreate(BaseModel):
    average_package: Optional[str] = None
    median_package: Optional[str] = None
    highest_package: Optional[str] = None
    placement_rate: Optional[float] = Field(None, ge=0, le=100)
    top_recruiters: Optional[List[str]] = []


class CoursesCreate(BaseModel):
    undergraduate: Optional[List[str]] = []
    postgraduate: Optional[List[str]] = []
    phd: Optional[List[str]] = []
    diploma: Optional[List[str]] = []
    certificate: Optional[List[str]] = []


class AcademicsCreate(BaseModel):
    courses: Optional[CoursesCreate] = None
    departments: Optional[List[str]] = []
    faculty_count: Optional[int] = None
    student_faculty_ratio: Optional[str] = None
    total_students: Optional[int] = None


class CampusCreate(BaseModel):
    area: Optional[str] = None
    buildings: Optional[int] = None
    labs: Optional[int] = None
    libraries: Optional[int] = None
    auditoriums: Optional[int] = None
    sports_facilities: Optional[List[str]] = []


class HostelCreate(BaseModel):
    available: bool = False
    capacity: Optional[int] = None
    rooms_type: Optional[str] = None
    facilities: Optional[List[str]] = []
    boys_hostel: bool = False
    girls_hostel: bool = False


class InfrastructureCreate(BaseModel):
    campus: Optional[CampusCreate] = None
    facilities: Optional[List[str]] = []
    hostel: Optional[HostelCreate] = None
    transport: Optional[List[str]] = []


class SocialMediaLinksCreate(BaseModel):
    facebook: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None
    instagram: Optional[HttpUrl] = None
    youtube: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None


class SocialMediaCreate(BaseModel):
    official: Optional[SocialMediaLinksCreate] = None
    student: Optional[SocialMediaLinksCreate] = None


class ImagesCreate(BaseModel):
    logo: Optional[HttpUrl] = None
    campus: Optional[List[HttpUrl]] = []
    hostel: Optional[List[HttpUrl]] = []
    facilities: Optional[List[HttpUrl]] = []
    events: Optional[List[HttpUrl]] = []
    classrooms: Optional[List[HttpUrl]] = []
    labs: Optional[List[HttpUrl]] = []


class NotableAlumniCreate(BaseModel):
    name: str
    position: Optional[str] = None
    company: Optional[str] = None
    image: Optional[HttpUrl] = None
    graduation_year: Optional[int] = None
    description: Optional[str] = None


class AlumniNetworkCreate(BaseModel):
    total_alumni: Optional[int] = None
    notable_alumni: Optional[List[NotableAlumniCreate]] = []


class EventCreate(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    image: Optional[HttpUrl] = None
    annual: bool = False


class ScholarshipCreate(BaseModel):
    name: str
    amount: Optional[str] = None
    eligibility: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None


class NearbyPlaceCreate(BaseModel):
    name: str
    distance: Optional[str] = None
    type: Optional[str] = None


class NewsItemCreate(BaseModel):
    title: str
    date: Optional[str] = None
    category: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    image: Optional[HttpUrl] = None
    url: Optional[HttpUrl] = None


class StartupCreate(BaseModel):
    name: str
    founder: Optional[str] = None
    description: Optional[str] = None
    funding: Optional[str] = None
    image: Optional[HttpUrl] = None
    founded_year: Optional[int] = None
    website: Optional[HttpUrl] = None


class GrantCreate(BaseModel):
    amount: str
    source: str
    purpose: Optional[str] = None
    year: Optional[int] = None


class FundingCreate(BaseModel):
    total_funding: Optional[str] = None
    sources: Optional[List[str]] = []
    recent_grants: Optional[List[GrantCreate]] = []


class AccreditationCreate(BaseModel):
    body: str
    grade: Optional[str] = None
    valid_until: Optional[str] = None
    score: Optional[float] = None


class AffiliationCreate(BaseModel):
    university: Optional[str] = None
    regulatory_bodies: Optional[List[str]] = []


# Main College Create Request Schema
class CollegeCreateRequest(BaseModel):
    # Basic Information (Required)
    name: str = Field(..., min_length=1, max_length=500, description="Full name of the college")
    
    # Basic Information (Optional)
    short_name: Optional[str] = Field(None, max_length=100, description="Short name or acronym")
    alias: Optional[str] = Field(None, max_length=200, description="Alternative name")
    description: Optional[str] = Field(None, description="Detailed description of the college")
    established_year: Optional[int] = Field(None, ge=1800, le=2030, description="Year of establishment")
    
    # Classification
    type: Optional[str] = Field(None, description="Public, Private, Deemed, or Autonomous")
    category: Optional[str] = Field(None, description="Engineering, Medical, Management, etc.")
    sub_category: Optional[str] = Field(None, description="IIT, NIT, IIIT, AIIMS, etc.")
    
    # Location & Contact
    address: Optional[AddressCreate] = None
    contact: Optional[ContactCreate] = None
    
    # Ratings & Rankings
    ratings: Optional[RatingsCreate] = None
    rankings: Optional[List[CollegeRankingCreate]] = []
    
    # Featured & Metadata
    featured: bool = False
    verified: bool = False
    tags: Optional[List[str]] = []
    
    # Academics
    academics: Optional[AcademicsCreate] = None
    
    # Financial
    fees: Optional[FeesCreate] = None
    placement: Optional[PlacementCreate] = None
    
    # Infrastructure
    infrastructure: Optional[InfrastructureCreate] = None
    
    # Media
    images: Optional[ImagesCreate] = None
    social_media: Optional[SocialMediaCreate] = None
    
    # Community
    alumni_network: Optional[AlumniNetworkCreate] = None
    clubs: Optional[List[str]] = []
    
    # Events & Activities
    events: Optional[List[EventCreate]] = []
    
    # Financial Aid
    scholarships: Optional[List[ScholarshipCreate]] = []
    
    # Additional Information
    nearby_places: Optional[List[NearbyPlaceCreate]] = []
    news: Optional[List[NewsItemCreate]] = []
    startups: Optional[List[StartupCreate]] = []
    funding: Optional[FundingCreate] = None
    
    # Accreditation & Affiliation
    accreditations: Optional[List[AccreditationCreate]] = []
    affiliation: Optional[AffiliationCreate] = None
    
    # Admission Information
    admission_process: Optional[str] = None
    entrance_exams: Optional[List[str]] = []
    
    # SEO & Metadata
    slug: Optional[str] = Field(None, description="URL-friendly slug")
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[List[str]] = []
    
    # Status
    is_active: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Indian Institute of Technology Delhi",
                "short_name": "IIT Delhi",
                "established_year": 1961,
                "type": "Public",
                "category": "Engineering",
                "sub_category": "IIT",
                "description": "IIT Delhi is one of the premier engineering institutions in India",
                "address": {
                    "line1": "Hauz Khas",
                    "city": "New Delhi",
                    "state": "Delhi",
                    "country": "India",
                    "pincode": "110016",
                    "coordinates": {"lat": 28.5449, "lng": 77.1929}
                },
                "contact": {
                    "phone": ["+91-11-2659-1999"],
                    "email": ["info@iitd.ac.in"],
                    "website": "https://www.iitd.ac.in"
                },
                "featured": True,
                "verified": True,
                "tags": ["engineering", "technology", "iit"]
            }
        }


# College Update Request Schema
class CollegeUpdateRequest(BaseModel):
    # All fields are optional for update
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    short_name: Optional[str] = Field(None, max_length=100)
    alias: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    established_year: Optional[int] = Field(None, ge=1800, le=2030)
    
    type: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    
    address: Optional[AddressCreate] = None
    contact: Optional[ContactCreate] = None
    
    ratings: Optional[RatingsCreate] = None
    rankings: Optional[List[CollegeRankingCreate]] = None
    
    featured: Optional[bool] = None
    verified: Optional[bool] = None
    tags: Optional[List[str]] = None
    
    academics: Optional[AcademicsCreate] = None
    fees: Optional[FeesCreate] = None
    placement: Optional[PlacementCreate] = None
    infrastructure: Optional[InfrastructureCreate] = None
    
    images: Optional[ImagesCreate] = None
    social_media: Optional[SocialMediaCreate] = None
    
    alumni_network: Optional[AlumniNetworkCreate] = None
    clubs: Optional[List[str]] = None
    
    events: Optional[List[EventCreate]] = None
    scholarships: Optional[List[ScholarshipCreate]] = None
    
    nearby_places: Optional[List[NearbyPlaceCreate]] = None
    news: Optional[List[NewsItemCreate]] = None
    startups: Optional[List[StartupCreate]] = None
    funding: Optional[FundingCreate] = None
    
    accreditations: Optional[List[AccreditationCreate]] = None
    affiliation: Optional[AffiliationCreate] = None
    
    admission_process: Optional[str] = None
    entrance_exams: Optional[List[str]] = None
    
    slug: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[List[str]] = None
    
    is_active: Optional[bool] = None

# College List Item Schema (for college listing page)
class CollegeListItem(BaseModel):
    id: str = Field(alias="_id")
    name: str
    short_name: Optional[str] = Field(None, alias="shortName")
    location: str  # city
    state: str
    rating: Optional[float] = None
    reviews: Optional[int] = Field(None, alias="review_count")
    type: Optional[str] = None  # Public/Private
    category: Optional[str] = None  # Engineering, Medical, etc.
    established: Optional[int] = Field(None, alias="established_year")
    fees: Optional[str] = None
    placement: Optional[str] = None  # Average package
    ranking: Optional[int] = None
    featured: bool = False
    courses: Optional[int] = None  # Total number of courses
    students: Optional[int] = None  # Total student count
    image: Optional[str] = None
    
    class Config:
        populate_by_name = True

# College List Page Response
class CollegeListPageResponse(BaseModel):
    colleges: List[CollegeListItem]
    total: int
    page: int
    size: int

# College Detail Page Schemas
class LocationDetail(BaseModel):
    address: str
    city: str
    state: str
    pincode: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {lat: float, lng: float}

class ContactDetail(BaseModel):
    phone: Optional[List[str]] = []
    email: Optional[List[str]] = []
    website: Optional[str] = None
    admission_helpline: Optional[str] = Field(None, alias="admissionHelpline")
    
    class Config:
        populate_by_name = True

class RatingsDetail(BaseModel):
    overall: Optional[float] = None
    academics: Optional[float] = None
    infrastructure: Optional[float] = None
    faculty: Optional[float] = None
    placement: Optional[float] = None
    hostel_life: Optional[float] = Field(None, alias="hostelLife")
    social_life: Optional[float] = Field(None, alias="socialLife")
    total_reviews: Optional[int] = Field(None, alias="totalReviews")
    
    class Config:
        populate_by_name = True

class FeesDetail(BaseModel):
    tuition: Optional[str] = None
    hostel: Optional[str] = None
    other: Optional[str] = None
    total: Optional[str] = None

class PlacementDetail(BaseModel):
    average_package: Optional[str] = Field(None, alias="averagePackage")
    highest_package: Optional[str] = Field(None, alias="highestPackage")
    placement_rate: Optional[float] = Field(None, alias="placementRate")
    top_recruiters: Optional[List[str]] = Field([], alias="topRecruiters")
    
    class Config:
        populate_by_name = True

class CoursesDetail(BaseModel):
    undergraduate: Optional[List[str]] = []
    postgraduate: Optional[List[str]] = []
    phd: Optional[List[str]] = []

class AcademicsDetail(BaseModel):
    courses: Optional[CoursesDetail] = None
    departments: Optional[List[str]] = []
    faculty_count: Optional[int] = Field(None, alias="facultyCount")
    student_faculty_ratio: Optional[str] = Field(None, alias="studentFacultyRatio")
    
    class Config:
        populate_by_name = True

class CampusDetail(BaseModel):
    area: Optional[str] = None
    buildings: Optional[int] = None
    labs: Optional[int] = None
    libraries: Optional[int] = None

class HostelDetail(BaseModel):
    capacity: Optional[int] = None
    rooms: Optional[str] = None
    facilities: Optional[List[str]] = []

class InfrastructureDetail(BaseModel):
    campus: Optional[CampusDetail] = None
    facilities: Optional[List[str]] = []
    hostel: Optional[HostelDetail] = None

class SocialMediaLinks(BaseModel):
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    linkedin: Optional[str] = None

class SocialMediaDetail(BaseModel):
    official: Optional[SocialMediaLinks] = None
    student: Optional[SocialMediaLinks] = None

class ImagesDetail(BaseModel):
    campus: Optional[List[str]] = []
    hostel: Optional[List[str]] = []
    facilities: Optional[List[str]] = []
    events: Optional[List[str]] = []

class NotableAlumni(BaseModel):
    name: str
    position: Optional[str] = None
    company: Optional[str] = None
    image: Optional[str] = None

class AlumniNetworkDetail(BaseModel):
    total_alumni: Optional[int] = Field(None, alias="totalAlumni")
    notable_alumni: Optional[List[NotableAlumni]] = Field([], alias="notableAlumni")
    
    class Config:
        populate_by_name = True

class EventDetail(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    image: Optional[str] = None

class ScholarshipDetail(BaseModel):
    name: str
    amount: Optional[str] = None
    eligibility: Optional[str] = None
    description: Optional[str] = None

class NearbyPlace(BaseModel):
    name: str
    distance: Optional[str] = None
    type: Optional[str] = None

class NewsItem(BaseModel):
    title: str
    date: Optional[str] = None
    category: Optional[str] = None
    excerpt: Optional[str] = None
    image: Optional[str] = None

class StartupDetail(BaseModel):
    name: str
    founder: Optional[str] = None
    description: Optional[str] = None
    funding: Optional[str] = None
    image: Optional[str] = None

class GrantDetail(BaseModel):
    amount: str
    source: str
    purpose: Optional[str] = None
    year: Optional[int] = None

class FundingDetail(BaseModel):
    total_funding: Optional[str] = Field(None, alias="totalFunding")
    sources: Optional[List[str]] = []
    recent_grants: Optional[List[GrantDetail]] = Field([], alias="recentGrants")
    
    class Config:
        populate_by_name = True

# College Detail Page Response
class CollegeDetailResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    short_name: Optional[str] = Field(None, alias="shortName")
    established: Optional[int] = Field(None, alias="established_year")
    type: Optional[str] = None
    category: Optional[str] = None
    location: Optional[LocationDetail] = None
    contact: Optional[ContactDetail] = None
    ratings: Optional[RatingsDetail] = None
    fees: Optional[FeesDetail] = None
    placement: Optional[PlacementDetail] = None
    academics: Optional[AcademicsDetail] = None
    infrastructure: Optional[InfrastructureDetail] = None
    social_media: Optional[SocialMediaDetail] = Field(None, alias="socialMedia")
    images: Optional[ImagesDetail] = None
    alumni_network: Optional[AlumniNetworkDetail] = Field(None, alias="alumniNetwork")
    clubs: Optional[List[str]] = []
    events: Optional[List[EventDetail]] = []
    scholarships: Optional[List[ScholarshipDetail]] = []
    nearby_places: Optional[List[NearbyPlace]] = Field([], alias="nearbyPlaces")
    news: Optional[List[NewsItem]] = []
    startups: Optional[List[StartupDetail]] = []
    funding: Optional[FundingDetail] = None
    
    class Config:
        populate_by_name = True