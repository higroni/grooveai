"""
Data models for Assertion Extractor module.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Integer, Text, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class LegalUnitInput(BaseModel):
    """Input legal unit for assertion extraction."""
    unit_id: str = Field(..., description="Legal unit ID")
    content: str = Field(..., description="Legal unit content text")
    unit_type: Optional[str] = Field(None, description="Type of legal unit (article, paragraph, etc.)")
    number: Optional[str] = Field(None, description="Legal unit number")


class Assertion(BaseModel):
    """Extracted assertion from legal unit."""
    assertion_id: str = Field(..., description="Unique assertion ID")
    text: str = Field(..., description="Assertion text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    sentence_index: int = Field(..., description="Index of sentence in original text")
    start_char: int = Field(..., description="Start character position in original text")
    end_char: int = Field(..., description="End character position in original text")


class ExtractionStats(BaseModel):
    """Statistics about extraction process."""
    total_assertions: int = Field(..., description="Total number of assertions extracted")
    total_sentences: int = Field(..., description="Total number of sentences processed")
    avg_confidence: float = Field(..., description="Average confidence score")


class ExtractionOutput(BaseModel):
    """Output from assertion extraction."""
    assertions: list[Assertion] = Field(default_factory=list, description="List of extracted assertions")
    stats: ExtractionStats = Field(..., description="Extraction statistics")


class ExtractionRequest(BaseModel):
    """Request for assertion extraction."""
    legal_unit: LegalUnitInput = Field(..., description="Legal unit to extract assertions from")
    language: str = Field(default="sr", description="Language code (sr, en, etc.)")
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")


class ExtractionResponse(BaseModel):
    """Response from assertion extraction."""
    module: str = Field(default="assertion-extractor", description="Module name")
    status: str = Field(..., description="Status (success, error)")
    job_id: str = Field(..., description="Job ID")
    output: ExtractionOutput = Field(..., description="Extraction output")
    metadata: dict = Field(default_factory=dict, description="Processing metadata")

class BatchExtractionRequest(BaseModel):
    """Request for batch assertion extraction."""
    legal_units: list[LegalUnitInput] = Field(..., description="List of legal units to process")
    language: str = Field(default="sr", description="Language code (sr, en, etc.)")
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    batch_size: int = Field(default=50, ge=1, le=100, description="Batch size for processing")


class BatchExtractionResult(BaseModel):
    """Result for a single legal unit in batch processing."""
    legal_unit_id: str = Field(..., description="Legal unit ID")
    status: str = Field(..., description="Status (success, error)")
    output: Optional[ExtractionOutput] = Field(None, description="Extraction output if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class BatchExtractionResponse(BaseModel):
    """Response from batch assertion extraction."""
    module: str = Field(default="assertion-extractor", description="Module name")
    status: str = Field(..., description="Overall status (success, partial, error)")
    job_id: str = Field(..., description="Batch job ID")
    results: list[BatchExtractionResult] = Field(..., description="Results for each legal unit")
    metadata: dict = Field(default_factory=dict, description="Processing metadata with detailed timing")



class ExtractionJobPydantic(BaseModel):
    """Pydantic model for extraction job API."""
    job_id: str = Field(..., description="Job ID")
    legal_unit_id: str = Field(..., description="Legal unit ID")
    input_content: str = Field(..., description="Input content")
    output_assertions: str = Field(..., description="Output assertions (JSON)")
    total_assertions: int = Field(..., description="Total assertions extracted")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class ExtractedAssertion(BaseModel):
    """Pydantic model for extracted assertion API."""
    assertion_id: str = Field(..., description="Assertion ID")
    job_id: str = Field(..., description="Job ID")
    text: str = Field(..., description="Assertion text")
    confidence: float = Field(..., description="Confidence score")
    sentence_index: int = Field(..., description="Sentence index")
    start_char: int = Field(..., description="Start character position")
    end_char: int = Field(..., description="End character position")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


# SQLAlchemy models for database
class ExtractionJob(Base):
    """
    SQLAlchemy model for extraction job.
    Stores assertion extraction jobs in database.
    """
    __tablename__ = "extraction_jobs"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Job data
    job_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    legal_unit_id: Mapped[str] = mapped_column(Text, nullable=False)
    input_content: Mapped[str] = mapped_column(Text, nullable=False)
    output_assertions: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Statistics
    total_assertions: Mapped[int] = mapped_column(Integer, nullable=False)
    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<ExtractionJob(id={self.id}, job_id='{self.job_id}', "
            f"total_assertions={self.total_assertions})>"
        )

# Made with Bob
