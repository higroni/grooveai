"""
Normative Extractor Module - Extracts obligations, prohibitions, permissions, and definitions.
"""

from .service import extract_normative_content, get_extractor, NormativeExtractor
from .models import (
    Obligation, Prohibition, Permission, Definition,
    Waiver, Transfer, Assignment, AmbiguityScore, CircularDefinition,
    NormativeContent, ExtractionResult
)

__all__ = [
    'extract_normative_content',
    'get_extractor',
    'NormativeExtractor',
    'Obligation',
    'Prohibition',
    'Permission',
    'Definition',
    'Waiver',
    'Transfer',
    'Assignment',
    'AmbiguityScore',
    'CircularDefinition',
    'NormativeContent',
    'ExtractionResult'
]

# Made with Bob
