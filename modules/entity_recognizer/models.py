"""
Data models for Entity Recognizer module.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy import Integer, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class AssertionInput(BaseModel):
    """Input assertion for entity recognition."""
    assertion_id: str = Field(..., description="Assertion ID")
    text: str = Field(..., description="Assertion text")
    confidence: Optional[float] = Field(None, description="Assertion confidence score")


class Entity(BaseModel):
    """Recognized entity from assertion."""
    entity_id: str = Field(..., description="Unique entity ID")
    entity_type: str = Field(..., description="Entity type (PERSON, ORGANIZATION, DATE, MONEY, LEGAL_REF, LOCATION, PERCENTAGE, DURATION)")
    text: str = Field(..., description="Entity text")
    start_char: int = Field(..., description="Start character position in assertion")
    end_char: int = Field(..., description="End character position in assertion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional entity metadata")


class RecognitionStats(BaseModel):
    """Statistics about entity recognition process."""
    total_entities: int = Field(..., description="Total number of entities recognized")
    entities_by_type: dict[str, int] = Field(default_factory=dict, description="Count of entities by type")
    avg_confidence: float = Field(..., description="Average confidence score")


class RecognitionOutput(BaseModel):
    """Output from entity recognition."""
    entities: List[Entity] = Field(default_factory=list, description="List of recognized entities")
    stats: RecognitionStats = Field(..., description="Recognition statistics")


class RecognitionRequest(BaseModel):
    """Request for entity recognition."""
    assertion: AssertionInput = Field(..., description="Assertion to extract entities from")
    language: str = Field(default="sr", description="Language code (sr, en, de)")
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    entity_types: Optional[List[str]] = Field(
        default=None,
        description="Specific entity types to extract (if None, extract all)"
    )
    use_ner: bool = Field(default=False, description="Use classla NER (True) or regex only (False)")


class RecognitionResponse(BaseModel):
    """Response from entity recognition."""
    job_id: str = Field(..., description="Recognition job ID")
    assertion_id: str = Field(..., description="Assertion ID")
    entities: List[Entity] = Field(default_factory=list, description="Recognized entities")
    stats: RecognitionStats = Field(..., description="Recognition statistics")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")


class BatchRecognitionRequest(BaseModel):
    """Request for batch entity recognition."""
    assertions: List[AssertionInput] = Field(..., description="List of assertions to process")
    language: str = Field(default="sr", description="Language code (sr, en, de)")
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    entity_types: Optional[List[str]] = Field(
        default=None,
        description="Specific entity types to extract (if None, extract all)"
    )
    use_ner: bool = Field(default=False, description="Use classla NER (True) or regex only (False)")
    batch_size: int = Field(default=100, ge=1, le=200, description="Batch size for processing")


class BatchRecognitionResult(BaseModel):
    """Result for a single assertion in batch processing."""
    assertion_id: str = Field(..., description="Assertion ID")
    status: str = Field(..., description="Status (success, error)")
    output: Optional[RecognitionOutput] = Field(None, description="Recognition output if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class BatchRecognitionResponse(BaseModel):
    """Response from batch entity recognition."""
    module: str = Field(default="entity-recognizer", description="Module name")
    status: str = Field(..., description="Overall status (success, partial, error)")
    job_id: str = Field(..., description="Batch job ID")
    results: List[BatchRecognitionResult] = Field(..., description="Results for each assertion")
    metadata: dict = Field(default_factory=dict, description="Processing metadata with detailed timing")



# SQLAlchemy models for database persistence
class RecognitionJob(Base):
    """Database model for recognition jobs."""
    __tablename__ = "recognition_jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    assertion_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    assertion_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_entities: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string (for backward compatibility)
    total_entities: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    language: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to entities
    entities: Mapped[list["EntityDB"]] = relationship("EntityDB", back_populates="job", cascade="all, delete-orphan")


class EntityDB(Base):
    """Database model for individual entities."""
    __tablename__ = "entities"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    job_id: Mapped[str] = mapped_column(Text, ForeignKey("recognition_jobs.job_id"), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_char: Mapped[int] = mapped_column(Integer, nullable=False)
    end_char: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string for metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to job
    job: Mapped["RecognitionJob"] = relationship("RecognitionJob", back_populates="entities")

# Made with Bob
