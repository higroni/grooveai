"""
Conflict Detector Module

This module detects conflicts between legal proposals and existing laws using
semantic search in Qdrant vector database.
"""

from .service import ConflictDetectorService
from .models import (
    ConflictType,
    ConflictSeverity,
    Conflict,
    ConflictDetectionResult,
    ConflictDetectionConfig
)

__all__ = [
    'ConflictDetectorService',
    'ConflictType',
    'ConflictSeverity',
    'Conflict',
    'ConflictDetectionResult',
    'ConflictDetectionConfig'
]

# Made with Bob
