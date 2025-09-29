from typing import List, Optional
from datetime import date
from enum import Enum
from beanie import Document, Link
from pydantic import HttpUrl, Field
from app.models.college import College
from app.models.academics import AcademicStream


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    ANY = "any"


class Category(str, Enum):
    GENERAL = "general"
    SC = "sc"  # Scheduled Caste
    ST = "st"  # Scheduled Tribe
    OBC = "obc"  # Other Backward Class
    EWS = "ews"  # Economically Weaker Section
    MINORITY = "minority"
    PWD = "pwd"  # Person with Disability
    ANY = "any"


class ScholarshipType(str, Enum):
    MERIT_BASED = "merit_based"
    NEED_BASED = "need_based"
    SPORTS = "sports"
    CULTURAL = "cultural"
    RESEARCH = "research"
    GOVERNMENT = "government"
    PRIVATE = "private"


class Scholarship(Document):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    amount: Optional[float] = Field(None, ge=0)  # fixed amount
    amount_range: Optional[List[float]] = Field(None, min_items=2, max_items=2)  # [min,max]
    benefit: Optional[str] = Field(None, max_length=200)  # e.g., Tuition fee waiver, Stipend
    
    # Eligibility criteria using enums
    eligible_genders: Optional[List[Gender]] = Field(default_factory=lambda: [Gender.ANY])
    eligible_categories: Optional[List[Category]] = Field(default_factory=lambda: [Category.ANY])
    scholarship_type: Optional[ScholarshipType] = None
    
    # Additional eligibility
    min_percentage: Optional[float] = Field(None, ge=0, le=100)
    min_cgpa: Optional[float] = Field(None, ge=0, le=10)
    max_family_income: Optional[float] = Field(None, ge=0)
    eligible_streams: Optional[List[Link[AcademicStream]]] = Field(default_factory=list)
    
    eligibility_criteria: Optional[str] = Field(None, max_length=500)
    application_process: Optional[str] = Field(None, max_length=500)
    deadline: Optional[date] = None
    active: bool = True
    url: Optional[HttpUrl] = None
    college: Link[College]
    
    # Metadata
    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)

    class Settings:
        name = "scholarships"
        indexes = [
            "active",
            "deadline", 
            "scholarship_type",
            "eligible_genders",
            "eligible_categories",
            "college"
        ]
    
    def is_eligible_for_gender(self, student_gender: Gender) -> bool:
        """Check if scholarship is available for student's gender"""
        return Gender.ANY in self.eligible_genders or student_gender in self.eligible_genders
    
    def is_eligible_for_category(self, student_category: Category) -> bool:
        """Check if scholarship is available for student's category"""
        return Category.ANY in self.eligible_categories or student_category in self.eligible_categories