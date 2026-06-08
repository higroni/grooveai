"""
Entity recognition service with regex patterns for Serbian legal text.
classla NER is DISABLED for batch processing due to memory leaks.
"""

import re
import uuid
import logging
from typing import List, Tuple, Optional
from modules.entity_recognizer.models import (
    Entity,
    RecognitionOutput,
    RecognitionStats
)

# Initialize logger
logger = logging.getLogger(__name__)


# classla entity type mapping to our types
CLASSLA_TYPE_MAPPING = {
    "PER": "PERSON",
    "PERSON": "PERSON",
    "ORG": "ORGANIZATION",
    "ORGANIZATION": "ORGANIZATION",
    "LOC": "LOCATION",
    "LOCATION": "LOCATION",
    "MISC": "OTHER",
}


# Serbian legal entity patterns (regex-only, no PERSON/ORGANIZATION due to high false positives)
ENTITY_PATTERNS = {
    "DATE": [
        # DD.MM.YYYY, DD/MM/YYYY
        r'\b\d{1,2}[./]\d{1,2}[./]\d{4}\b',
        # DD. mesec YYYY (15. januar 2024)
        r'\b\d{1,2}\.\s+(?:januar|februar|mart|april|maj|jun|jul|avgust|septembar|oktobar|novembar|decembar)[a-z]*\s+\d{4}\b',
        # Relative dates
        r'\b(?:u\s+roku\s+od|nakon|pre|do)\s+\d+\s+(?:dan|dana|mesec|meseci|godina|godine)\b',
    ],
    "MONEY": [
        # Amounts with RSD, EUR, USD
        r'\b\d+(?:[.,]\d+)?\s*(?:RSD|dinara|evra|EUR|dolara|USD)\b',
        # Written amounts
        r'\b(?:hiljade|miliona|milijardi)\s+dinara\b',
    ],
    "LEGAL_REF": [
        # Član X, stav Y, tačka Z
        r'\b[Čč]lan(?:a|u|om)?\s+\d+(?:\s+stav(?:a|u|om)?\s+\d+)?(?:\s+tačk(?:a|e|u|om)\s+\d+)?\b',
        # Zakon o..., Pravilnik o..., Uredba o...
        r'\b(?:Zakon|Pravilnik|Uredba|Odluka|Naredba)\s+o\s+[a-zšđčćž\s]+\b',
        # Službeni glasnik references
        r'\b(?:Službeni\s+glasnik|Sl\.\s*glasnik)\s+RS,?\s*br\.?\s*\d+/\d+\b',
    ],
    "LOCATION": [
        # Cities and places
        r'\b(?:Beograd|Novi\s+Sad|Niš|Kragujevac|Subotica|Zrenjanin|Pančevo|Čačak|Kruševac|Kraljevo|Smederevo|Leskovac|Užice|Vranje|Šabac|Sombor|Valjevo|Kikinda|Sremska\s+Mitrovica|Jagodina|Vršac|Zaječar|Požarevac|Pirot|Prokuplje|Negotin|Bor|Loznica|Aranđelovac|Paraćin|Ćuprija|Lazarevac|Mladenovac|Obrenovac|Sopot|Barajevo)\b',
        # Opština, grad
        r'\b(?:opštin[aeu]|grad(?:a|u)?)\s+[A-ZŠĐČĆŽ][a-zšđčćž]+\b',
    ],
    "PERCENTAGE": [
        # X%, X procenata
        r'\b\d+(?:[.,]\d+)?\s*(?:%|procent[a]?)\b',
    ],
    "DURATION": [
        # Time periods
        r'\b\d+\s+(?:dan|dana|mesec|meseci|godina|godine|sat|sati|minut|minuta|nedelj[aeu]|nedeljama)\b',
        # From-to periods
        r'\bod\s+\d+\s+do\s+\d+\s+(?:dan|dana|mesec|meseci|godina|godine)\b',
    ],
}


def recognize_entities(
    text: str,
    min_confidence: float = 0.5,
    entity_types: Optional[List[str]] = None,
    use_ner: bool = False  # IGNORED - NER is disabled
) -> RecognitionOutput:
    """
    Recognize entities in text using regex patterns only.
    
    Args:
        text: Input text
        min_confidence: Minimum confidence threshold (0.0-1.0)
        entity_types: Optional list of entity types to extract
        use_ner: IGNORED - classla NER is disabled for batch processing
        
    Returns:
        RecognitionOutput with entities and statistics
    """
    # CRITICAL: classla NER is disabled for batch processing
    # Only use regex patterns
    entities = _recognize_with_regex(text, entity_types)
    
    # Filter by confidence
    entities = [e for e in entities if e.confidence >= min_confidence]
    
    # Calculate statistics
    entity_counts = {}
    for entity in entities:
        entity_counts[entity.entity_type] = entity_counts.get(entity.entity_type, 0) + 1
    
    avg_confidence = sum(e.confidence for e in entities) / len(entities) if entities else 0.0
    
    stats = RecognitionStats(
        total_entities=len(entities),
        entities_by_type=entity_counts,
        avg_confidence=round(avg_confidence, 2)
    )
    
    return RecognitionOutput(entities=entities, stats=stats)


def _recognize_with_regex(
    text: str,
    entity_types: Optional[List[str]] = None
) -> List[Entity]:
    """Recognize entities using regex patterns."""
    entities = []
    
    # Determine which patterns to use
    patterns_to_use = ENTITY_PATTERNS
    if entity_types:
        patterns_to_use = {k: v for k, v in ENTITY_PATTERNS.items() if k in entity_types}
    
    # Extract entities using patterns
    for entity_type, patterns in patterns_to_use.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entity = Entity(
                    entity_id=str(uuid.uuid4()),
                    text=match.group(),
                    entity_type=entity_type,
                    start_char=match.start(),
                    end_char=match.end(),
                    confidence=0.85  # Fixed confidence for regex matches
                )
                entities.append(entity)
    
    return entities

# Made with Bob
