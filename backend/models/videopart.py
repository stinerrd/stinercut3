"""
Videopart model for SQLAlchemy.
Represents intro/outro video segments.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, LargeBinary
from database import Base


class Videopart(Base):
    """
    Videopart model representing an intro or outro video segment.
    """
    __tablename__ = "videopart"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # 'intro' or 'outro'
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    thumbnail = Column(LargeBinary, nullable=True)  # JPEG bytes stored as BLOB
    duration = Column(Integer, nullable=True)  # Duration in seconds

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Videopart(id={self.id}, name={self.name}, type={self.type})>"
