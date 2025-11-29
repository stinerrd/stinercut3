"""
Video model for SQLAlchemy.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Video(Base):
    """
    Video model representing a video file in a project.
    """
    __tablename__ = "video"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)

    # File info
    filename = Column(String(255), nullable=False)
    path = Column(String(512), nullable=False)  # Relative to /shared-videos/

    # Video metadata
    duration = Column(Float, nullable=True)  # Duration in seconds
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    codec = Column(String(50), nullable=True)
    fps = Column(Float, nullable=True)

    # Editing
    order = Column(Integer, nullable=False, default=0)  # Sequence order in timeline
    in_point = Column(Float, nullable=True)  # Start trim point in seconds
    out_point = Column(Float, nullable=True)  # End trim point in seconds

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="videos")

    def __repr__(self):
        return f"<Video(id={self.id}, uuid={self.uuid}, filename={self.filename})>"
