"""
Temporal Linker Module - Links temporal elements to normative statements.
"""

from .service import link_temporal_elements, get_linker, TemporalLinker
from .models import (
    TemporalElement, LinkedObligation, LinkedProhibition, LinkedPermission,
    TemporalLinkingResult
)

__all__ = [
    'link_temporal_elements',
    'get_linker',
    'TemporalLinker',
    'TemporalElement',
    'LinkedObligation',
    'LinkedProhibition',
    'LinkedPermission',
    'TemporalLinkingResult'
]

# Made with Bob
