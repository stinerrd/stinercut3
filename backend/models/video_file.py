"""
VideoFile model for SQLAlchemy.
Stores per-file records with metadata and classification.
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, Integer, Numeric, LargeBinary, ForeignKey
from sqlalchemy.dialects.mysql import MEDIUMBLOB
from sqlalchemy.orm import relationship

from database import Base


class VideoFile(Base):
    """
    VideoFile model representing an imported video file.
    Tracks classification, QR detection, and workload assignment.
    """
    __tablename__ = "video_file"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False)

    # Folder tracking
    import_folder_uuid = Column(String(36), nullable=False)  # Original import folder UUID
    current_folder_uuid = Column(String(36), nullable=False)  # Current folder (may change after matching)
    filepath = Column(String(500), nullable=False)  # Full relative path: {folder_uuid}/{filename}
    original_filename = Column(String(255), nullable=False)

    # Video metadata
    duration = Column(Numeric(10, 3), nullable=True)  # Duration in seconds
    file_size_bytes = Column(BigInteger, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    fps = Column(Numeric(6, 3), nullable=True)
    codec = Column(String(50), nullable=True)
    recorded_at = Column(DateTime, nullable=True)

    # Classification
    dominant_classification = Column(String(50), default='unknown')
    classification_confidence = Column(Numeric(5, 4), nullable=True)

    # QR Detection
    qr_content = Column(Text, nullable=True)  # Raw QR content if found
    detected_workload_uuid = Column(String(36), nullable=True)  # Parsed workload UUID from QR
    workload_id = Column(BigInteger, nullable=True)  # FK to workload table (after matching)

    # Processing status: pending, analyzing, analyzed, matched, error
    status = Column(String(50), default='pending', nullable=False)
    error_message = Column(Text, nullable=True)

    # Jump assignment (for multi-jump scenarios)
    jump_number = Column(Integer, nullable=True)  # Which jump in the session (1, 2, ...)

    # Metadata
    thumbnail = Column(MEDIUMBLOB, nullable=True)  # JPEG thumbnail (up to 16MB)
    import_source = Column(String(50), default='gopro')  # gopro, upload

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    segments = relationship("VideoFileSegment", back_populates="video_file", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<VideoFile(id={self.id}, uuid={self.uuid}, filename={self.original_filename})>"

    def to_dict(self, include_segments=False):
        """Convert to dictionary for JSON serialization."""
        result = {
            'id': self.id,
            'uuid': self.uuid,
            'import_folder_uuid': self.import_folder_uuid,
            'current_folder_uuid': self.current_folder_uuid,
            'filepath': self.filepath,
            'original_filename': self.original_filename,
            'duration': float(self.duration) if self.duration else None,
            'file_size_bytes': self.file_size_bytes,
            'width': self.width,
            'height': self.height,
            'fps': float(self.fps) if self.fps else None,
            'codec': self.codec,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'dominant_classification': self.dominant_classification,
            'classification_confidence': float(self.classification_confidence) if self.classification_confidence else None,
            'qr_content': self.qr_content,
            'detected_workload_uuid': self.detected_workload_uuid,
            'workload_id': self.workload_id,
            'status': self.status,
            'error_message': self.error_message,
            'jump_number': self.jump_number,
            'import_source': self.import_source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_segments and self.segments:
            result['segments'] = [seg.to_dict() for seg in self.segments]
        return result
