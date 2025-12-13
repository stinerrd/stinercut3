"""
Splashscreen model for SQLAlchemy.
Represents SVG templates (category='image') and font definitions (category='font').
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

from database import Base


class Splashscreen(Base):
    """
    Splashscreen model representing SVG content for PAX screen intros.

    Categories:
    - 'image': SVG template with placeholders [[[WIDTH]]], [[[HEIGHT]]], [[[TEXT]]]
    - 'font': SVG font definitions with character paths like <path id="_A" .../>
    """
    __tablename__ = "splashscreen"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # 'image' or 'font'
    svg_content = Column(Text, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Splashscreen(id={self.id}, name={self.name}, category={self.category})>"

    def is_image(self) -> bool:
        """Check if this splashscreen is an image template."""
        return self.category == 'image'

    def is_font(self) -> bool:
        """Check if this splashscreen is a font definition."""
        return self.category == 'font'
