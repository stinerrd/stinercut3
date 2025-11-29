"""
Tandem Video Editing Backend
FastAPI + FFmpeg video processing service
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from models import Project, Video, Job, Asset  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager - initialize database on startup."""
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup on shutdown (if needed)


app = FastAPI(
    title="Tandem Video Editor API",
    description="Backend API for video processing with FFmpeg",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Tandem Video Editor Backend",
        "version": "0.1.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    # Check database connection
    db_status = "connected"
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "ffmpeg": "available",  # TODO: Check FFmpeg installation
        "storage": "mounted"     # TODO: Check shared volume
    }


# Service control router
from routers import services
app.include_router(services.router)

# TODO: Implement other routers
# from routers import videos, projects, jobs, websocket
# app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
# app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
# app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
# app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
