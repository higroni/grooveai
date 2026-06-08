"""
Data models for temporal linking.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date


class TemporalElement(BaseModel):
    """Represents a temporal element (deadline, duration, date)."""
    type: str = Field(..., description="Type: deadline, duration, effective_date, expiry_date")
    value: str = Field(..., description="Temporal value (e.g., '30 dana', '2025-01-01')")
    reference_point: Optional[str] = Field(None, description="Reference point (e.g., 'od dana dostavljanja')")
    is_mandatory: bool = Field(default=True, description="Whether this temporal constraint is mandatory")
    can_be_extended: bool = Field(default=False, description="Whether this deadline can be extended")
    applies_to: Optional[str] = Field(None, description="ID of obligation/prohibition/permission this applies to")
    source_text: str = Field(..., description="Original text")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class LinkedObligation(BaseModel):
    """Obligation with linked temporal elements."""
    subject: str
    action: str
    object: Optional[str]
    modality: str
    condition: Optional[str]
    temporal_elements: list[TemporalElement] = Field(default_factory=list)
    source_text: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class LinkedProhibition(BaseModel):
    """Prohibition with linked temporal elements."""
    subject: str
    action: str
    object: Optional[str]
    modality: str
    exception: Optional[str]
    temporal_elements: list[TemporalElement] = Field(default_factory=list)
    source_text: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class LinkedPermission(BaseModel):
    """Permission with linked temporal elements."""
    subject: str
    action: str
    object: Optional[str]
    modality: str
    condition: Optional[str]
    temporal_elements: list[TemporalElement] = Field(default_factory=list)
    source_text: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class TemporalLinkingResult(BaseModel):
    """Result of temporal linking."""
    linked_obligations: list[LinkedObligation] = Field(default_factory=list)
    linked_prohibitions: list[LinkedProhibition] = Field(default_factory=list)
    linked_permissions: list[LinkedPermission] = Field(default_factory=list)
    unlinked_temporal_elements: list[TemporalElement] = Field(default_factory=list)
    processing_time: float = Field(..., description="Processing time in seconds")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'linked_obligations': [o.model_dump() for o in self.linked_obligations],
            'linked_prohibitions': [p.model_dump() for p in self.linked_prohibitions],
            'linked_permissions': [p.model_dump() for p in self.linked_permissions],
            'unlinked_temporal_elements': [t.model_dump() for t in self.unlinked_temporal_elements],
            'processing_time': self.processing_time
        }

# Made with Bob
