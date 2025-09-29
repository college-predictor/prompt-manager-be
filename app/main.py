from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.mongo import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🔄 Connecting to MongoDB...")
    try:
        await connect_to_mongo()
        print("✅ MongoDB connection established successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise
    yield
    # Shutdown
    print("🔄 Closing MongoDB connection...")
    await close_mongo_connection()
    print("✅ MongoDB connection closed successfully!")

app = FastAPI(
    title="Educational Website API",
    description="A FastAPI backend for educational website similar to shiksha.com",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")



@app.get("/")
async def root():
    return {"message": "College Predictor Website API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint that verifies MongoDB connection"""
    try:
        from app.db.mongo import mongodb
        if mongodb.client is None:
            return {"status": "unhealthy", "database": "disconnected"}
        
        # Test database connection
        await mongodb.client.admin.command('ping')
        return {
            "status": "healthy", 
            "database": "connected",
            "database_name": settings.DATABASE_NAME
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "database": "error",
            "error": str(e)
        }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )