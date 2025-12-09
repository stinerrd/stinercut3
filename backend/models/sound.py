"""
Sound model for SQLAlchemy.
Represents audio files for different skydiving phases (boden, plane, freefall, canopy).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, LargeBinary

from database import Base


class Sound(Base):
    """
    Sound model representing an audio file for a specific skydiving phase.
    """
    __tablename__ = "sound"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # 'boden', 'plane', 'freefall', 'canopy'
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    waveform = Column(LargeBinary, nullable=True)  # PNG bytes stored as BLOB
    duration = Column(Integer, nullable=True)  # Duration in seconds

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Sound(id={self.id}, name={self.name}, type={self.type})>"
