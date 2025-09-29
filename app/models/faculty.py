# models.py (Beanie documents)
from typing import List, Optional
from beanie import Document, Link
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from app.models.college import College

class Department(BaseModel):
    name: str
    code: Optional[str]  # e.g., CSE, ECE

class Faculty(Document):
    first_name: str
    middle_name: Optional[str]
    last_name: Optional[str]
    title: Optional[str]          # Prof, Dr, Asst Prof
    email: Optional[EmailStr]
    phone: Optional[str]
    designation: Optional[str]
    departments: Optional[List[Department]] = []
    bio: Optional[str]
    research_interests: Optional[List[str]] = []
    achievements: Optional[List[str]] = []
    publications: Optional[List[str]] = []
    portfolio_url: Optional[HttpUrl]
    linkedin_url: Optional[HttpUrl]
    photo_url: Optional[HttpUrl]
    education: Optional[str]  # e.g., PhD in Computer Science
    experience_years: Optional[int]  # total years of experience
    college: Optional[Link[College]] = None

    class Settings:
        name = "faculties"