"""
Project model for SQLAlchemy.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base


class Project(Base):
    """
    Project model representing a video editing project.
    """
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    status = Column(
        SQLEnum("draft", "processing", "completed", "error", name="project_status"),
        nullable=False,
        default="draft"
    )
    settings = Column(Text, nullable=True)  # JSON stored as text
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    videos = relationship("Video", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, uuid={self.uuid}, name={self.name}, status={self.status})>"
