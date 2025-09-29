from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List


class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    profile_image: Optional[HttpUrl] = None
    bio: Optional[str] = Field(None, max_length=500)