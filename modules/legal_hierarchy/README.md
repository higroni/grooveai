# Legal Hierarchy Classifier Module

## Overview

This module classifies legal documents by their type and hierarchy level according to Serbian legal system.

## Hierarchy Levels

1. **Ustav** (Constitution) - Highest authority
2. **Zakon** (Law) - Primary legislation
3. **Uredba** (Decree) - Government regulation
4. **Pravilnik** (Rulebook) - Ministerial regulation
5. **Odluka** (Decision) - Administrative decision
6. **Naređenje** (Order) - Administrative order

## Features

- **Document Type Classification**: Identifies document type (zakon, pravilnik, uredba, etc.)
- **Hierarchy Level Assignment**: Assigns hierarchy level (1-6)
- **Issuing Authority Extraction**: Identifies who issued the document
- **Legal Basis Extraction**: Extracts references to legal basis
- **Official Gazette Detection**: Finds official publication references
- **Hierarchy Relationships**: Determines what document can/cannot override

## Usage

```python
from modules.legal_hierarchy import classify_document

text = """
ZAKON O RADU
Na osnovu člana 98. Ustava Republike Srbije...
"""

result = classify_document(text)

print(f"Document type: {result['document']['document_type']}")
print(f"Hierarchy level: {result['document']['hierarchy_level']}")
print(f"Authority: {result['document']['issuing_authority']}")
print(f"Can override: {result['document']['can_override']}")
```

## Output Format

```json
{
  "document": {
    "document_type": "zakon",
    "hierarchy_level": 2,
    "issuing_authority": "Narodna skupština Republike Srbije",
    "legal_basis": ["člana 98. Ustava Republike Srbije"],
    "official_gazette": "Službeni glasnik RS, br. 24/2005",
    "can_override": ["uredba", "pravilnik", "odluka", "naređenje"],
    "cannot_override": ["ustav"],
    "confidence": 0.9
  },
  "title": "ZAKON O RADU",
  "detected_patterns": ["ZAKON o [a-zšđčćž\\s]+"],
  "processing_time": 0.003
}
```

## Pattern Detection

### Document Types

- **Ustav**: "USTAV Republike Srbije", "USTAV Srbije"
- **Zakon**: "ZAKON o ...", "ovaj zakon", "u smislu ovog zakona"
- **Uredba**: "UREDBA o ...", "Vlada donosi UREDBU", "ova uredba"
- **Pravilnik**: "PRAVILNIK o ...", "ovaj pravilnik"
- **Odluka**: "ODLUKA o ...", "donosi ODLUKU"
- **Naređenje**: "NAREĐENJE o ...", "ovo naređenje"

### Issuing Authorities

- **Narodna skupština**: "Narodna skupština Republike Srbije"
- **Vlada**: "Vlada Republike Srbije", "Vlada donosi"
- **Ministarstvo**: "Ministar ... donosi", "Ministarstvo ..."

### Legal Basis

- "Na osnovu člana X ..."
- "Na osnovu ... Zakona ..."
- "U skladu sa ..."

## Conflict Detection Support

This module supports conflict detection by:

1. **Hierarchy Violations**: Lower-level document contradicting higher-level
2. **Authority Violations**: Document issued by wrong authority
3. **Legal Basis Violations**: Missing or invalid legal basis
4. **Override Analysis**: Determining valid override relationships

## Performance

- Processing time: ~3ms per document
- Memory usage: Minimal (compiled regex patterns cached)
- Scalability: Can process thousands of documents efficiently

## Dependencies

- Python 3.8+
- pydantic
- No external NLP libraries required (pure regex)

## Integration

This module integrates with:
- **Normative Extractor**: Links hierarchy to normative statements
- **Temporal Linker**: Validates temporal constraints by hierarchy
- **Conflict Detector**: Identifies hierarchy-based conflicts