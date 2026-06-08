"""
Data models for Conflict Detector module
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ConflictType(str, Enum):
    """Types of conflicts"""
    DIRECT_CONTRADICTION = "direct_contradiction"  # Direct contradiction in content
    NORMATIVE_CONFLICT = "normative_conflict"  # Conflicting obligations/prohibitions
    HIERARCHICAL_CONFLICT = "hierarchical_conflict"  # Lower law contradicts higher law
    TEMPORAL_CONFLICT = "temporal_conflict"  # Conflicting effective dates
    SEMANTIC_SIMILARITY = "semantic_similarity"  # High semantic similarity (potential overlap)
    DEFINITION_CONFLICT = "definition_conflict"  # Different definitions of same term


class ConflictSeverity(str, Enum):
    """Severity levels for conflicts"""
    CRITICAL = "critical"  # Must be resolved before adoption
    HIGH = "high"  # Should be resolved
    MEDIUM = "medium"  # Should be reviewed
    LOW = "low"  # Minor issue, informational


class Conflict(BaseModel):
    """A detected conflict between proposal and existing law"""
    # Conflict identification
    conflict_id: str = Field(..., description="Unique conflict identifier")
    conflict_type: ConflictType = Field(..., description="Type of conflict")
    severity: ConflictSeverity = Field(..., description="Severity level")
    
    # Proposal side
    proposal_unit_id: str = Field(..., description="Proposal legal unit ID")
    proposal_content: str = Field(..., description="Proposal content")
    proposal_hierarchy: str = Field(..., description="Proposal hierarchy path")
    
    # Existing law side
    existing_document_id: str = Field(..., description="Existing document ID")
    existing_document_title: str = Field(..., description="Existing document title")
    existing_unit_id: str = Field(..., description="Existing legal unit ID")
    existing_content: str = Field(..., description="Existing content")
    existing_hierarchy: str = Field(..., description="Existing hierarchy path")
    
    # Conflict details
    description: str = Field(..., description="Human-readable conflict description")
    explanation: str = Field(..., description="Detailed explanation of the conflict")
    similarity_score: float = Field(..., description="Semantic similarity score (0-1)")
    
    # Recommendations
    recommendation: Optional[str] = Field(None, description="Recommendation for resolution")
    
    # Metadata
    detected_at: str = Field(..., description="When this was detected")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "conflict_id": self.conflict_id,
            "conflict_type": self.conflict_type.value,
            "severity": self.severity.value,
            "proposal_unit_id": self.proposal_unit_id,
            "proposal_content": self.proposal_content[:200] + "..." if len(self.proposal_content) > 200 else self.proposal_content,
            "proposal_hierarchy": self.proposal_hierarchy,
            "existing_document_id": self.existing_document_id,
            "existing_document_title": self.existing_document_title,
            "existing_unit_id": self.existing_unit_id,
            "existing_content": self.existing_content[:200] + "..." if len(self.existing_content) > 200 else self.existing_content,
            "existing_hierarchy": self.existing_hierarchy,
            "description": self.description,
            "explanation": self.explanation,
            "similarity_score": self.similarity_score,
            "recommendation": self.recommendation,
            "detected_at": self.detected_at
        }


class ConflictDetectionResult(BaseModel):
    """Result of conflict detection"""
    # Summary
    total_conflicts: int = Field(..., description="Total number of conflicts detected")
    conflicts_by_severity: Dict[str, int] = Field(default_factory=dict, description="Count by severity")
    conflicts_by_type: Dict[str, int] = Field(default_factory=dict, description="Count by type")
    
    # Conflicts
    conflicts: List[Conflict] = Field(default_factory=list, description="List of detected conflicts")
    
    # Proposal info
    proposal_id: str = Field(..., description="Proposal identifier")
    proposal_title: str = Field(..., description="Proposal title")
    
    # Processing info
    documents_searched: int = Field(..., description="Number of documents searched")
    processing_time_seconds: float = Field(..., description="Processing time")
    detected_at: str = Field(..., description="When detection was performed")
    
    def get_critical_conflicts(self) -> List[Conflict]:
        """Get only critical conflicts"""
        return [c for c in self.conflicts if c.severity == ConflictSeverity.CRITICAL]
    
    def get_high_conflicts(self) -> List[Conflict]:
        """Get high severity conflicts"""
        return [c for c in self.conflicts if c.severity == ConflictSeverity.HIGH]
    
    def get_conflicts_by_type(self, conflict_type: ConflictType) -> List[Conflict]:
        """Get conflicts of specific type"""
        return [c for c in self.conflicts if c.conflict_type == conflict_type]
    
    def to_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        return {
            "proposal_id": self.proposal_id,
            "proposal_title": self.proposal_title,
            "total_conflicts": self.total_conflicts,
            "critical": self.conflicts_by_severity.get("critical", 0),
            "high": self.conflicts_by_severity.get("high", 0),
            "medium": self.conflicts_by_severity.get("medium", 0),
            "low": self.conflicts_by_severity.get("low", 0),
            "by_type": self.conflicts_by_type,
            "documents_searched": self.documents_searched,
            "processing_time": f"{self.processing_time_seconds:.2f}s",
            "detected_at": self.detected_at
        }


class ConflictDetectionConfig(BaseModel):
    """Configuration for conflict detection"""
    # Qdrant settings
    qdrant_url: str = Field(default="http://localhost:6333", description="Qdrant server URL")
    qdrant_api_key: Optional[str] = Field(None, description="Qdrant API key")
    
    # Collection names
    legal_units_collection: str = Field(default="legal_units", description="Legal units collection")
    normative_collection: str = Field(default="normative_content", description="Normative content collection")
    
    # Search settings
    similarity_threshold: float = Field(default=0.75, description="Minimum similarity for conflict (0-1)")
    max_results_per_unit: int = Field(default=5, description="Max similar units to check per proposal unit")
    
    # Conflict detection settings
    enable_direct_contradiction: bool = Field(default=True, description="Detect direct contradictions")
    enable_normative_conflict: bool = Field(default=True, description="Detect normative conflicts")
    enable_semantic_similarity: bool = Field(default=True, description="Detect semantic similarities")
    
    # Severity thresholds
    critical_threshold: float = Field(default=0.95, description="Similarity threshold for critical severity")
    high_threshold: float = Field(default=0.85, description="Similarity threshold for high severity")
    medium_threshold: float = Field(default=0.75, description="Similarity threshold for medium severity")
    
    # Embedding model
    embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        description="Sentence transformer model"
    )

# Made with Bob
