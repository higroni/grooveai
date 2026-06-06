"""
Database models for Latinizer module.

This module defines the SQLAlchemy models for storing latinization jobs.
"""

from sqlalchemy import Integer, String, Text, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    """Base class for all models in this module."""
    pass


class LatinizerJob(Base):
    """
    Model for storing latinization jobs.
    
    Stores information about Cyrillic to Latin text conversion including:
    - Input text (Cyrillic)
    - Output text (Latin)
    - Processing metrics
    """
    
    __tablename__ = "latinizer_jobs"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Input/Output data
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Statistics
    cyrillic_chars_converted: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Processing metrics
    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return (
            f"<LatinizerJob(id={self.id}, "
            f"input_len={len(self.input_text)}, output_len={len(self.output_text)}, "
            f"converted={self.cyrillic_chars_converted})>"
        )

# Made with Bob
