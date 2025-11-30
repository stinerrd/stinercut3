"""
Setting model for SQLAlchemy.
"""
import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import Session
from database import Base


class Setting(Base):
    """
    Setting model for application configuration stored in database.
    Read-only from backend perspective - settings are managed via frontend.
    """
    __tablename__ = "setting"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    type = Column(
        SQLEnum("string", "integer", "boolean", "json", name="setting_type"),
        nullable=False,
        default="string"
    )
    category = Column(String(100), nullable=False)
    label = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    options = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Setting(id={self.id}, key={self.key}, type={self.type})>"

    def get_typed_value(self):
        """
        Get the value with proper type casting based on setting type.
        """
        if self.value is None:
            return None

        if self.type == "integer":
            return int(self.value)
        elif self.type == "boolean":
            return self.value.lower() in ("true", "1", "yes")
        elif self.type == "json":
            return json.loads(self.value)
        else:
            return self.value

    def get_options(self):
        """Get options as list if defined."""
        if self.options is None:
            return None
        return json.loads(self.options)

    @classmethod
    def get(cls, db: Session, key: str, default=None):
        """
        Get a setting value by key with type casting.

        Args:
            db: SQLAlchemy session
            key: Setting key (e.g., "video.default_codec")
            default: Default value if setting not found

        Returns:
            The typed value or default if not found
        """
        setting = db.query(cls).filter(cls.key == key).first()
        if setting is None:
            return default
        return setting.get_typed_value()

    @classmethod
    def get_by_category(cls, db: Session, category: str):
        """
        Get all settings in a category.

        Args:
            db: SQLAlchemy session
            category: Category name (e.g., "video", "storage")

        Returns:
            List of Setting objects
        """
        return db.query(cls).filter(cls.category == category).all()

    @classmethod
    def get_all(cls, db: Session):
        """
        Get all settings.

        Args:
            db: SQLAlchemy session

        Returns:
            List of Setting objects
        """
        return db.query(cls).all()
