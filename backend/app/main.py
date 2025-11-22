"""
FastAPI Main Application
AI Resume Parser & Screening System
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import init_db, Base, engine
from .routes import auth, resume, candidate, analytics
import os

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered resume parsing and candidate screening system",
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting AI Resume Parser API...")
    print(f"📁 Upload directory: {settings.upload_dir}")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")
    
    # Load ML model
    from .services.ml_parser import get_ml_parser
    parser = get_ml_parser()
    parser.load_model()
    print("✓ ML model loaded")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(candidate.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Resume Parser API",
        "version": settings.app_version,
        "status": "running"
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
