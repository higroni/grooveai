"""
Database models for Embedding Generator module.

This module defines the SQLAlchemy models for storing embedding generation jobs.
"""

from sqlalchemy import Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    """Base class for all models in this module."""
    pass


class EmbeddingJob(Base):
    """
    Model for storing embedding generation jobs.
    
    Stores information about text embedding generation including:
    - Input text and metadata
    - Generated embeddings (as JSON array)
    - Model information
    - Processing metrics
    """
    
    __tablename__ = "embedding_jobs"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Job identification
    job_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Input data
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    text_length: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Model information
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Output data - stored as JSON array
    embeddings: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string of float array
    
    # Processing metrics
    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return (
            f"<EmbeddingJob(id={self.id}, job_id='{self.job_id}', "
            f"model='{self.model_name}', dim={self.embedding_dimension}, "
            f"text_len={self.text_length})>"
        )

# Made with Bob
