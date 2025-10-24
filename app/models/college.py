from enum import Enum
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from beanie import Document


class CollegeType(str, Enum):
    PUBLIC = "Public"
    PRIVATE = "Private"
    DEEMED = "Deemed"
    AUTONOMOUS = "Autonomous"


class CollegeCategory(str, Enum):
    ENGINEERING = "Engineering"
    MEDICAL = "Medical"
    MANAGEMENT = "Management"
    LAW = "Law"
    ARTS = "Arts"
    SCIENCE = "Science"
    COMMERCE = "Commerce"
    PHARMACY = "Pharmacy"
    ARCHITECTURE = "Architecture"
    AGRICULTURE = "Agriculture"
    DENTAL = "Dental"
    NURSING = "Nursing"
    HOTEL_MANAGEMENT = "Hotel Management"
    DESIGN = "Design"
    EDUCATION = "Education"
    PARAMEDICAL = "Paramedical"
    MASS_COMMUNICATION = "Mass Communication"
    OTHER = "Other"


class CollegeSubCategory(str, Enum):
    IIT = "IIT"
    NIT = "NIT"
    IIIT = "IIIT"
    AIIMS = "AIIMS"
    IIM = "IIM"
    CENTRAL_UNIVERSITY = "Central University"
    STATE_UNIVERSITY = "State University"
    PRIVATE_UNIVERSITY = "Private University"
    TECHNICAL_INSTITUTE = "Technical Institute"
    MEDICAL_COLLEGE = "Medical College"
    ENGINEERING_COLLEGE = "Engineering College"
    OTHER = "Other"


