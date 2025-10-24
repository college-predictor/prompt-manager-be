from pydantic import BaseModel
from typing import Optional, List


class BaseResponseSchema(BaseModel):
    success: bool = True
    data: Optional[dict] = None
    message: Optional[str] = None
    error: Optional[str] = None