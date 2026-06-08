"""
Data models for legal hierarchy classification.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class LegalDocument(BaseModel):
    """Represents a legal document with hierarchy information."""
    document_type: str = Field(..., description="Type: zakon, pravilnik, uredba, odluka, naređenje, ustav")
    hierarchy_level: int = Field(..., description="Hierarchy level (1=highest, 6=lowest)")
    issuing_authority: Optional[str] = Field(None, description="Authority that issued the document")
    legal_basis: List[str] = Field(default_factory=list, description="Legal basis references")
    official_gazette: Optional[str] = Field(None, description="Official gazette reference")
    can_override: List[str] = Field(default_factory=list, description="Document types this can override")
    cannot_override: List[str] = Field(default_factory=list, description="Document types this cannot override")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class HierarchyClassificationResult(BaseModel):
    """Result of legal hierarchy classification."""
    document: LegalDocument
    title: Optional[str] = Field(None, description="Document title")
    detected_patterns: List[str] = Field(default_factory=list, description="Patterns that matched")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'document': self.document.model_dump(),
            'title': self.title,
            'detected_patterns': self.detected_patterns,
            'processing_time': self.processing_time
        }

# Made with Bob
