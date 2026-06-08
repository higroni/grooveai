"""
Qdrant Loader Module

This module handles loading legal document data from JSON exports into Qdrant vector database.
It creates and manages three collections:
- legal_units: Individual legal units (articles, paragraphs, etc.)
- normative_content: Normative assertions extracted from legal units
- document_metadata: Document-level metadata and statistics
"""

from .service import QdrantLoaderService
from .models import (
    LegalUnitPayload,
    NormativeContentPayload,
    DocumentMetadataPayload,
    LoaderConfig,
    LoaderStats
)

__all__ = [
    'QdrantLoaderService',
    'LegalUnitPayload',
    'NormativeContentPayload',
    'DocumentMetadataPayload',
    'LoaderConfig',
    'LoaderStats'
]

# Made with Bob
