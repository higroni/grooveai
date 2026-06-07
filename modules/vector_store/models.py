"""
Database models for Vector Store module.

This module defines the SQLAlchemy models for storing embedding generation jobs.
Supports both assertion-level and document-level embeddings with rich metadata.
"""

from sqlalchemy import Integer, String, Text, Float, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import Optional
import enum


class Base(DeclarativeBase):
    """Base class for all models in this module."""
    pass


class EmbeddingType(str, enum.Enum):
    """Type of embedding."""
    ASSERTION = "assertion"  # Assertion-level embedding (primary)
    DOCUMENT = "document"    # Document-level embedding (secondary)
    CHUNK = "chunk"          # Generic chunk embedding


class EmbeddingJob(Base):
    """
    Model for storing embedding generation jobs.
    
    Stores information about text embedding generation including:
    - Input text and metadata
    - Generated embeddings (as JSON array)
    - Model information
    - Processing metrics
    - Rich metadata for vector DB filtering
    """
    
    __tablename__ = "embedding_jobs"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Job identification
    job_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Embedding type
    embedding_type: Mapped[str] = mapped_column(
        SQLEnum(EmbeddingType),
        nullable=False,
        default=EmbeddingType.ASSERTION,
        index=True
    )
    
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
    
    # Rich metadata for vector DB (stored as JSON)
    embedding_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    
    # Source tracking
    source_document: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_article: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Assertion-specific metadata (for quick filtering)
    assertion_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    assertion_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return (
            f"<EmbeddingJob(id={self.id}, job_id='{self.job_id}', "
            f"type='{self.embedding_type}', model='{self.model_name}', "
            f"dim={self.embedding_dimension}, text_len={self.text_length})>"
        )

# Made with Bob

