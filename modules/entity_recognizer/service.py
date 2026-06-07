"""
Entity recognition service with regex-based pattern matching for Serbian legal text.
"""

import re
import uuid
from typing import List, Tuple, Optional
from modules.entity_recognizer.models import (
    Entity,
    RecognitionOutput,
    RecognitionStats
)


# Serbian legal entity patterns
ENTITY_PATTERNS = {
    "PERSON": [
        # Serbian names: Ime Prezime, Ime Srednje Prezime
        r'\b[A-ZŠĐČĆŽ][a-zšđčćž]+\s+[A-ZŠĐČĆŽ][a-zšđčćž]+(?:\s+[A-ZŠĐČĆŽ][a-zšđčćž]+)?\b',
    ],
    "ORGANIZATION": [
        # Ministarstvo, Vlada, Agencija, Direkcija, Institut, Zavod
        r'\b(?:Ministarstvo|Vlada|Agencija|Direkcija|Institut|Zavod|Fond|Služba|Uprava|Inspekcija)\s+[a-zšđčćž\s]+\b',
        # Privredna društva: d.o.o., a.d., j.p.
        r'\b[A-ZŠĐČĆŽ][a-zšđčćž\s]+\s+(?:d\.o\.o\.|a\.d\.|j\.p\.)\b',
        # Republika Srbija, Autonomna pokrajina
        r'\b(?:Republika\s+Srbija|Autonomna\s+pokrajina\s+[A-ZŠĐČĆŽ][a-zšđčćž]+)\b',
    ],
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
    entity_types: Optional[List[str]] = None
) -> RecognitionOutput:
    """
    Recognize entities in text using regex pattern matching.
    
    Args:
        text: Input text to analyze
        min_confidence: Minimum confidence threshold (0-1)
        entity_types: Specific entity types to extract (if None, extract all)
    
    Returns:
        RecognitionOutput with entities and statistics
    """
    entities = []
    entity_counts = {}
    
    # Determine which entity types to process
    types_to_process = entity_types if entity_types else list(ENTITY_PATTERNS.keys())
    
    for entity_type in types_to_process:
        if entity_type not in ENTITY_PATTERNS:
            continue
            
        patterns = ENTITY_PATTERNS[entity_type]
        type_entities = _extract_entities_by_type(text, entity_type, patterns)
        
        # Filter by confidence
        type_entities = [e for e in type_entities if e.confidence >= min_confidence]
        
        entities.extend(type_entities)
        entity_counts[entity_type] = len(type_entities)
    
    # Remove duplicate entities (same text at same position)
    entities = _remove_duplicates(entities)
    
    # Calculate statistics
    avg_confidence = sum(e.confidence for e in entities) / len(entities) if entities else 0.0
    
    stats = RecognitionStats(
        total_entities=len(entities),
        entities_by_type=entity_counts,
        avg_confidence=round(avg_confidence, 2)
    )
    
    return RecognitionOutput(entities=entities, stats=stats)


def _extract_entities_by_type(
    text: str,
    entity_type: str,
    patterns: List[str]
) -> List[Entity]:
    """Extract entities of a specific type using regex patterns."""
    entities = []
    
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            entity_text = match.group(0)
            start_pos = match.start()
            end_pos = match.end()
            
            # Calculate confidence based on pattern specificity
            confidence = _calculate_entity_confidence(entity_text, entity_type)
            
            entity = Entity(
                entity_id=str(uuid.uuid4()),
                entity_type=entity_type,
                text=entity_text,
                start_char=start_pos,
                end_char=end_pos,
                confidence=confidence,
                metadata={
                    "pattern": pattern[:50],  # Store pattern used (truncated)
                    "length": len(entity_text)
                }
            )
            entities.append(entity)
    
    return entities


def _calculate_entity_confidence(text: str, entity_type: str) -> float:
    """
    Calculate confidence score for an entity based on various factors.
    
    Factors:
    - Length of entity text
    - Presence of specific keywords
    - Format validation
    """
    confidence = 0.5  # Base confidence
    
    # Length-based confidence
    text_len = len(text)
    if text_len > 5:
        confidence += 0.1
    if text_len > 10:
        confidence += 0.1
    if text_len > 20:
        confidence += 0.1
    
    # Type-specific confidence adjustments
    if entity_type == "LEGAL_REF":
        # Legal references with specific keywords are more confident
        if any(kw in text.lower() for kw in ["član", "stav", "tačka", "zakon", "pravilnik"]):
            confidence += 0.2
    
    elif entity_type == "DATE":
        # Dates with full format are more confident
        if re.match(r'\d{1,2}[./]\d{1,2}[./]\d{4}', text):
            confidence += 0.3
    
    elif entity_type == "MONEY":
        # Money with currency is more confident
        if any(curr in text for curr in ["RSD", "EUR", "USD", "dinara", "evra"]):
            confidence += 0.2
    
    elif entity_type == "ORGANIZATION":
        # Organizations with official keywords are more confident
        if any(kw in text for kw in ["Ministarstvo", "Vlada", "Republika", "Agencija"]):
            confidence += 0.2
    
    elif entity_type == "PERCENTAGE":
        # Percentages with % symbol are more confident
        if "%" in text:
            confidence += 0.2
    
    # Cap confidence at 1.0
    return min(confidence, 1.0)


def _remove_duplicates(entities: List[Entity]) -> List[Entity]:
    """Remove duplicate entities (same text at same position)."""
    seen = set()
    unique_entities = []
    
    for entity in entities:
        key = (entity.text, entity.start_char, entity.end_char)
        if key not in seen:
            seen.add(key)
            unique_entities.append(entity)
    
    return unique_entities

# Made with Bob
