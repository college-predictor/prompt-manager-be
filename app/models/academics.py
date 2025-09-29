from typing import Optional
from enum import Enum
from beanie import Document, Link
from app.models.faculty import Faculty, Department

class CourseLevel(str, Enum):
    BACHELOR = "Bachelor"
    MASTER = "Master"
    PHD = "PhD"

class AcademicStream(Document):
    code: Optional[str]
    title: str 
    description: Optional[str]

    class Settings:
        name = "academic_streams"

class AcademicCourse(Document):
    title: str
    course_code: Optional[str]
    description: str
    academic_stream: Link[AcademicStream]
    course_level: Optional[CourseLevel]
    credits: Optional[int]
    semester: Optional[int]
    faculty: Optional[Link[Faculty]] = None

    class Settings:
        name = "academic_courses"