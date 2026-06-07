# Module 9: Assertion Classifier

## Overview
Classifies legal assertions into five distinct types based on their semantic meaning and legal function.

## Classification Types

### 1. Obligation
Requirements, duties, and mandatory actions.
- **Patterns**: "mora", "dužan je", "obavezan je", "potrebno je"
- **Example**: "Poslodavac mora da obezbedi bezbedne uslove rada"

### 2. Prohibition
Restrictions, bans, and forbidden actions.
- **Patterns**: "ne sme", "zabranjeno", "ne dozvoljava se"
- **Example**: "Zaposleni ne sme da koristi službene resurse u privatne svrhe"

### 3. Permission
Rights, allowances, and permitted actions.
- **Patterns**: "može", "ima pravo", "dozvoljeno", "ovlašćen"
- **Example**: "Radnik može da zatraži godišnji odmor"

### 4. Deadline
Time-bound requirements and temporal constraints.
- **Patterns**: "u roku od", "najkasnije do", "pre isteka"
- **Example**: "Zahtev se podnosi u roku od 30 dana"

### 5. Definition
Definitions, explanations, and conceptual clarifications.
- **Patterns**: "jeste", "smatra se", "predstavlja", "podrazumeva"
- **Example**: "Radni odnos jeste odnos između poslodavca i zaposlenog"

## API Endpoints

### POST /classify
Classify a single assertion.

**Request:**
```json
{
  "assertion": {
    "assertion_id": "assert_001",
    "text": "Poslodavac mora da obezbedi bezbedne uslove rada",
    "confidence": 0.9
  },
  "language": "sr",
  "min_confidence": 0.5
}
```

**Response:**
```json
{
  "module": "assertion-classifier",
  "status": "success",
  "job_id": "uuid",
  "output": {
    "classification": {
      "assertion_id": "assert_001",
      "assertion_type": "obligation",
      "confidence": 0.95,
      "matched_patterns": ["mora"],
      "reasoning": "Matched 1 pattern(s) for obligation"
    },
    "stats": {
      "total_patterns_checked": 45,
      "patterns_matched": 1,
      "type_scores": {
        "obligation": 0.95,
        "prohibition": 0.0,
        "permission": 0.0,
        "deadline": 0.0,
        "definition": 0.0
      }
    }
  },
  "metadata": {
    "processing_time_ms": 5,
    "language": "sr",
    "min_confidence": 0.5
  }
}
```

### POST /classify/batch
Classify multiple assertions at once.

**Request:**
```json
[
  {
    "assertion_id": "assert_001",
    "text": "Poslodavac mora da obezbedi bezbedne uslove rada",
    "confidence": 0.9
  },
  {
    "assertion_id": "assert_002",
    "text": "Zaposleni ne sme da koristi službene resurse",
    "confidence": 0.85
  }
]
```

### GET /stats
Get classification statistics.

**Query Parameters:**
- `days`: Number of days to retrieve (default: 7)

**Response:**
```json
{
  "total_classifications": 150,
  "type_distribution": {
    "obligation": 60,
    "prohibition": 30,
    "permission": 25,
    "deadline": 20,
    "definition": 15
  },
  "recent_stats": [...]
}
```

### GET /patterns
Get available classification patterns.

**Query Parameters:**
- `language`: Language code (default: "sr")

**Response:**
```json
{
  "obligation": {
    "count": 9,
    "avg_confidence": 0.88,
    "patterns": ["mora", "dužan je", "obavezan je", ...]
  },
  "prohibition": {
    "count": 9,
    "avg_confidence": 0.90,
    "patterns": ["ne sme", "zabranjeno", ...]
  },
  ...
}
```

### GET /classification/{job_id}
Get classification by job ID.

### GET /classifications/type/{assertion_type}
Get all classifications of a specific type.

**Query Parameters:**
- `limit`: Maximum number of results (default: 100)

## Configuration

### Port
- **Default**: 8109
- **Configurable**: Yes (in main.py)

### Database
- **Type**: SQLite
- **Location**: `data/databases/assertion_classifier.db`
- **Tables**: 
  - `classification_jobs`: Individual classification records
  - `classification_stats`: Daily aggregated statistics

## Pattern Matching Strategy

1. **Multi-Pattern Matching**: Each assertion is checked against all pattern types
2. **Confidence Scoring**: Patterns have predefined confidence scores (0.7-0.95)
3. **Type Selection**: Type with highest average confidence is selected
4. **Threshold Filtering**: Results below min_confidence are defaulted to "obligation"
5. **Pattern Prioritization**: More specific patterns have higher confidence scores

## Usage Example

```python
import requests

# Classify a single assertion
response = requests.post(
    "http://localhost:8109/classify",
    json={
        "assertion": {
            "assertion_id": "assert_001",
            "text": "Poslodavac mora da obezbedi bezbedne uslove rada",
            "confidence": 0.9
        },
        "language": "sr",
        "min_confidence": 0.5
    }
)

result = response.json()
print(f"Type: {result['output']['classification']['assertion_type']}")
print(f"Confidence: {result['output']['classification']['confidence']}")
```

## Running the Module

```bash
# Start the module
python -m modules.assertion_classifier.main

# Or use the batch script
.\restart_all_modules.bat
```

## Testing

```bash
# Run unit tests
python -m pytest tests/test_assertion_classifier.py

# Test with curl
curl -X POST http://localhost:8109/classify \
  -H "Content-Type: application/json" \
  -d '{
    "assertion": {
      "assertion_id": "test_001",
      "text": "Poslodavac mora da obezbedi bezbedne uslove rada",
      "confidence": 0.9
    }
  }'
```

## Performance

- **Average Processing Time**: 5-10ms per assertion
- **Batch Processing**: ~2-5ms per assertion
- **Pattern Matching**: Regex-based, highly efficient
- **Database**: SQLite with indexed queries

## Dependencies

- fastapi==0.104.1
- uvicorn==0.24.0
- pydantic==2.5.0
- sqlalchemy==2.0.23

## Integration

This module integrates with:
- **Module 6 (Assertion Extractor)**: Receives assertions for classification
- **Module 10 (Embedding Generator)**: Provides classified assertions for embedding
- **Module 11 (Vector Store)**: Stores classified assertions with embeddings

## Future Enhancements

1. **Machine Learning**: Train ML model on classified data
2. **Multi-Label Classification**: Support assertions with multiple types
3. **Confidence Calibration**: Adjust confidence scores based on historical accuracy
4. **Pattern Learning**: Automatically discover new patterns from data
5. **Cross-Language Support**: Add English and other language patterns