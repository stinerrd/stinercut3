"""
ImportBatch model for SQLAlchemy.
Tracks import batches and their resolution status.
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, Integer

from database import Base


class ImportBatch(Base):
    """
    ImportBatch model representing a batch of imported video files.
    Tracks analysis progress and resolution status.
    """
    __tablename__ = "import_batch"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False)  # Folder UUID

    # Analysis results
    total_files = Column(Integer, default=0)
    analyzed_files = Column(Integer, default=0)
    detected_qr_count = Column(Integer, default=0)  # Number of unique QR codes found
    detected_freefall_count = Column(Integer, default=0)  # Number of freefall segments

    # Status: pending, analyzing, resolved, needs_manual, error
    status = Column(String(50), default='pending', nullable=False)
    # Resolution type: auto_single, auto_multi, manual, unresolved
    resolution_type = Column(String(50), nullable=True)

    error_message = Column(Text, nullable=True)

    # SD card mount path (for organizing SD card after resolution)
    mount_path = Column(String(255), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ImportBatch(id={self.id}, uuid={self.uuid}, status={self.status})>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'total_files': self.total_files,
            'analyzed_files': self.analyzed_files,
            'detected_qr_count': self.detected_qr_count,
            'detected_freefall_count': self.detected_freefall_count,
            'status': self.status,
            'resolution_type': self.resolution_type,
            'error_message': self.error_message,
            'mount_path': self.mount_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
