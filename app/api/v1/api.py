from fastapi import APIRouter
from app.api.v1.endpoints import colleges

api_router = APIRouter()

api_router.include_router(colleges.router, prefix="/colleges", tags=["colleges"])
# api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
# api_router.include_router(faculties.router, prefix="/faculties", tags=["faculties"])
# api_router.include_router(academics.router, prefix="/academics", tags=["academics"])
# api_router.include_router(scholarships.router, prefix="/scholarships", tags=["scholarships"])
# api_router.include_router(branches.router, prefix="/branches", tags=["branches"])