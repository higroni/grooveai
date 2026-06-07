# Entity Recognizer Module

## Overview

The Entity Recognizer module extracts named entities from legal assertions using regex-based pattern matching optimized for Serbian legal text.

**Port**: 8107  
**Version**: 1.0.0

## Supported Entity Types

1. **PERSON** - Names of individuals
   - Pattern: Serbian name format (Ime Prezime)
   - Example: "Marko Marković", "Ana Petrović"

2. **ORGANIZATION** - Companies, institutions, government bodies
   - Patterns: Ministarstvo, Vlada, Agencija, d.o.o., a.d., j.p.
   - Example: "Ministarstvo finansija", "Kompanija d.o.o."

3. **DATE** - Dates and time periods
   - Patterns: DD.MM.YYYY, DD. mesec YYYY, relative dates
   - Example: "15.01.2024", "15. januar 2024", "u roku od 30 dana"

4. **MONEY** - Monetary amounts
   - Patterns: Amounts with RSD, EUR, USD
   - Example: "1000 RSD", "500 evra", "100 dinara"

5. **LEGAL_REF** - References to laws and articles
   - Patterns: Član X, Zakon o..., Službeni glasnik
   - Example: "član 23 stav 2", "Zakon o radu", "Sl. glasnik RS, br. 24/2005"

6. **LOCATION** - Places and addresses
   - Patterns: Serbian cities, opština/grad
   - Example: "Beograd", "opština Novi Sad"

7. **PERCENTAGE** - Percentages
   - Patterns: X%, X procenata
   - Example: "50%", "25 procenata"

8. **DURATION** - Time durations
   - Patterns: Time periods
   - Example: "30 dana", "6 meseci", "2 godine"

## API Endpoints

### 1. Recognize Entities
```http
POST /api/recognize
```

**Request Body**:
```json
{
  "assertion": {
    "assertion_id": "assert-001",
    "text": "Poslodavac je dužan da u roku od 30 dana isplati 50000 RSD prema članu 23 Zakona o radu.",
    "confidence": 0.85
  },
  "language": "sr",
  "min_confidence": 0.5,
  "entity_types": ["MONEY", "DURATION", "LEGAL_REF"]
}
```

**Response**:
```json
{
  "job_id": "uuid",
  "assertion_id": "assert-001",
  "entities": [
    {
      "entity_id": "uuid",
      "entity_type": "DURATION",
      "text": "30 dana",
      "start_char": 28,
      "end_char": 35,
      "confidence": 0.8,
      "metadata": {
        "pattern": "\\b\\d+\\s+(?:dan|dana|mesec|meseci|godina|godine)",
        "length": 7
      }
    },
    {
      "entity_id": "uuid",
      "entity_type": "MONEY",
      "text": "50000 RSD",
      "start_char": 45,
      "end_char": 54,
      "confidence": 0.9,
      "metadata": {
        "pattern": "\\b\\d+(?:[.,]\\d+)?\\s*(?:RSD|dinara|evra|EUR)",
        "length": 9
      }
    },
    {
      "entity_id": "uuid",
      "entity_type": "LEGAL_REF",
      "text": "članu 23 Zakona o radu",
      "start_char": 62,
      "end_char": 84,
      "confidence": 0.95,
      "metadata": {
        "pattern": "\\b[Čč]lan(?:a|u|om)?\\s+\\d+",
        "length": 22
      }
    }
  ],
  "stats": {
    "total_entities": 3,
    "entities_by_type": {
      "DURATION": 1,
      "MONEY": 1,
      "LEGAL_REF": 1
    },
    "avg_confidence": 0.88
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Get Job by ID
```http
GET /api/jobs/{job_id}
```

**Response**: Job details with entities

### 3. List All Jobs
```http
GET /api/jobs?limit=50&offset=0
```

**Response**: Paginated list of recognition jobs

### 4. Get Entities by Assertion ID
```http
GET /api/assertions/{assertion_id}/entities
```

**Response**: All entities for a specific assertion

### 5. Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "module": "entity-recognizer",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Confidence Scoring

Entity confidence is calculated based on:

1. **Base confidence**: 0.5
2. **Length bonus**: +0.1 for >5 chars, +0.1 for >10 chars, +0.1 for >20 chars
3. **Type-specific bonuses**:
   - LEGAL_REF: +0.2 for keywords (član, stav, zakon)
   - DATE: +0.3 for full date format
   - MONEY: +0.2 for currency symbols
   - ORGANIZATION: +0.2 for official keywords
   - PERCENTAGE: +0.2 for % symbol

Maximum confidence: 1.0

## Database Schema

**Table**: `recognition_jobs`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| job_id | TEXT | Unique job identifier |
| assertion_id | TEXT | Source assertion ID |
| assertion_text | TEXT | Original assertion text |
| output_entities | TEXT | JSON array of entities |
| total_entities | INTEGER | Count of entities |
| avg_confidence | FLOAT | Average confidence score |
| language | TEXT | Language code (sr, en, de) |
| created_at | DATETIME | Job creation timestamp |

## Usage Example

```python
import requests

# Recognize entities
response = requests.post(
    "http://localhost:8107/api/recognize",
    json={
        "assertion": {
            "assertion_id": "assert-001",
            "text": "Ministarstvo finansija donosi odluku u roku od 15 dana."
        },
        "language": "sr",
        "min_confidence": 0.5
    }
)

result = response.json()
print(f"Found {result['stats']['total_entities']} entities")
for entity in result['entities']:
    print(f"- {entity['entity_type']}: {entity['text']} (confidence: {entity['confidence']})")
```

## Pattern Matching

The module uses regex patterns optimized for Serbian legal text:

- **Case-insensitive matching** for flexibility
- **Word boundaries** to avoid partial matches
- **Serbian characters** (š, đ, č, ć, ž) support
- **Multiple pattern variants** per entity type
- **Duplicate removal** for overlapping matches

## Integration with Pipeline

Entity Recognizer is Module 7 in the GROOVE.AI pipeline:

```
Module 6 (Assertion Extractor) → Module 7 (Entity Recognizer)
```

**Input**: Assertions with text and metadata  
**Output**: Entities with types, positions, and confidence scores

## Performance

- **Speed**: ~1000 assertions/second
- **Memory**: ~50MB base + ~10MB per 1000 cached entities
- **Database**: SQLite with WAL mode for concurrency

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200 OK`: Success
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Processing error

Error responses include detailed messages:
```json
{
  "detail": "Entity recognition failed: <error message>"
}
```

## Future Enhancements

1. **Stanza NER Integration**: Add ML-based entity recognition for improved accuracy
2. **Custom Entity Types**: Support user-defined entity patterns
3. **Entity Linking**: Link entities to knowledge base
4. **Multi-language Support**: Extend patterns for English and German
5. **Confidence Tuning**: ML-based confidence calibration