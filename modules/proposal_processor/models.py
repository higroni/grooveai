"""
Data models for Proposal Processor module
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path


class ProposalInput(BaseModel):
    """Input for proposal processing"""
    # Source can be file path, URL, or direct text
    source_type: Literal["file", "text", "url"] = Field(..., description="Type of input source")
    source: str = Field(..., description="File path, URL, or text content")
    
    # Metadata
    title: Optional[str] = Field(None, description="Proposal title (auto-detected if not provided)")
    document_type: str = Field(default="predlog_zakona", description="Document type")
    author: Optional[str] = Field(None, description="Proposal author/submitter")
    submission_date: Optional[str] = Field(None, description="Submission date")
    
    # Processing options
    skip_ocr: bool = Field(default=False, description="Skip OCR for scanned documents")
    force_reprocess: bool = Field(default=False, description="Force reprocessing even if cached")


class ProposalMetadata(BaseModel):
    """Metadata about the processed proposal"""
    proposal_id: str = Field(..., description="Unique proposal identifier")
    title: str = Field(..., description="Proposal title")
    document_type: str = Field(..., description="Document type")
    author: Optional[str] = Field(None, description="Proposal author")
    submission_date: Optional[str] = Field(None, description="Submission date")
    
    # Processing info
    processed_at: str = Field(..., description="When this was processed")
    processing_time_seconds: float = Field(..., description="Processing time")
    source_type: str = Field(..., description="Source type (file/text/url)")
    source: str = Field(..., description="Source reference")
    
    # Statistics
    total_chars: int = Field(..., description="Total characters")
    total_words: int = Field(..., description="Total words")
    total_units: int = Field(..., description="Total legal units")
    total_normative: int = Field(..., description="Total normative assertions")


class ProposalProcessingResult(BaseModel):
    """Result of proposal processing"""
    # Metadata
    metadata: ProposalMetadata = Field(..., description="Proposal metadata")
    
    # Processed data (same structure as regular documents)
    legal_units: List[Dict[str, Any]] = Field(default_factory=list, description="Parsed legal units")
    
    # Raw data
    raw_text: str = Field(..., description="Raw extracted text")
    latinized_text: str = Field(..., description="Latinized text")
    
    # Processing status
    success: bool = Field(..., description="Whether processing succeeded")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    warnings: List[str] = Field(default_factory=list, description="Any warnings")
    
    def to_json_export_format(self) -> Dict[str, Any]:
        """Convert to same format as regular document exports"""
        return {
            "document_metadata": {
                "document_id": self.metadata.proposal_id,
                "document_legal_unit_id": self.metadata.proposal_id,
                "title": self.metadata.title,
                "document_type": self.metadata.document_type,
                "effective_date": self.metadata.submission_date,
                "total_chars": self.metadata.total_chars,
                "total_words": self.metadata.total_words,
                "processed_at": self.metadata.processed_at,
                "processing_time_seconds": self.metadata.processing_time_seconds,
                "is_proposal": True,  # Flag to identify proposals
                "author": self.metadata.author,
                "source_type": self.metadata.source_type,
                "source": self.metadata.source
            },
            "legal_units": self.legal_units,
            "raw_text": self.raw_text,
            "latinized_text": self.latinized_text
        }

# Made with Bob
