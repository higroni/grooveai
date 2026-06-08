"""
Data models for Qdrant Loader module
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class LegalUnitPayload(BaseModel):
    """Payload for legal_units collection"""
    # Identifiers
    document_id: str = Field(..., description="Document identifier")
    legal_unit_id: str = Field(..., description="Unique legal unit ID")
    parent_legal_unit_id: Optional[str] = Field(None, description="Parent unit ID")
    document_legal_unit_id: str = Field(..., description="Document-level unit ID")
    
    # Hierarchy
    unit_type: str = Field(..., description="Type of legal unit (article, paragraph, etc.)")
    hierarchy_level: int = Field(..., description="Depth in hierarchy (0=document, 1=article, etc.)")
    hierarchy_path: str = Field(..., description="Full path in hierarchy")
    
    # Content
    title: Optional[str] = Field(None, description="Unit title")
    content: str = Field(..., description="Full text content")
    content_latinized: str = Field(..., description="Latinized text content")
    
    # Metadata
    document_title: str = Field(..., description="Parent document title")
    document_type: str = Field(..., description="Document type (zakon, uredba, etc.)")
    effective_date: Optional[str] = Field(None, description="When this unit becomes effective")
    
    # Statistics
    char_count: int = Field(..., description="Character count")
    word_count: int = Field(..., description="Word count")
    
    # Processing info
    processed_at: str = Field(..., description="When this was processed")


class NormativeContentPayload(BaseModel):
    """Payload for normative_content collection"""
    # Link to legal unit
    document_id: str = Field(..., description="Document identifier")
    legal_unit_id: str = Field(..., description="Source legal unit ID")
    document_legal_unit_id: str = Field(..., description="Document-level unit ID")
    
    # Normative content
    normative_type: str = Field(..., description="Type: obligation, prohibition, right, etc.")
    normative_text: str = Field(..., description="Extracted normative text")
    normative_text_latinized: str = Field(..., description="Latinized normative text")
    
    # Context
    unit_type: str = Field(..., description="Source unit type")
    hierarchy_path: str = Field(..., description="Source hierarchy path")
    document_title: str = Field(..., description="Parent document title")
    document_type: str = Field(..., description="Document type")
    
    # Conditions (if any)
    has_conditions: bool = Field(False, description="Whether this has conditions")
    condition_count: int = Field(0, description="Number of conditions")
    
    # Processing info
    processed_at: str = Field(..., description="When this was processed")


class DocumentMetadataPayload(BaseModel):
    """Payload for document_metadata collection"""
    # Document identifiers
    document_id: str = Field(..., description="Document identifier")
    document_legal_unit_id: str = Field(..., description="Document-level unit ID")
    
    # Document info
    title: str = Field(..., description="Document title")
    document_type: str = Field(..., description="Document type")
    effective_date: Optional[str] = Field(None, description="Effective date")
    
    # Statistics
    total_units: int = Field(..., description="Total legal units")
    total_normative: int = Field(..., description="Total normative assertions")
    total_conditions: int = Field(0, description="Total conditions")
    total_assertions: int = Field(0, description="Total assertions")
    
    # Content stats
    total_chars: int = Field(..., description="Total characters")
    total_words: int = Field(..., description="Total words")
    
    # Hierarchy stats
    max_hierarchy_depth: int = Field(..., description="Maximum hierarchy depth")
    unit_type_distribution: Dict[str, int] = Field(default_factory=dict, description="Count by unit type")
    
    # Processing info
    processed_at: str = Field(..., description="When this was processed")
    processing_time_seconds: Optional[float] = Field(None, description="Processing time")


class LoaderConfig(BaseModel):
    """Configuration for Qdrant loader"""
    qdrant_url: str = Field(default="http://localhost:6333", description="Qdrant server URL")
    qdrant_api_key: Optional[str] = Field(None, description="Qdrant API key (if using cloud)")
    
    # Collection names
    legal_units_collection: str = Field(default="legal_units", description="Legal units collection name")
    normative_collection: str = Field(default="normative_content", description="Normative content collection name")
    metadata_collection: str = Field(default="document_metadata", description="Document metadata collection name")
    
    # Vector settings
    vector_size: int = Field(default=768, description="Embedding vector size")
    distance_metric: str = Field(default="Cosine", description="Distance metric (Cosine, Euclid, Dot)")
    
    # Embedding model
    embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        description="Sentence transformer model for embeddings"
    )
    
    # Batch settings
    batch_size: int = Field(default=100, description="Batch size for uploads")
    recreate_collections: bool = Field(default=False, description="Whether to recreate collections")


class LoaderStats(BaseModel):
    """Statistics from loading process"""
    documents_processed: int = 0
    legal_units_loaded: int = 0
    normative_content_loaded: int = 0
    metadata_loaded: int = 0
    errors: List[str] = Field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "documents_processed": self.documents_processed,
            "legal_units_loaded": self.legal_units_loaded,
            "normative_content_loaded": self.normative_content_loaded,
            "metadata_loaded": self.metadata_loaded,
            "errors": self.errors,
            "duration_seconds": self.duration_seconds
        }

# Made with Bob
