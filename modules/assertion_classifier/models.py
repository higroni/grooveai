"""
Data models for Assertion Classifier module.
Classifies assertions into types: obligation, prohibition, permission, deadline, definition.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Integer, Text, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Assertion(BaseModel):
    """Input assertion for classification."""
    assertion_id: str = Field(..., description="Unique assertion ID")
    text: str = Field(..., description="Assertion text to classify")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Original extraction confidence")


class ClassificationResult(BaseModel):
    """Classification result for an assertion."""
    assertion_id: str = Field(..., description="Assertion ID")
    assertion_type: str = Field(..., description="Classified type: obligation, prohibition, permission, deadline, definition")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")
    matched_patterns: list[str] = Field(default_factory=list, description="List of matched pattern names")
    reasoning: Optional[str] = Field(None, description="Explanation of classification")


class ClassificationOutput(BaseModel):
    """Output from assertion classification."""
    classification: ClassificationResult = Field(..., description="Classification result")
    stats: dict = Field(default_factory=dict, description="Classification statistics")


class ClassificationRequest(BaseModel):
    """Request for assertion classification."""
    assertion: Assertion = Field(..., description="Assertion to classify")
    language: str = Field(default="sr", description="Language code (sr, en)")
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")


class ClassificationResponse(BaseModel):
    """Response from classification API."""
    module: str = Field(default="assertion-classifier", description="Module name")
    status: str = Field(..., description="Status: success or error")
    job_id: str = Field(..., description="Unique job ID")
    output: ClassificationOutput = Field(..., description="Classification output")
    metadata: dict = Field(default_factory=dict, description="Processing metadata")


# SQLAlchemy Models for Database

class ClassificationJobDB(Base):
    """Database model for classification jobs."""
    __tablename__ = "classification_jobs"
    
    job_id: Mapped[str] = mapped_column(Text, primary_key=True)
    assertion_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    assertion_text: Mapped[str] = mapped_column(Text, nullable=False)
    assertion_type: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    matched_patterns: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(Text, nullable=False)
    processing_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ClassificationStatsDB(Base):
    """Database model for classification statistics."""
    __tablename__ = "classification_stats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    total_classifications: Mapped[int] = mapped_column(Integer, default=0)
    obligation_count: Mapped[int] = mapped_column(Integer, default=0)
    prohibition_count: Mapped[int] = mapped_column(Integer, default=0)
    permission_count: Mapped[int] = mapped_column(Integer, default=0)
    deadline_count: Mapped[int] = mapped_column(Integer, default=0)
    definition_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# Made with Bob
