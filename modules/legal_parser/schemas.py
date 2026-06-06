"""Pydantic schemas for Legal Parser module - Akoma Ntoso compatible."""

from typing import Any
from pydantic import BaseModel, Field


# Akoma Ntoso-compatible Legal Unit
class LegalUnit(BaseModel):
    """
    Akoma Ntoso-compatible legal unit.
    Maps directly to Akoma Ntoso XML elements.
    """
    legal_unit_id: str = Field(..., description="UUID (deterministic from path)")
    parent_legal_unit_id: str | None = Field(None, description="Parent UUID (hierarchy)")
    
    # Akoma Ntoso core fields
    unit_type: str = Field(..., description="article, paragraph, point, list, indent")
    number: str = Field(..., description="Unit number (e.g., '1', '2', '1a')")
    ordinal: int = Field(..., description="Sequential order (1, 2, 3...)")
    heading: str | None = Field(None, description="Heading/title (e.g., 'Predmet zakona')")
    content_text: str = Field(..., description="Content text")
    path: str = Field(..., description="Hierarchical path (e.g., 'article:1/paragraph:1')")
    
    # Akoma Ntoso metadata
    akoma_eid: str = Field(..., description="Akoma Ntoso eId (e.g., 'article_1__para_1')")
    akoma_wid: str | None = Field(None, description="Akoma Ntoso wId (optional)")
    
    # Additional metadata
    metadata: dict[str, Any] = Field(default_factory=dict, description="Flexible metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "legal_unit_id": "550e8400-e29b-41d4-a716-446655440000",
                "parent_legal_unit_id": None,
                "unit_type": "article",
                "number": "1",
                "ordinal": 1,
                "heading": "Predmet zakona",
                "content_text": "",
                "path": "article:1",
                "akoma_eid": "article_1",
                "akoma_wid": None,
                "metadata": {}
            }
        }


# Document metadata (FRBR-compatible)
class DocumentMetadata(BaseModel):
    """Document metadata compatible with Akoma Ntoso FRBR model."""
    publication_date: str | None = None
    official_gazette: str | None = None
    enactment_date: str | None = None
    effective_date: str | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "publication_date": "2005-03-15",
                "official_gazette": "Službeni glasnik RS br. 24/2005",
                "enactment_date": "2005-03-15",
                "effective_date": "2005-03-23"
            }
        }


# Document container
class Document(BaseModel):
    """
    Akoma Ntoso-compatible document container.
    Maps to <act> element in Akoma Ntoso.
    """
    source_uri: str = Field(..., description="File path or URL")
    filename: str = Field(..., description="Original filename")
    document_type: str = Field(default="law", description="Document type (law, regulation, etc.)")
    title: str | None = Field(None, description="Document title")
    language_code: str = Field(default="sr", description="Language code (ISO 639-1)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Document metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "source_uri": "file:///documents/zakon_o_radu.pdf",
                "filename": "zakon_o_radu.pdf",
                "document_type": "law",
                "title": "Zakon o radu",
                "language_code": "sr",
                "metadata": {
                    "publication_date": "2005-03-15",
                    "official_gazette": "Službeni glasnik RS br. 24/2005"
                }
            }
        }


# Statistics
class ParsingStatistics(BaseModel):
    """Statistics about parsed legal units."""
    total_units: int = Field(..., description="Total legal units parsed")
    total_articles: int = Field(..., description="Number of articles")
    total_paragraphs: int = Field(..., description="Number of paragraphs")
    total_points: int = Field(..., description="Number of points")
    total_lists: int = Field(default=0, description="Number of lists/subpoints")
    total_indents: int = Field(default=0, description="Number of indents")

    class Config:
        json_schema_extra = {
            "example": {
                "total_units": 5,
                "total_articles": 1,
                "total_paragraphs": 2,
                "total_points": 2,
                "total_lists": 0,
                "total_indents": 0
            }
        }


# API Request/Response schemas

class ParseRequest(BaseModel):
    """Request to parse legal document."""
    text: str = Field(..., description="Latinized text to parse")
    source_uri: str = Field(..., description="Source file path or URL")
    filename: str = Field(..., description="Original filename")
    document_type: str = Field(default="law", description="Document type")
    language_code: str = Field(default="sr", description="Language code")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Clan 1.\nPredmet zakona\n(1) Ovim zakonom...",
                "source_uri": "file:///documents/zakon_o_radu.pdf",
                "filename": "zakon_o_radu.pdf",
                "document_type": "law",
                "language_code": "sr"
            }
        }


class ParseOutput(BaseModel):
    """Output from parsing operation."""
    document: Document = Field(..., description="Document metadata")
    legal_units: list[LegalUnit] = Field(..., description="Parsed legal units")
    statistics: ParsingStatistics = Field(..., description="Parsing statistics")


class ParseResponse(BaseModel):
    """Response from parse endpoint."""
    module: str = Field(default="legal-parser", description="Module name")
    status: str = Field(..., description="Status (success/error)")
    job_id: int = Field(..., description="Job ID")
    output: ParseOutput = Field(..., description="Parsed output")
    metadata: dict[str, Any] = Field(..., description="Processing metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "module": "legal-parser",
                "status": "success",
                "job_id": 1,
                "output": {
                    "document": {
                        "source_uri": "file:///documents/zakon_o_radu.pdf",
                        "filename": "zakon_o_radu.pdf",
                        "document_type": "law",
                        "title": "Zakon o radu",
                        "language_code": "sr",
                        "metadata": {}
                    },
                    "legal_units": [],
                    "statistics": {
                        "total_units": 0,
                        "total_articles": 0,
                        "total_paragraphs": 0,
                        "total_points": 0
                    }
                },
                "metadata": {
                    "processing_time_ms": 145.5
                }
            }
        }


class JobResponse(BaseModel):
    """Response for job retrieval."""
    job_id: int = Field(..., description="Job ID")
    document: Document = Field(..., description="Document metadata")
    legal_units: list[LegalUnit] = Field(..., description="Parsed legal units")
    statistics: ParsingStatistics = Field(..., description="Parsing statistics")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    created_at: str = Field(..., description="Creation timestamp (ISO 8601)")


class JobListResponse(BaseModel):
    """Response for job list."""
    jobs: list[JobResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")


class StatsResponse(BaseModel):
    """Response for statistics endpoint."""
    total_jobs: int = Field(..., description="Total number of jobs")
    total_units_parsed: int = Field(..., description="Total legal units parsed")
    total_articles: int = Field(..., description="Total articles parsed")
    total_paragraphs: int = Field(..., description="Total paragraphs parsed")
    total_points: int = Field(..., description="Total points parsed")
    avg_processing_time_ms: float = Field(..., description="Average processing time")


class HealthResponse(BaseModel):
    """Response for health check."""
    status: str = Field(..., description="Health status")
    module: str = Field(..., description="Module name")
    version: str = Field(..., description="Module version")


class DeleteResponse(BaseModel):
    """Response for delete operation."""
    message: str = Field(..., description="Success message")

# Made with Bob
