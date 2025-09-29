from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from app.db.mongo import get_database
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    def __init__(self):
        self.collection_name = "users"
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        db = await get_database()
        collection = db[self.collection_name]
        
        # Check if user already exists
        existing_user = await collection.find_one(
            {"$or": [{"email": user_data.email}, {"username": user_data.username}]}
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.dict(exclude={"password"})
        user_dict["hashed_password"] = hashed_password
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        
        try:
            result = await collection.insert_one(user_dict)
            user_dict["_id"] = str(result.inserted_id)
            return User(**user_dict)
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        db = await get_database()
        collection = db[self.collection_name]
        
        user_doc = await collection.find_one({"email": email})
        if user_doc:
            user_doc["_id"] = str(user_doc["_id"])
            return User(**user_doc)
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        db = await get_database()
        collection = db[self.collection_name]
        
        try:
            user_doc = await collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                user_doc["_id"] = str(user_doc["_id"])
                return User(**user_doc)
        except Exception:
            pass
        return None
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        db = await get_database()
        collection = db[self.collection_name]
        
        update_data = user_data.model_dump()
        if not update_data:
            return await self.get_user_by_id(user_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            result = await collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            if result.modified_count:
                return await self.get_user_by_id(user_id)
        except Exception:
            pass
        return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def enroll_course(self, user_id: str, course_id: str) -> bool:
        """Enroll user in a course."""
        db = await get_database()
        collection = db[self.collection_name]
        
        try:
            result = await collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$addToSet": {"enrolled_courses": course_id}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def get_users(self, skip: int = 0, limit: int = 10, role: Optional[UserRole] = None) -> List[User]:
        """Get list of users with pagination."""
        db = await get_database()
        collection = db[self.collection_name]
        
        query = {}
        if role:
            query["role"] = role
        
        cursor = collection.find(query).skip(skip).limit(limit)
        users = []
        
        async for user_doc in cursor:
            user_doc["_id"] = str(user_doc["_id"])
            users.append(User(**user_doc))
        
        return users


user_service = UserService()