# Embedded Document Models
class Coordinates(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None


class Address(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: str
    state: str
    country: str = "India"
    pincode: Optional[str] = None
    coordinates: Optional[Coordinates] = None


class Contact(BaseModel):
    phone: Optional[List[str]] = []
    email: Optional[List[str]] = []
    website: Optional[str] = None
    admission_helpline: Optional[str] = None


class Ratings(BaseModel):
    overall: Optional[float] = Field(None, ge=0, le=5)
    academics: Optional[float] = Field(None, ge=0, le=5)
    infrastructure: Optional[float] = Field(None, ge=0, le=5)
    faculty: Optional[float] = Field(None, ge=0, le=5)
    placement: Optional[float] = Field(None, ge=0, le=5)
    hostel_life: Optional[float] = Field(None, ge=0, le=5)
    social_life: Optional[float] = Field(None, ge=0, le=5)
    total_reviews: int = 0


class CollegeRanking(BaseModel):
    organisation: str  # NIRF, QS, Times, etc.
    rank: int
    year: int
    category: Optional[str] = None  # Overall, Engineering, etc.


class Fees(BaseModel):
    tuition: Optional[str] = None
    hostel: Optional[str] = None
    other: Optional[str] = None
    total: Optional[str] = None
    currency: str = "INR"


class Placement(BaseModel):
    average_package: Optional[str] = None
    median_package: Optional[str] = None
    highest_package: Optional[str] = None
    placement_rate: Optional[float] = Field(None, ge=0, le=100)
    top_recruiters: Optional[List[str]] = []


class Courses(BaseModel):
    undergraduate: Optional[List[str]] = []
    postgraduate: Optional[List[str]] = []
    phd: Optional[List[str]] = []
    diploma: Optional[List[str]] = []
    certificate: Optional[List[str]] = []


class Academics(BaseModel):
    courses: Optional[Courses] = None
    departments: Optional[List[str]] = []
    faculty_count: Optional[int] = None
    student_faculty_ratio: Optional[str] = None
    total_students: Optional[int] = None


class Campus(BaseModel):
    area: Optional[str] = None
    buildings: Optional[int] = None
    labs: Optional[int] = None
    libraries: Optional[int] = None
    auditoriums: Optional[int] = None
    sports_facilities: Optional[List[str]] = []


class Hostel(BaseModel):
    available: bool = False
    capacity: Optional[int] = None
    rooms_type: Optional[str] = None  # Single, Double, Triple
    facilities: Optional[List[str]] = []
    boys_hostel: bool = False
    girls_hostel: bool = False


class Infrastructure(BaseModel):
    campus: Optional[Campus] = None
    facilities: Optional[List[str]] = []
    hostel: Optional[Hostel] = None
    transport: Optional[List[str]] = []  # Bus, Metro connectivity, etc.


class SocialMediaLinks(BaseModel):
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    linkedin: Optional[str] = None


class SocialMedia(BaseModel):
    official: Optional[SocialMediaLinks] = None
    student: Optional[SocialMediaLinks] = None


class Images(BaseModel):
    logo: Optional[str] = None
    campus: Optional[List[str]] = []
    hostel: Optional[List[str]] = []
    facilities: Optional[List[str]] = []
    events: Optional[List[str]] = []
    classrooms: Optional[List[str]] = []
    labs: Optional[List[str]] = []


class NotableAlumni(BaseModel):
    name: str
    position: Optional[str] = None
    company: Optional[str] = None
    image: Optional[str] = None
    graduation_year: Optional[int] = None
    description: Optional[str] = None


class AlumniNetwork(BaseModel):
    total_alumni: Optional[int] = None
    notable_alumni: Optional[List[NotableAlumni]] = []


class Event(BaseModel):
    name: str
    type: Optional[str] = None  # Cultural, Technical, Sports
    description: Optional[str] = None
    date: Optional[str] = None
    image: Optional[str] = None
    annual: bool = False


class Scholarship(BaseModel):
    name: str
    amount: Optional[str] = None
    eligibility: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None  # Merit, Need-based, Sports, etc.


class NearbyPlace(BaseModel):
    name: str
    distance: Optional[str] = None
    type: Optional[str] = None  # Transport, Recreation, Shopping, etc.


class NewsItem(BaseModel):
    title: str
    date: Optional[str] = None
    category: Optional[str] = None  # Rankings, Research, Events, etc.
    excerpt: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    url: Optional[str] = None


class Startup(BaseModel):
    name: str
    founder: Optional[str] = None
    description: Optional[str] = None
    funding: Optional[str] = None
    image: Optional[str] = None
    founded_year: Optional[int] = None
    website: Optional[str] = None


class Grant(BaseModel):
    amount: str
    source: str
    purpose: Optional[str] = None
    year: Optional[int] = None


class Funding(BaseModel):
    total_funding: Optional[str] = None
    sources: Optional[List[str]] = []
    recent_grants: Optional[List[Grant]] = []


class Accreditation(BaseModel):
    body: str  # NAAC, NBA, UGC, AICTE, etc.
    grade: Optional[str] = None
    valid_until: Optional[str] = None
    score: Optional[float] = None


class Affiliation(BaseModel):
    university: Optional[str] = None
    regulatory_bodies: Optional[List[str]] = []  # UGC, AICTE, MCI, etc.


# Main College Model
class College(Document):
    # Basic Information
    name: str = Field(..., min_length=1, max_length=500)
    short_name: Optional[str] = None
    alias: Optional[str] = None
    description: Optional[str] = None
    established_year: Optional[int] = Field(None, ge=1800, le=2030)
    
    # Classification
    type: Optional[CollegeType] = None
    category: Optional[CollegeCategory] = None
    sub_category: Optional[CollegeSubCategory] = None
    
    # Location & Contact
    address: Optional[Address] = None
    contact: Optional[Contact] = None
    
    # Ratings & Rankings
    ratings: Optional[Ratings] = Ratings()
    rankings: Optional[List[CollegeRanking]] = []
    
    # Featured & Metadata
    featured: bool = False
    verified: bool = False
    tags: Optional[List[str]] = []
    
    # Academics
    academics: Optional[Academics] = None
    
    # Financial
    fees: Optional[Fees] = None
    placement: Optional[Placement] = None
    
    # Infrastructure
    infrastructure: Optional[Infrastructure] = None
    
    # Media
    images: Optional[Images] = None
    social_media: Optional[SocialMedia] = None
    
    # Community
    alumni_network: Optional[AlumniNetwork] = None
    clubs: Optional[List[str]] = []
    
    # Events & Activities
    events: Optional[List[Event]] = []
    
    # Financial Aid
    scholarships: Optional[List[Scholarship]] = []
    
    # Additional Information
    nearby_places: Optional[List[NearbyPlace]] = []
    news: Optional[List[NewsItem]] = []
    startups: Optional[List[Startup]] = []
    funding: Optional[Funding] = None
    
    # Accreditation & Affiliation
    accreditations: Optional[List[Accreditation]] = []
    affiliation: Optional[Affiliation] = None
    
    # Admission Information
    admission_process: Optional[str] = None
    entrance_exams: Optional[List[str]] = []  # JEE, NEET, CAT, etc.
    
    # SEO & Metadata
    slug: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[List[str]] = []
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    is_deleted: bool = False
    
    class Settings:
        name = "colleges"