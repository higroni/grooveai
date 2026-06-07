"""
Entity recognition service with classla NER (default) and regex fallback for Serbian legal text.
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

# Global classla pipeline (lazy loaded)
_classla_pipeline = None


def _get_classla_pipeline():
    """Get or initialize classla NER pipeline for Serbian."""
    global _classla_pipeline
    if _classla_pipeline is None:
        try:
            import classla
            logger.info("Initializing classla NER pipeline for Serbian...")
            _classla_pipeline = classla.Pipeline(
                lang='sr',
                processors='tokenize,ner',
                use_gpu=False,  # Set to True if GPU available
                verbose=False
            )
            logger.info("classla NER pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize classla NER: {e}")
            _classla_pipeline = False  # Mark as failed to avoid retrying
    return _classla_pipeline if _classla_pipeline is not False else None


# classla entity type mapping to our types
CLASSLA_TYPE_MAPPING = {
    "PER": "PERSON",
    "PERSON": "PERSON",
    "ORG": "ORGANIZATION",
    "ORGANIZATION": "ORGANIZATION",
    "LOC": "LOCATION",
    "LOCATION": "LOCATION",
    "GPE": "LOCATION",  # Geo-political entity
    "DATE": "DATE",
    "TIME": "DATE",
    "MONEY": "MONEY",
    "PERCENT": "PERCENTAGE",
}


# Stop words that indicate entity boundaries (for cleaning)
STOP_WORDS = {
    'donosi', 'odluku', 'u', 'dana', 'godine', 'sa', 'je', 'su', 'bio', 'bila', 'bilo',
    'biti', 'ima', 'imaju', 'može', 'mogu', 'treba', 'trebaju', 'mora', 'moraju',
    'i', 'ili', 'a', 'ali', 'da', 'te', 'ni', 'niti', 'već', 'nego'
}

# Common organization endings to detect proper boundaries
ORG_ENDINGS = {
    'ministarstvo', 'vlada', 'agencija', 'direkcija', 'institut', 'zavod',
    'fond', 'služba', 'uprava', 'inspekcija', 'republika', 'pokrajina'
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
    use_ner: bool = True
) -> RecognitionOutput:
    """
    Recognize entities in text using classla NER (default) or regex fallback.
    
    Args:
        text: Input text to analyze
        min_confidence: Minimum confidence threshold (0-1)
        entity_types: Specific entity types to extract (if None, extract all)
        use_ner: Whether to use classla NER (True) or regex only (False)
    
    Returns:
        RecognitionOutput with entities and statistics
    """
    entities = []
    
    # Try classla NER first if enabled
    if use_ner:
        classla_entities = _recognize_with_classla(text, entity_types)
        if classla_entities is not None:
            entities.extend(classla_entities)
            logger.info(f"classla NER found {len(classla_entities)} entities (before post-processing)")
    
    # Always add regex-based entities for types not covered well by classla
    regex_types = ["LEGAL_REF", "DURATION", "DATE", "MONEY", "PERCENTAGE"]  # Types classla doesn't handle well
    if entity_types:
        regex_types = [t for t in regex_types if t in entity_types]
    
    regex_entities = _recognize_with_regex(text, min_confidence, regex_types)
    entities.extend(regex_entities)
    logger.info(f"Regex found {len(regex_entities)} additional entities")
    
    # If classla failed or was disabled, use regex for all types
    if not use_ner or (use_ner and not entities):
        logger.warning("Using regex fallback for all entity types")
        entities = _recognize_with_regex(text, min_confidence, entity_types)
    
    # POST-PROCESSING PIPELINE (generički pristup)
    entities = _post_process_entities(entities, text)
    logger.info(f"After post-processing: {len(entities)} entities")
    
    # Remove duplicates
    entities = _remove_duplicates(entities)
    
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


def _recognize_with_classla(
    text: str,
    entity_types: Optional[List[str]] = None
) -> Optional[List[Entity]]:
    """Recognize entities using classla NER."""
    pipeline = _get_classla_pipeline()
    if pipeline is None:
        return None
    
    try:
        doc = pipeline(text)
        entities = []
        
        # classla returns a Document object with sentences
        for sentence in doc.sentences:
            for ent in sentence.ents:
                # Map classla type to our type
                entity_type = CLASSLA_TYPE_MAPPING.get(ent.type, None)
                if entity_type is None:
                    continue
                
                # Filter by requested types
                if entity_types and entity_type not in entity_types:
                    continue
                
                # Calculate character positions (classla doesn't provide them)
                # Find the entity text in the original text
                entity_text = ent.text
                start_char = text.find(entity_text)
                if start_char == -1:
                    continue  # Skip if not found
                end_char = start_char + len(entity_text)
                
                # Calculate confidence (classla doesn't provide confidence, so use high default)
                confidence = 0.90
                
                entity = Entity(
                    entity_id=str(uuid.uuid4()),
                    entity_type=entity_type,
                    text=entity_text,
                    start_char=start_char,
                    end_char=end_char,
                    confidence=confidence,
                    metadata={
                        "source": "classla",
                        "original_type": ent.type
                    }
                )
                entities.append(entity)
        
        return entities
    
    except Exception as e:
        logger.error(f"classla NER failed: {e}")
        return None


def _recognize_with_regex(
    text: str,
    min_confidence: float = 0.5,
    entity_types: Optional[List[str]] = None
) -> List[Entity]:
    """Recognize entities using regex patterns."""
    entities = []
    
    # Determine which entity types to process
    types_to_process = entity_types if entity_types else list(ENTITY_PATTERNS.keys())
    
    for entity_type in types_to_process:
        if entity_type not in ENTITY_PATTERNS:
            continue
            
        patterns = ENTITY_PATTERNS[entity_type]
        type_entities = _extract_entities_by_type(text, entity_type, patterns)
        entities.extend(type_entities)
    
    return entities


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
                    "source": "regex",
                    "pattern": pattern[:50],
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


def _post_process_entities(entities: List[Entity], text: str) -> List[Entity]:
    """
    Post-process entities to improve quality (generički pristup).
    
    Steps:
    1. Clean entity boundaries (remove trailing stop words)
    2. Filter false positives based on context
    3. Merge fragmented entities
    4. Recalculate confidence based on quality
    """
    processed = []
    
    for entity in entities:
        # Step 1: Clean boundaries
        cleaned_entity = _clean_entity_boundaries(entity, text)
        if cleaned_entity is None:
            continue  # Entity was invalid
        
        # Step 2: Filter false positives
        if _is_false_positive(cleaned_entity, text):
            logger.debug(f"Filtered false positive: {cleaned_entity.text} ({cleaned_entity.entity_type})")
            continue
        
        # Step 3: Recalculate confidence based on quality
        cleaned_entity.confidence = _recalculate_confidence(cleaned_entity, text)
        
        processed.append(cleaned_entity)
    
    # Step 4: Merge fragmented entities (e.g., "Ministarstvo" + "finansija")
    processed = _merge_fragmented_entities(processed, text)
    
    return processed


def _clean_entity_boundaries(entity: Entity, text: str) -> Optional[Entity]:
    """
    Clean entity boundaries by removing trailing stop words and punctuation.
    Returns None if entity becomes invalid.
    """
    entity_text = entity.text.strip()
    start_char = entity.start_char
    end_char = entity.end_char
    
    # Remove trailing stop words
    words = entity_text.split()
    while words and words[-1].lower() in STOP_WORDS:
        removed_word = words.pop()
        end_char -= len(removed_word) + 1  # +1 for space
    
    # Remove leading stop words
    while words and words[0].lower() in STOP_WORDS:
        removed_word = words.pop(0)
        start_char += len(removed_word) + 1
    
    if not words:
        return None  # Entity is only stop words
    
    # For ORGANIZATION, keep up to keyword + next word (e.g., "Ministarstvo finansija")
    if entity.entity_type == "ORGANIZATION":
        for i, word in enumerate(words):
            if word.lower() in ORG_ENDINGS:
                # Keep words up to and including keyword + next word if exists
                end_idx = min(i + 2, len(words))  # keyword + 1 more word
                words = words[:end_idx]
                break
    
    # For LOCATION, extract only the actual city/place name using regex
    elif entity.entity_type == "LOCATION":
        # Use regex to find known Serbian cities in the text
        location_pattern = r'\b(Beograd|Novi\s+Sad|Niš|Kragujevac|Subotica|Zrenjanin|Pančevo|Čačak|Kruševac|Kraljevo|Smederevo|Leskovac|Užice|Vranje|Šabac|Sombor|Valjevo|Kikinda|Sremska\s+Mitrovica|Jagodina|Vršac|Zaječar|Požarevac|Pirot|Prokuplje|Negotin|Bor|Loznica|Aranđelovac|Paraćin|Ćuprija|Lazarevac|Mladenovac|Obrenovac|Sopot|Barajevo)[ua]?\b'
        
        full_text = ' '.join(words)
        match = re.search(location_pattern, full_text, re.IGNORECASE)
        
        if match:
            # Extract just the city name
            city_name = match.group(0)
            words = city_name.split()
        else:
            # If no known city found, keep only first 1-2 capitalized words
            location_words = []
            for word in words:
                if word and word[0].isupper():
                    location_words.append(word)
                    if len(location_words) >= 2:
                        break
                else:
                    break
            if location_words:
                words = location_words
    
    # Reconstruct entity
    new_text = ' '.join(words)
    if not new_text:
        return None
    
    # Find new boundaries in original text
    new_start = text.find(new_text, start_char)
    if new_start == -1:
        return None
    new_end = new_start + len(new_text)
    
    # Create cleaned entity
    return Entity(
        entity_id=entity.entity_id,
        entity_type=entity.entity_type,
        text=new_text,
        start_char=new_start,
        end_char=new_end,
        confidence=entity.confidence,
        metadata=entity.metadata
    )


def _is_false_positive(entity: Entity, text: str) -> bool:
    """
    Detect false positives based on context and patterns.
    """
    entity_text = entity.text.lower()
    
    # PERSON false positives
    if entity.entity_type == "PERSON":
        # Filter if it's actually part of an organization name
        if any(org_word in entity_text for org_word in ORG_ENDINGS):
            return True
        
        # Filter if it's a common verb phrase (e.g., "donosi odluku")
        common_verbs = ['donosi', 'odlučuje', 'određuje', 'utvrđuje', 'propisuje']
        if any(verb in entity_text for verb in common_verbs):
            return True
        
        # Filter very short person names (likely false positives)
        words = entity_text.split()
        if len(words) < 2:
            return True
    
    # ORGANIZATION false positives
    elif entity.entity_type == "ORGANIZATION":
        # Filter if it's too long (likely includes extra context)
        if len(entity.text) > 100:
            return True
        
        # Filter if it doesn't contain any organization keywords
        if not any(org_word in entity_text for org_word in ORG_ENDINGS):
            return True
    
    # LOCATION false positives
    elif entity.entity_type == "LOCATION":
        # Filter common false positives like "dana" (days)
        false_loc_words = ['dana', 'godine', 'meseca']
        if entity_text in false_loc_words:
            return True
    
    return False


def _recalculate_confidence(entity: Entity, text: str) -> float:
    """
    Recalculate confidence based on entity quality after cleaning.
    """
    base_confidence = entity.confidence
    
    # Adjust based on entity length
    text_len = len(entity.text)
    if text_len < 3:
        base_confidence *= 0.5  # Very short entities are less confident
    elif text_len > 50:
        base_confidence *= 0.8  # Very long entities might include noise
    
    # Adjust based on source
    metadata = entity.metadata or {}
    if metadata.get("source") == "classla":
        # classla entities that survived cleaning are more confident
        base_confidence = min(base_confidence + 0.05, 0.95)
    
    # Type-specific adjustments
    if entity.entity_type == "ORGANIZATION":
        # Check if it has proper organization structure
        if any(keyword in entity.text.lower() for keyword in ORG_ENDINGS):
            base_confidence = min(base_confidence + 0.1, 0.95)
    
    elif entity.entity_type == "LOCATION":
        # Known cities get higher confidence
        known_cities = ['beograd', 'novi sad', 'niš', 'kragujevac']
        if entity.text.lower() in known_cities:
            base_confidence = min(base_confidence + 0.15, 0.95)
    
    return round(base_confidence, 2)


def _merge_fragmented_entities(entities: List[Entity], text: str) -> List[Entity]:
    """
    Merge entities that are likely fragments of a single entity.
    For example: "Ministarstvo" (ORG) + "finansija" (ORG) -> "Ministarstvo finansija" (ORG)
    """
    if len(entities) < 2:
        return entities
    
    # Sort by position
    sorted_entities = sorted(entities, key=lambda e: e.start_char)
    merged = []
    skip_next = set()
    
    for i, entity in enumerate(sorted_entities):
        if i in skip_next:
            continue
        
        # Check if next entity is close and same type
        if i + 1 < len(sorted_entities):
            next_entity = sorted_entities[i + 1]
            
            # Merge if: same type, close proximity (< 10 chars), and both are ORG or PERSON
            gap = next_entity.start_char - entity.end_char
            if (entity.entity_type == next_entity.entity_type and
                gap < 10 and
                entity.entity_type in ["ORGANIZATION", "PERSON"]):
                
                # Extract text between entities
                between_text = text[entity.end_char:next_entity.start_char].strip()
                
                # Merge if gap is just whitespace or a single word
                if not between_text or len(between_text.split()) <= 1:
                    merged_text = text[entity.start_char:next_entity.end_char]
                    entity_meta = entity.metadata or {}
                    next_meta = next_entity.metadata or {}
                    merged_entity = Entity(
                        entity_id=entity.entity_id,
                        entity_type=entity.entity_type,
                        text=merged_text,
                        start_char=entity.start_char,
                        end_char=next_entity.end_char,
                        confidence=max(entity.confidence, next_entity.confidence),
                        metadata={
                            "source": "merged",
                            "original_sources": [
                                entity_meta.get("source"),
                                next_meta.get("source")
                            ]
                        }
                    )
                    merged.append(merged_entity)
                    skip_next.add(i + 1)
                    logger.debug(f"Merged entities: '{entity.text}' + '{next_entity.text}' -> '{merged_text}'")
                    continue
        
        merged.append(entity)
    
    return merged




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
