# Condition Extractor Module

Module 8 in the GROOVE.AI pipeline - extracts conditions, exceptions, temporal and modal clauses from legal assertions.

## Overview

The Condition Extractor analyzes legal assertions and identifies:
- **Conditions**: "ako", "kada", "u slučaju da", "pod uslovom da"
- **Exceptions**: "osim", "izuzev", "sem", "osim ako"
- **Temporal conditions**: "pre", "nakon", "do", "od", "u roku od"
- **Modal conditions**: "može", "mora", "treba", "sme", "dužan je"

## Features

- Regex-based pattern matching for Serbian and English
- Context extraction around each condition
- Clause boundary detection
- Confidence scoring per condition type
- Database storage of all extracted conditions

## API Endpoints

### POST /api/extract
Extract conditions from an assertion.

**Request:**
```json
{
  "assertion": {
    "assertion_id": "assertion-123",
    "text": "Zaposleni mora da obavesti poslodavca ako planira da koristi godišnji odmor.",
    "confidence": 0.85
  },
  "language": "sr",
  "min_confidence": 0.5,
  "extract_conditions": true,
  "extract_exceptions": true,
  "extract_temporal": true,
  "extract_modal": true
}
```

**Response:**
```json
{
  "job_id": "job-uuid",
  "assertion_id": "assertion-123",
  "output": {
    "conditions": [
      {
        "condition_id": "cond-uuid-1",
        "condition_type": "modal",
        "text": "Zaposleni mora da obavesti poslodavca",
        "start_char": 0,
        "end_char": 40,
        "confidence": 0.95,
        "trigger_word": "mora",
        "context": "Zaposleni mora da obavesti poslodavca ako planira..."
      },
      {
        "condition_id": "cond-uuid-2",
        "condition_type": "condition",
        "text": "ako planira da koristi godišnji odmor",
        "start_char": 41,
        "end_char": 79,
        "confidence": 0.9,
        "trigger_word": "ako",
        "context": "...obavesti poslodavca ako planira da koristi godišnji odmor."
      }
    ],
    "total_conditions": 1,
    "total_exceptions": 0,
    "total_temporal": 0,
    "total_modal": 1,
    "average_confidence": 0.93,
    "processing_time_ms": 15.5
  },
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### GET /api/jobs/{job_id}
Get extraction job details by ID.

### GET /api/assertions/{assertion_id}/conditions
Get all conditions for a specific assertion.

### GET /health
Health check endpoint.

## Configuration

Module configuration in `config.yaml`:

```yaml
network:
  modules:
    condition_extractor:
      host: "0.0.0.0"
      port: 8108
      url: "http://localhost:8108"

database:
  modules:
    condition_extractor: "sqlite:///data/databases/condition_extractor.db"
```

## Database Schema

### condition_extraction_jobs
- `job_id` (TEXT, PRIMARY KEY)
- `assertion_id` (TEXT, indexed)
- `assertion_text` (TEXT)
- `output_conditions` (TEXT, JSON)
- `total_conditions` (INTEGER)
- `total_exceptions` (INTEGER)
- `total_temporal` (INTEGER)
- `total_modal` (INTEGER)
- `average_confidence` (REAL)
- `processing_time_ms` (REAL)
- `created_at` (TIMESTAMP)

### extracted_conditions
- `condition_id` (TEXT, PRIMARY KEY)
- `job_id` (TEXT, FOREIGN KEY)
- `condition_type` (TEXT, indexed)
- `text` (TEXT)
- `start_char` (INTEGER)
- `end_char` (INTEGER)
- `confidence` (REAL)
- `trigger_word` (TEXT)
- `context` (TEXT)

## Condition Types

### 1. Conditions (condition)
Trigger words: ako, kada, ukoliko, u slučaju da, pod uslovom da, kad

Example: "**Ako** zaposleni kasni na posao, mora da obavesti poslodavca."

### 2. Exceptions (exception)
Trigger words: osim, izuzev, sem, osim ako, izuzev u slučaju, sem ako

Example: "Svi zaposleni imaju pravo na odmor, **osim** onih u probnom radu."

### 3. Temporal Conditions (temporal)
Trigger words: pre, nakon, do, od, u roku od, pre nego što, nakon što

Example: "Zaposleni mora da podnese zahtev **u roku od** 30 dana."

### 4. Modal Conditions (modal)
Trigger words: može, mora, treba, sme, ne sme, ne može, dužan je, obavezan je, ima pravo

Example: "Poslodavac **mora** da isplati platu do kraja meseca."

## Usage Example

```python
import requests

# Extract conditions
response = requests.post(
    "http://localhost:8108/api/extract",
    json={
        "assertion": {
            "assertion_id": "art-15-assert-1",
            "text": "Zaposleni mora da obavesti poslodavca ako planira da koristi godišnji odmor u roku od 15 dana.",
            "confidence": 0.85
        },
        "language": "sr",
        "min_confidence": 0.5
    }
)

result = response.json()
print(f"Extracted {result['output']['total_conditions']} conditions")
print(f"Extracted {result['output']['total_modal']} modal conditions")
print(f"Extracted {result['output']['total_temporal']} temporal conditions")

for condition in result['output']['conditions']:
    print(f"- {condition['condition_type']}: {condition['text']}")
```

## Running the Module

```bash
# Install dependencies
pip install -r requirements.txt

# Run the module
python -m modules.condition_extractor.main
```

## Integration with Pipeline

Module 8 receives assertions from Module 6 (Assertion Extractor) and extracts conditions that will be used by downstream modules for conflict detection and reasoning.

**Pipeline Flow:**
1. Module 6 extracts assertions from legal units
2. **Module 8 extracts conditions from assertions**
3. Module 9 classifies assertions
4. Module 10 generates embeddings
5. Further modules use conditions for conflict detection

## Performance

- Average processing time: 10-20ms per assertion
- Supports batch processing
- Efficient regex-based extraction
- Context-aware clause boundary detection

## Limitations

- Regex-based approach may miss complex conditional structures
- Requires well-formed Serbian/English text
- May need pattern tuning for specific legal domains
- Does not handle nested conditions explicitly

## Future Improvements

- Add support for nested conditions
- Implement ML-based condition classification
- Add support for more languages
- Improve clause boundary detection with NLP
- Add condition dependency analysis