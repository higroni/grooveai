"""
Data models for Condition Extractor module.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Assertion(BaseModel):
    """Input assertion model."""
    assertion_id: str = Field(..., description="Unique assertion identifier")
    text: str = Field(..., description="Assertion text")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Assertion confidence score")


class ExtractedCondition(BaseModel):
    """Model for a single extracted condition."""
    condition_id: str = Field(..., description="Unique condition identifier")
    condition_type: str = Field(..., description="Type: 'condition', 'exception', 'temporal', 'modal'")
    text: str = Field(..., description="Condition text")
    start_char: int = Field(..., description="Start character position in assertion")
    end_char: int = Field(..., description="End character position in assertion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    trigger_word: str = Field(..., description="Word that triggered condition detection")
    context: Optional[str] = Field(None, description="Surrounding context")


class ConditionExtractionRequest(BaseModel):
    """Request model for condition extraction."""
    assertion: Assertion = Field(..., description="Assertion to extract conditions from")
    language: str = Field(default="sr", description="Language code (sr, en)")
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    extract_conditions: bool = Field(default=True, description="Extract conditional clauses")
    extract_exceptions: bool = Field(default=True, description="Extract exception clauses")
    extract_temporal: bool = Field(default=True, description="Extract temporal conditions")
    extract_modal: bool = Field(default=True, description="Extract modal conditions")


class ConditionExtractionOutput(BaseModel):
    """Output model for condition extraction."""
    conditions: List[ExtractedCondition] = Field(default_factory=list, description="Extracted conditions")
    total_conditions: int = Field(..., description="Total number of conditions extracted")
    total_exceptions: int = Field(..., description="Total number of exceptions extracted")
    total_temporal: int = Field(..., description="Total number of temporal conditions")
    total_modal: int = Field(..., description="Total number of modal conditions")
    average_confidence: float = Field(..., description="Average confidence score")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class ConditionExtractionResponse(BaseModel):
    """Response model for condition extraction."""
    job_id: str = Field(..., description="Unique job identifier")
    assertion_id: str = Field(..., description="Assertion identifier")
    output: ConditionExtractionOutput = Field(..., description="Extraction output")
    status: str = Field(default="completed", description="Job status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class BatchConditionExtractionRequest(BaseModel):
    """Request model for batch condition extraction."""
    assertions: List[Assertion] = Field(..., description="List of assertions to process")
    language: str = Field(default="sr", description="Language code (sr, en)")
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    extract_conditions: bool = Field(default=True, description="Extract conditional clauses")
    extract_exceptions: bool = Field(default=True, description="Extract exception clauses")
    extract_temporal: bool = Field(default=True, description="Extract temporal conditions")
    extract_modal: bool = Field(default=True, description="Extract modal conditions")
    batch_size: int = Field(default=100, ge=1, le=200, description="Batch size for processing")


class BatchConditionExtractionResult(BaseModel):
    """Result for a single assertion in batch processing."""
    assertion_id: str = Field(..., description="Assertion ID")
    status: str = Field(..., description="Status (success, error)")
    output: Optional[ConditionExtractionOutput] = Field(None, description="Extraction output if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class BatchConditionExtractionResponse(BaseModel):
    """Response model for batch condition extraction."""
    module: str = Field(default="condition-extractor", description="Module name")
    status: str = Field(..., description="Overall status (success, partial, error)")
    job_id: str = Field(..., description="Batch job ID")
    results: List[BatchConditionExtractionResult] = Field(..., description="Results for each assertion")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata with detailed timing")



class ConditionExtractionJob(BaseModel):
    """Database model for condition extraction job."""
    job_id: str
    assertion_id: str
    assertion_text: str
    output_conditions: str  # JSON string
    total_conditions: int
    total_exceptions: int
    total_temporal: int
    total_modal: int
    average_confidence: float
    processing_time_ms: float
    created_at: datetime


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy", description="Service status")
    module: str = Field(default="condition_extractor", description="Module name")
    version: str = Field(default="1.0.0", description="Module version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current timestamp")

# Made with Bob
