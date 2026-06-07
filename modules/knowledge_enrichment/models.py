"""
Knowledge Enrichment Module - Data Models
Defines Pydantic models for ontology, references, and definitions
"""

from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RelationshipType(str, Enum):
    """Types of ontology relationships"""
    BROADER_THAN = "broader_than"
    NARROWER_THAN = "narrower_than"
    RELATED_TO = "related_to"
    SYNONYM_OF = "synonym_of"


class OntologyTerm(BaseModel):
    """Ontology term model"""
    id: Optional[int] = None
    canonical_form: str = Field(..., description="Canonical form of the term")
    label: str = Field(..., description="Display label")
    domain: Optional[str] = Field(None, description="Legal domain (e.g., 'criminal', 'civil')")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    frequency: int = Field(default=1, ge=1, description="Usage frequency")
    source: str = Field(default="manual", description="Source of the term (manual, ner, auto)")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OntologyRelationship(BaseModel):
    """Ontology relationship model"""
    id: Optional[int] = None
    term1_id: int = Field(..., description="First term ID")
    term2_id: int = Field(..., description="Second term ID")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    created_at: Optional[datetime] = None


class LegalReference(BaseModel):
    """Legal reference model"""
    id: Optional[int] = None
    assertion_id: str = Field(..., description="ID of the assertion containing the reference (UUID)")
    raw_reference: str = Field(..., description="Raw reference text (e.g., 'Član 5. Zakona o...')")
    document_type: Optional[str] = Field(None, description="Type of document (zakon, uredba, etc.)")
    document_name: Optional[str] = Field(None, description="Name of the referenced document")
    article_number: Optional[str] = Field(None, description="Article number")
    paragraph_number: Optional[str] = Field(None, description="Paragraph number")
    item_number: Optional[str] = Field(None, description="Item number")
    external_url: Optional[str] = Field(None, description="URL to external legal database")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    created_at: Optional[datetime] = None


class TermDefinition(BaseModel):
    """Term definition model"""
    id: Optional[int] = None
    assertion_id: str = Field(..., description="ID of the assertion containing the definition (UUID)")
    term: str = Field(..., description="The term being defined")
    definition: str = Field(..., description="The definition text")
    definition_pattern: Optional[str] = Field(None, description="Pattern used to extract (e.g., 'X znači')")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    created_at: Optional[datetime] = None


class EnrichedAssertion(BaseModel):
    """Enriched assertion with ontology, references, and definitions"""
    assertion_id: str = Field(..., description="Original assertion ID (UUID)")
    text: str = Field(..., description="Assertion text")
    
    @property
    def assertion_text(self) -> str:
        """Alias for text field for backward compatibility"""
        return self.text
    
    # Ontology enrichment
    matched_terms: List[Dict[str, Any]] = Field(default_factory=list, description="Matched ontology terms")
    
    # Reference enrichment
    legal_references: List[LegalReference] = Field(default_factory=list, description="Resolved legal references")
    
    # Definition enrichment
    term_definitions: List[TermDefinition] = Field(default_factory=list, description="Extracted definitions")
    
    # Metadata
    enrichment_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = None


class EnrichmentRequest(BaseModel):
    """Request model for enrichment"""
    assertion_id: str = Field(..., description="Assertion ID to enrich (UUID or integer)")
    assertion_text: str = Field(..., description="Assertion text")
    entities: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Recognized entities from M7")
    use_classla: bool = Field(default=True, description="Whether to use CLASSLA NER for additional entity extraction")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('assertion_id', mode='before')
    @classmethod
    def convert_assertion_id(cls, v):
        """Convert assertion_id to string if it's an integer"""
        if isinstance(v, int):
            return str(v)
        return v
    
    @model_validator(mode='before')
    @classmethod
    def handle_field_aliases(cls, data: Any) -> Any:
        """Transform input data to handle different field names from upstream modules"""
        if isinstance(data, dict):
            # Handle text -> assertion_text
            if 'text' in data and 'assertion_text' not in data:
                data['assertion_text'] = data['text']
        return data


class EnrichmentResponse(BaseModel):
    """Response model for enrichment"""
    success: bool = Field(..., description="Whether enrichment was successful")
    enriched_assertion: Optional[EnrichedAssertion] = None
    error: Optional[str] = None
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class BatchEnrichmentRequest(BaseModel):
    """Batch enrichment request"""
    assertions: List[EnrichmentRequest] = Field(..., description="List of assertions to enrich")
    
    @model_validator(mode='before')
    @classmethod
    def transform_assertions(cls, data: Any) -> Any:
        """Transform assertions data before validation"""
        if isinstance(data, dict) and 'assertions' in data:
            assertions = data['assertions']
            if isinstance(assertions, list):
                # Transform each assertion
                transformed = []
                for assertion in assertions:
                    if isinstance(assertion, dict):
                        # Handle text -> assertion_text
                        if 'text' in assertion and 'assertion_text' not in assertion:
                            assertion['assertion_text'] = assertion['text']
                        transformed.append(assertion)
                    else:
                        transformed.append(assertion)
                data['assertions'] = transformed
        return data


class BatchEnrichmentResult(BaseModel):
    """Result for a single assertion in batch enrichment"""
    assertion_id: str = Field(..., description="Assertion ID (UUID or integer)")
    status: str = Field(..., description="Status: success or error")
    enriched_assertion: Optional[EnrichedAssertion] = Field(None, description="Enriched assertion if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time_ms: float = Field(..., description="Processing time for this assertion in milliseconds")


class BatchEnrichmentResponse(BaseModel):
    """Batch enrichment response with detailed timing metrics"""
    module: str = Field(default="knowledge-enrichment", description="Module name")
    status: str = Field(..., description="Overall status: success, partial, or error")
    total_assertions: int = Field(..., description="Total number of assertions processed")
    successful: int = Field(default=0, description="Number of successful enrichments")
    failed: int = Field(default=0, description="Number of failed enrichments")
    results: List[BatchEnrichmentResult] = Field(default_factory=list, description="Individual results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Batch processing metadata with timing metrics")


class OntologyMatchRequest(BaseModel):
    """Request for ontology matching"""
    text: str = Field(..., description="Text to match against ontology")
    entities: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Pre-extracted entities")
    auto_learn: bool = Field(default=True, description="Whether to auto-learn new terms")


class OntologyMatchResponse(BaseModel):
    """Response for ontology matching"""
    matched_terms: List[Dict[str, Any]] = Field(default_factory=list, description="Matched terms with scores")
    new_terms_learned: int = Field(default=0, description="Number of new terms learned")
    processing_time_ms: float = Field(..., description="Processing time")


class ReferenceResolutionRequest(BaseModel):
    """Request for reference resolution"""
    text: str = Field(..., description="Text containing legal references")


class ReferenceResolutionResponse(BaseModel):
    """Response for reference resolution"""
    references: List[LegalReference] = Field(default_factory=list, description="Resolved references")
    processing_time_ms: float = Field(..., description="Processing time")


class DefinitionExtractionRequest(BaseModel):
    """Request for definition extraction"""
    text: str = Field(..., description="Text containing definitions")


class DefinitionExtractionResponse(BaseModel):
    """Response for definition extraction"""
    definitions: List[TermDefinition] = Field(default_factory=list, description="Extracted definitions")
    processing_time_ms: float = Field(..., description="Processing time")

# Made with Bob
