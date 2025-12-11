"""
VideoFileSegment model for SQLAlchemy.
Stores detected segment boundaries within each video file.
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class VideoFileSegment(Base):
    """
    VideoFileSegment model representing a classified segment within a video file.
    Each segment has a start/end time and classification.
    """
    __tablename__ = "video_file_segment"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False)
    video_file_id = Column(BigInteger, ForeignKey("video_file.id", ondelete="CASCADE"), nullable=False)

    # Timeslot
    start_time = Column(Numeric(10, 3), nullable=False)  # Start timestamp in seconds
    end_time = Column(Numeric(10, 3), nullable=False)  # End timestamp in seconds

    # Classification: qr_code, ground_before, flight, freefall, canopy, ground_after, unknown
    classification = Column(String(50), nullable=False)
    confidence = Column(Numeric(5, 4), nullable=True)

    # Order within video
    sequence_order = Column(Integer, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    video_file = relationship("VideoFile", back_populates="segments")

    def __repr__(self):
        return f"<VideoFileSegment(id={self.id}, classification={self.classification}, {self.start_time}-{self.end_time}s)>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'video_file_id': self.video_file_id,
            'start_time': float(self.start_time) if self.start_time else None,
            'end_time': float(self.end_time) if self.end_time else None,
            'classification': self.classification,
            'confidence': float(self.confidence) if self.confidence else None,
            'sequence_order': self.sequence_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
