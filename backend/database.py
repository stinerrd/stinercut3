"""
Database configuration and session management for SQLAlchemy.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Get database URL from environment and ensure pymysql driver is used
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://stiner:local@mysql:3306/stinercut")
# Ensure pymysql driver is used even if DATABASE_URL is set with mysql:// scheme
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Create engine with connection pool settings
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    echo=False,  # Set to True for SQL logging in development
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI endpoints to get database session.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Call this on application startup.
    """
    from backend.models import project, video, job, asset  # noqa: F401
    Base.metadata.create_all(bind=engine)
