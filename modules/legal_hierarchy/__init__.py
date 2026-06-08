"""
Legal Hierarchy Classifier Module

This module classifies legal documents by their type and hierarchy level.
"""

from .models import LegalDocument, HierarchyClassificationResult
from .service import LegalHierarchyClassifier, get_classifier, classify_document

__all__ = [
    'LegalDocument',
    'HierarchyClassificationResult',
    'LegalHierarchyClassifier',
    'get_classifier',
    'classify_document'
]

# Made with Bob
