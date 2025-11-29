"""
Asset model for SQLAlchemy.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from database import Base


class Asset(Base):
    """
    Asset model representing reusable assets (intros, outros, watermarks, audio).
    """
    __tablename__ = "asset"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    type = Column(
        SQLEnum(
            "intro", "outro", "watermark", "audio", "audio_freefall", "pax_template",
            name="asset_type"
        ),
        nullable=False
    )
    name = Column(String(255), nullable=False)
    path = Column(String(512), nullable=False)  # Relative to /shared-videos/

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Asset(id={self.id}, uuid={self.uuid}, type={self.type}, name={self.name})>"
