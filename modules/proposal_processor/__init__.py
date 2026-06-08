"""
Proposal Processor Module

This module processes legal proposal documents (PDF, DOCX, or text) and prepares them
for conflict detection by running them through the same pipeline as existing laws.
"""

from .service import ProposalProcessorService
from .models import (
    ProposalInput,
    ProposalProcessingResult,
    ProposalMetadata
)

__all__ = [
    'ProposalProcessorService',
    'ProposalInput',
    'ProposalProcessingResult',
    'ProposalMetadata'
]

# Made with Bob
