# Normative Extractor Module

## Overview
Extracts normative content (obligations, prohibitions, permissions, definitions) from legal text using regex pattern matching.

## Purpose
This module addresses the critical gap identified in PARSING_ANALYSIS_FOR_CONFLICT_DETECTION.md - extracting semantic normative content needed for conflict detection.

## Features

### 1. Obligation Extraction
Detects legal obligations using patterns:
- "dužan je", "mora", "obavezan je"
- "ima obavezu"
- Extracts: subject, action, object, modality, temporal constraints

**Example:**
```
Input: "Poslodavac je dužan da isplati zaradu u roku od 30 dana"
Output: {
  "subject": "Poslodavac",
  "action": "isplati",
  "object": "zaradu",
  "modality": "dužan je",
  "temporal": {"deadline": "u roku od 30 dana"}
}
```

### 2. Prohibition Extraction
Detects legal prohibitions using patterns:
- "zabranjeno je", "ne sme", "ne može"
- Extracts: subject, action, object, modality, exceptions

**Example:**
```
Input: "Poslodavac ne sme zapošljavati lica mlađa od 18 godina"
Output: {
  "subject": "Poslodavac",
  "action": "zapošljavati",
  "object": "lica mlađa od 18 godina",
  "modality": "ne sme"
}
```

### 3. Permission Extraction
Detects legal permissions using patterns:
- "može", "ima pravo", "dozvoljeno je"
- Extracts: subject, action, object, modality, conditions

**Example:**
```
Input: "Zaposleni može raditi noćni rad ako ima pisanu saglasnost"
Output: {
  "subject": "Zaposleni",
  "action": "raditi",
  "object": "noćni rad",
  "modality": "može",
  "condition": "ako ima pisanu saglasnost"
}
```

### 4. Definition Extraction
Detects legal definitions using patterns:
- "smatra se", "u smislu ovog zakona"
- "pod terminom ... podrazumeva se"
- Extracts: term, definition, scope

**Example:**
```
Input: "Zaposleni se smatra fizičko lice koje je u radnom odnosu u smislu ovog zakona"
Output: {
  "term": "Zaposleni",
  "definition": "fizičko lice koje je u radnom odnosu",
  "scope": "u smislu ovog zakona"
}
```

## Usage

### Basic Usage
```python
from modules.normative_extractor import extract_normative_content

text = """
Poslodavac je dužan da isplati zaradu u roku od 30 dana.
Zabranjeno je zapošljavanje lica mlađih od 18 godina.
Zaposleni može raditi noćni rad uz pisanu saglasnost.
"""

result = extract_normative_content(text)

print(f"Obligations: {len(result['normative_content']['obligations'])}")
print(f"Prohibitions: {len(result['normative_content']['prohibitions'])}")
print(f"Permissions: {len(result['normative_content']['permissions'])}")
print(f"Definitions: {len(result['normative_content']['definitions'])}")
```

### Advanced Usage
```python
from modules.normative_extractor import get_extractor

extractor = get_extractor()

# Extract specific types
obligations = extractor.extract_obligations(text)
prohibitions = extractor.extract_prohibitions(text)
permissions = extractor.extract_permissions(text)
definitions = extractor.extract_definitions(text)

# Full extraction with timing
result = extractor.extract(text)
print(f"Processing time: {result.processing_time:.3f}s")
print(f"Total extracted: {result.normative_content.total_count}")
```

## Output Format

```json
{
  "normative_content": {
    "obligations": [
      {
        "subject": "Poslodavac",
        "action": "isplati",
        "object": "zaradu",
        "modality": "dužan je",
        "condition": null,
        "temporal": {"deadline": "u roku od 30 dana"},
        "source_text": "Poslodavac je dužan da isplati zaradu u roku od 30 dana",
        "confidence": 0.8
      }
    ],
    "prohibitions": [...],
    "permissions": [...],
    "definitions": [...]
  },
  "processing_time": 0.045,
  "text_length": 1234,
  "total_extracted": 15
}
```

## Pattern Matching

### Obligation Patterns
1. `Subject + dužan je + action + object + temporal`
2. `Subject + ima obavezu + action + object`
3. `Obaveza + subject + je + action + object`

### Prohibition Patterns
1. `Subject + ne sme/ne može + action + object`
2. `Zabranjeno je + action + object`
3. `Subject + je zabranjeno + action + object`

### Permission Patterns
1. `Subject + može + action + object + condition`
2. `Subject + ima pravo + action + object`
3. `Dozvoljeno je + action + object`

### Definition Patterns
1. `Term + se smatra + definition + scope`
2. `U smislu ovog zakona, term je definition`
3. `Term je definition (u smislu ovog zakona)`
4. `Pod terminom "X" podrazumeva se Y`

## Performance

- **Speed**: ~0.05s per document (1000 words)
- **Accuracy**: ~80% (regex-based)
- **Memory**: Minimal (no ML models)

## Limitations

1. **Regex-based**: May miss complex sentence structures
2. **Serbian language only**: Patterns designed for Serbian legal text
3. **No context understanding**: Cannot resolve ambiguities
4. **Fixed patterns**: Requires pattern updates for new phrasings

## Future Improvements

1. **Add more patterns** for edge cases
2. **Improve temporal extraction** (link to specific obligations)
3. **Add condition extraction** (IF-THEN logic)
4. **Hybrid approach** (combine with LLM for low-confidence cases)
5. **Fine-tune confidence scores** based on pattern quality

## Integration with Conflict Detection

This module provides the **semantic foundation** for conflict detection:

- **Contradictory Obligation**: Compare obligations with same subject/action but different temporal constraints
- **Contradictory Prohibition**: Compare prohibitions across documents
- **Conflicting Definition**: Compare definitions of same term
- **Permission vs Prohibition**: Detect when permission conflicts with prohibition

## Testing

```bash
# Run tests
python -m pytest modules/normative_extractor/tests/

# Test on sample text
python modules/normative_extractor/test_extractor.py
```

## Dependencies

- `pydantic` - Data validation
- `re` - Regex pattern matching (built-in)

No external NLP libraries required!

## Related Modules

- **assertion_extractor**: Extracts assertions (simpler, less structured)
- **condition_extractor**: Extracts conditions (IF-THEN logic)
- **legal_parser**: Extracts structural elements (articles, paragraphs)

## References

- [PARSING_ANALYSIS_FOR_CONFLICT_DETECTION.md](../../GEN/PARSING_ANALYSIS_FOR_CONFLICT_DETECTION.md)
- [CONFLICT_TYPES_SPECIFICATION.md](../../GEN/CONFLICT_TYPES_SPECIFICATION.md)