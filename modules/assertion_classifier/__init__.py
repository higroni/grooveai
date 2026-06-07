"""
Assertion Classifier Module

Classifies legal assertions into types:
- obligation: Requirements and duties
- prohibition: Restrictions and bans
- permission: Rights and allowances
- deadline: Time-bound requirements
- definition: Definitions and explanations
"""

from modules.assertion_classifier.models import (
    Assertion,
    ClassificationResult,
    ClassificationOutput,
    ClassificationRequest,
    ClassificationResponse
)
from modules.assertion_classifier.service import AssertionClassifierService
from modules.assertion_classifier.database import ClassificationDatabase

__all__ = [
    "Assertion",
    "ClassificationResult",
    "ClassificationOutput",
    "ClassificationRequest",
    "ClassificationResponse",
    "AssertionClassifierService",
    "ClassificationDatabase"
]

# Made with Bob
