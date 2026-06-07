"""
Knowledge Enrichment Module
Enriches legal assertions with ontology, references, and definitions
"""

from .models import (
    OntologyTerm,
    OntologyRelationship,
    LegalReference,
    TermDefinition,
    EnrichedAssertion,
    EnrichmentRequest,
    EnrichmentResponse,
    BatchEnrichmentRequest,
    BatchEnrichmentResponse,
    OntologyMatchRequest,
    OntologyMatchResponse,
    ReferenceResolutionRequest,
    ReferenceResolutionResponse,
    DefinitionExtractionRequest,
    DefinitionExtractionResponse,
    RelationshipType
)

from .database import KnowledgeEnrichmentDatabase
from .service import KnowledgeEnrichmentService
from .api import create_app

__version__ = "1.0.0"
__all__ = [
    "OntologyTerm",
    "OntologyRelationship",
    "LegalReference",
    "TermDefinition",
    "EnrichedAssertion",
    "EnrichmentRequest",
    "EnrichmentResponse",
    "BatchEnrichmentRequest",
    "BatchEnrichmentResponse",
    "OntologyMatchRequest",
    "OntologyMatchResponse",
    "ReferenceResolutionRequest",
    "ReferenceResolutionResponse",
    "DefinitionExtractionRequest",
    "DefinitionExtractionResponse",
    "RelationshipType",
    "KnowledgeEnrichmentDatabase",
    "KnowledgeEnrichmentService",
    "create_app"
]

# Made with Bob
