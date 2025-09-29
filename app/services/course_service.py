from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from bson import ObjectId

from app.db.mongo import get_database
from app.models.academics import Course, CourseStatus, Lesson
from app.schemas.course import CourseCreate, CourseUpdate, LessonCreate, LessonUpdate


class CourseService:
    def __init__(self):
        self.collection_name = "courses"
    
    async def create_course(self, course_data: CourseCreate, instructor_id: str) -> Course:
        """Create a new course."""
        db = await get_database()
        collection = db[self.collection_name]
        
        course_dict = course_data.dict()
        course_dict["instructor_id"] = instructor_id
        course_dict["status"] = CourseStatus.DRAFT
        course_dict["created_at"] = datetime.utcnow()
        course_dict["updated_at"] = datetime.utcnow()
        course_dict["enrolled_students"] = []
        course_dict["lessons"] = []
        course_dict["rating"] = 0.0
        course_dict["review_count"] = 0
        
        result = await collection.insert_one(course_dict)
        course_dict["_id"] = str(result.inserted_id)
        return Course(**course_dict)
    
    async def get_course_by_id(self, course_id: str) -> Optional[Course]:
        """Get course by ID."""
        db = await get_database()
        collection = db[self.collection_name]
        
        try:
            course_doc = await collection.find_one({"_id": ObjectId(course_id)})
            if course_doc:
                course_doc["_id"] = str(course_doc["_id"])
                return Course(**course_doc)
        except Exception:
            pass
        return None
    
    async def update_course(self, course_id: str, course_data: CourseUpdate, instructor_id: str) -> Optional[Course]:
        """Update course information."""
        db = await get_database()
        collection = db[self.collection_name]
        
        # Verify instructor owns the course
        course = await self.get_course_by_id(course_id)
        if not course or course.instructor_id != instructor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this course"
            )
        
        update_data = course_data.model_dump()
        if not update_data:
            return course
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            result = await collection.update_one(
                {"_id": ObjectId(course_id)},
                {"$set": update_data}
            )
            if result.modified_count:
                return await self.get_course_by_id(course_id)
        except Exception:
            pass
        return None
    
    async def get_courses(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        category: Optional[str] = None,
        level: Optional[str] = None,
        status: Optional[CourseStatus] = None,
        instructor_id: Optional[str] = None
    ) -> List[Course]:
        """Get list of courses with filtering and pagination."""
        db = await get_database()
        collection = db[self.collection_name]
        
        query = {}
        if category:
            query["category"] = category
        if level:
            query["level"] = level
        if status:
            query["status"] = status
        if instructor_id:
            query["instructor_id"] = instructor_id
        
        cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        courses = []
        
        async for course_doc in cursor:
            course_doc["_id"] = str(course_doc["_id"])
            courses.append(Course(**course_doc))
        
        return courses
    
    async def search_courses(self, query: str, skip: int = 0, limit: int = 10) -> List[Course]:
        """Search courses by title, description, or tags."""
        db = await get_database()
        collection = db[self.collection_name]
        
        search_query = {
            "$and": [
                {"status": CourseStatus.PUBLISHED},
                {
                    "$or": [
                        {"title": {"$regex": query, "$options": "i"}},
                        {"description": {"$regex": query, "$options": "i"}},
                        {"tags": {"$in": [query]}},
                        {"category": {"$regex": query, "$options": "i"}}
                    ]
                }
            ]
        }
        
        cursor = collection.find(search_query).skip(skip).limit(limit)
        courses = []
        
        async for course_doc in cursor:
            course_doc["_id"] = str(course_doc["_id"])
            courses.append(Course(**course_doc))
        
        return courses
    
    async def enroll_student(self, course_id: str, student_id: str) -> bool:
        """Enroll a student in a course."""
        db = await get_database()
        collection = db[self.collection_name]
        
        try:
            result = await collection.update_one(
                {"_id": ObjectId(course_id), "status": CourseStatus.PUBLISHED},
                {"$addToSet": {"enrolled_students": student_id}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def add_lesson(self, course_id: str, lesson_data: LessonCreate, instructor_id: str) -> Optional[Course]:
        """Add a lesson to a course."""
        db = await get_database()
        collection = db[self.collection_name]
        
        # Verify instructor owns the course
        course = await self.get_course_by_id(course_id)
        if not course or course.instructor_id != instructor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add lessons to this course"
            )
        
        lesson_dict = lesson_data.dict()
        
        try:
            result = await collection.update_one(
                {"_id": ObjectId(course_id)},
                {
                    "$push": {"lessons": lesson_dict},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            if result.modified_count:
                return await self.get_course_by_id(course_id)
        except Exception:
            pass
        return None
    
    async def delete_course(self, course_id: str, instructor_id: str) -> bool:
        """Delete a course."""
        db = await get_database()
        collection = db[self.collection_name]
        
        try:
            result = await collection.delete_one({
                "_id": ObjectId(course_id),
                "instructor_id": instructor_id
            })
            return result.deleted_count > 0
        except Exception:
            return False


course_service = CourseService()