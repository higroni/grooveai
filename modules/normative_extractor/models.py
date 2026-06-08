"""
Data models for normative extraction.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Obligation(BaseModel):
    """Represents a legal obligation."""
    subject: str = Field(..., description="Who has the obligation (e.g., 'Poslodavac')")
    action: str = Field(..., description="What action must be performed (e.g., 'isplati')")
    object: Optional[str] = Field(None, description="Object of the action (e.g., 'zaradu')")
    modality: str = Field(..., description="Modal expression (e.g., 'dužan je', 'mora')")
    condition: Optional[str] = Field(None, description="Condition for the obligation")
    temporal: Optional[Dict[str, Any]] = Field(None, description="Temporal constraints")
    source_text: str = Field(..., description="Original text")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class Prohibition(BaseModel):
    """Represents a legal prohibition."""
    subject: str = Field(..., description="Who is prohibited")
    action: str = Field(..., description="What action is prohibited")
    object: Optional[str] = Field(None, description="Object of the action")
    modality: str = Field(..., description="Modal expression (e.g., 'zabranjeno je', 'ne sme')")
    exception: Optional[str] = Field(None, description="Exception to the prohibition")
    source_text: str = Field(..., description="Original text")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class Permission(BaseModel):
    """Represents a legal permission."""
    subject: str = Field(..., description="Who has the permission")
    action: str = Field(..., description="What action is permitted")
    object: Optional[str] = Field(None, description="Object of the action")
    modality: str = Field(..., description="Modal expression (e.g., 'može', 'ima pravo')")
    condition: Optional[str] = Field(None, description="Condition for the permission")
    source_text: str = Field(..., description="Original text")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class Definition(BaseModel):
    """Represents a legal definition."""
    term: str = Field(..., description="Term being defined")
    definition: str = Field(..., description="Definition text")
    scope: Optional[str] = Field(None, description="Scope of the definition (e.g., 'u smislu ovog zakona')")
    source_text: str = Field(..., description="Original text")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class Waiver(BaseModel):
    """Represents a waiver of rights."""
    subject: str = Field(..., description="Who waives the right")
    right: str = Field(..., description="What right is being waived")
    waivable: bool = Field(..., description="Whether the right can be waived")
    condition: Optional[str] = Field(None, description="Condition for waiver")
    source_text: str = Field(..., description="Original text")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class Transfer(BaseModel):
    """Represents a transfer of rights or obligations."""
    from_party: str = Field(..., description="Who transfers")
    to_party: str = Field(..., description="Who receives")
    subject: str = Field(..., description="What is being transferred")
    transferable: bool = Field(..., description="Whether transfer is allowed")
    condition: Optional[str] = Field(None, description="Condition for transfer")
    source_text: str = Field(..., description="Original text")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class Assignment(BaseModel):
    """Represents an assignment."""
    assignor: str = Field(..., description="Who assigns")
    assignee: Optional[str] = Field(None, description="Who receives assignment")
    subject: str = Field(..., description="What is being assigned")
    requires_consent: bool = Field(default=False, description="Whether consent is required")
    condition: Optional[str] = Field(None, description="Condition for assignment")
    source_text: str = Field(..., description="Original text")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class AmbiguityScore(BaseModel):
    """Represents ambiguity analysis of a normative statement."""
    statement_type: str = Field(..., description="Type: obligation, prohibition, permission")
    statement_id: str = Field(..., description="ID of the statement")
    ambiguity_score: float = Field(..., ge=0.0, le=1.0, description="Ambiguity score (0=clear, 1=very ambiguous)")
    ambiguous_terms: List[str] = Field(default_factory=list, description="List of ambiguous terms found")
    source_text: str = Field(..., description="Original text")


class CircularDefinition(BaseModel):
    """Represents a circular definition."""
    term1: str = Field(..., description="First term")
    term2: str = Field(..., description="Second term")
    definition1: str = Field(..., description="Definition of first term")
    definition2: str = Field(..., description="Definition of second term")
    source_text: str = Field(..., description="Combined source text")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class NormativeContent(BaseModel):
    """Complete normative content extracted from text."""
    obligations: List[Obligation] = Field(default_factory=list)
    prohibitions: List[Prohibition] = Field(default_factory=list)
    permissions: List[Permission] = Field(default_factory=list)
    definitions: List[Definition] = Field(default_factory=list)
    waivers: List[Waiver] = Field(default_factory=list)
    transfers: List[Transfer] = Field(default_factory=list)
    assignments: List[Assignment] = Field(default_factory=list)
    ambiguity_scores: List[AmbiguityScore] = Field(default_factory=list)
    circular_definitions: List[CircularDefinition] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'obligations': [o.model_dump() for o in self.obligations],
            'prohibitions': [p.model_dump() for p in self.prohibitions],
            'permissions': [p.model_dump() for p in self.permissions],
            'definitions': [d.model_dump() for d in self.definitions],
            'waivers': [w.model_dump() for w in self.waivers],
            'transfers': [t.model_dump() for t in self.transfers],
            'assignments': [a.model_dump() for a in self.assignments],
            'ambiguity_scores': [a.model_dump() for a in self.ambiguity_scores],
            'circular_definitions': [c.model_dump() for c in self.circular_definitions]
        }
    
    @property
    def total_count(self) -> int:
        """Total number of extracted normative elements."""
        return (
            len(self.obligations) +
            len(self.prohibitions) +
            len(self.permissions) +
            len(self.definitions) +
            len(self.waivers) +
            len(self.transfers) +
            len(self.assignments) +
            len(self.ambiguity_scores) +
            len(self.circular_definitions)
        )


class ExtractionResult(BaseModel):
    """Result of normative extraction."""
    normative_content: NormativeContent
    processing_time: float = Field(..., description="Processing time in seconds")
    text_length: int = Field(..., description="Length of input text")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'normative_content': self.normative_content.to_dict(),
            'processing_time': self.processing_time,
            'text_length': self.text_length,
            'total_extracted': self.normative_content.total_count
        }

# Made with Bob
