# Module 6: Assertion Extractor

**Port:** 8106  
**Version:** 1.0.0  
**Status:** Production Ready

## Overview

Assertion Extractor module extracts legal assertions from legal unit content. An assertion is a fundamental unit of legal content that can be compared with other assertions for conflict detection.

## Features

- **Sentence Splitting**: Splits legal text into individual sentences
- **Assertion Detection**: Identifies legal assertions using pattern matching
- **Confidence Scoring**: Calculates confidence score for each assertion
- **Database Storage**: Stores assertions with full metadata
- **Query API**: Retrieve assertions by job, confidence, etc.

## API Endpoints

### POST /api/extract
Extract assertions from legal unit content.

**Request:**
```json
{
  "legal_unit": {
    "unit_id": "uuid-123",
    "content": "Poslodavac je dužan da zaposlenom isplati zaradu.",
    "unit_type": "article",
    "number": "1"
  },
  "language": "sr",
  "min_confidence": 0.5
}
```

**Response:**
```json
{
  "module": "assertion-extractor",
  "status": "success",
  "job_id": "uuid-job-456",
  "output": {
    "assertions": [
      {
        "assertion_id": "uuid-a1",
        "text": "Poslodavac je dužan da zaposlenom isplati zaradu.",
        "confidence": 0.85,
        "sentence_index": 0,
        "start_char": 0,
        "end_char": 52
      }
    ],
    "stats": {
      "total_assertions": 1,
      "total_sentences": 1,
      "avg_confidence": 0.85
    }
  },
  "metadata": {
    "processing_time_ms": 12.5
  }
}
```

### GET /api/job/{job_id}
Get extraction job details with all assertions.

### GET /api/assertions/high-confidence
Get assertions with high confidence scores.

**Query Parameters:**
- `min_confidence`: Minimum confidence threshold (default: 0.8)
- `limit`: Maximum number of results (default: 100)

### GET /health
Health check endpoint.

## Assertion Detection Logic

### Sentence Splitting
Text is split into sentences using regex pattern matching for Serbian sentence endings (`.`, `!`, `?`).

### Assertion Indicators
The following patterns indicate legal assertions in Serbian:
- `je dužan`, `je obavezan` - obligation
- `mora`, `treba` - must, should
- `može`, `ima pravo` - permission
- `zabranjeno je`, `ne sme` - prohibition
- `utvrđuje se`, `određuje se` - determination
- `smatra se`, `računa se` - consideration

### Confidence Calculation
Confidence score (0-1) is calculated based on:
- **Assertion indicators**: +0.3 per match (max +0.6)
- **Sentence length**: +0.1 for 5+ words, +0.1 for 10+ words
- **Penalties**: -0.2 for very short sentences (<3 words)

## Database Schema

### extraction_jobs
```sql
CREATE TABLE extraction_jobs (
    job_id TEXT PRIMARY KEY,
    legal_unit_id TEXT NOT NULL,
    input_content TEXT NOT NULL,
    output_assertions TEXT NOT NULL,
    total_assertions INTEGER NOT NULL,
    processing_time_ms REAL NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

### extracted_assertions
```sql
CREATE TABLE extracted_assertions (
    assertion_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    text TEXT NOT NULL,
    confidence REAL NOT NULL,
    sentence_index INTEGER NOT NULL,
    start_char INTEGER NOT NULL,
    end_char INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (job_id) REFERENCES extraction_jobs(job_id)
);
```

## Usage Example

```python
import requests

# Extract assertions
response = requests.post("http://localhost:8106/api/extract", json={
    "legal_unit": {
        "unit_id": "article-1",
        "content": "Poslodavac je dužan da zaposlenom isplati zaradu. Zaposleni ima pravo na odmor."
    },
    "language": "sr",
    "min_confidence": 0.5
})

result = response.json()
print(f"Extracted {result['output']['stats']['total_assertions']} assertions")

for assertion in result['output']['assertions']:
    print(f"- {assertion['text']} (confidence: {assertion['confidence']})")
```

## Running the Module

```bash
# Install dependencies
pip install -r requirements.txt

# Run the module
python main.py
```

The module will start on port 8106.

## Integration with Other Modules

Module 6 receives legal units from Module 4 (Legal Parser) and extracts assertions for further processing by:
- Module 10: Embedding Generator (for semantic search)
- Module 17: Candidate Finder (for conflict detection)
- Module 18: Conflict Detector (for conflict analysis)

## Performance

- **Average processing time**: 10-20ms per legal unit
- **Throughput**: ~50-100 legal units per second
- **Database**: SQLite with indexed queries

## Future Improvements

1. **Advanced NLP**: Integrate spaCy or similar for better sentence splitting
2. **Machine Learning**: Train ML model for assertion classification
3. **Multi-language**: Support for English and other languages
4. **Caching**: Cache frequently extracted assertions
5. **Batch Processing**: Process multiple legal units in parallel