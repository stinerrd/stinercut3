"""
Job model for SQLAlchemy.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base


class Job(Base):
    """
    Job model representing a rendering/processing job.
    """
    __tablename__ = "job"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)

    # Status tracking
    status = Column(
        SQLEnum("pending", "processing", "completed", "failed", "cancelled", name="job_status"),
        nullable=False,
        default="pending"
    )
    progress = Column(Integer, nullable=False, default=0)  # 0-100

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Result
    output_path = Column(String(512), nullable=True)  # Relative to /shared-videos/
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="jobs")

    def __repr__(self):
        return f"<Job(id={self.id}, uuid={self.uuid}, status={self.status}, progress={self.progress})>"
