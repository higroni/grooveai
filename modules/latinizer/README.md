# Latinizer Module

Module 3 in the GROOVE.AI pipeline - Converts Serbian Cyrillic text to Latin script.

## Overview

The Latinizer module converts Serbian Cyrillic text to Latin script using standard transliteration rules. This is a critical preprocessing step before embedding generation, as the BAAI/bge-m3 embedding model performs better with Latin script than Cyrillic for Serbian text.

## Port Assignment

- **Port**: 8103
- **Module Number**: 3

## Features

- Standard Serbian Cyrillic-to-Latin transliteration
- Character-by-character conversion
- Preserves non-Cyrillic characters (numbers, punctuation, Latin text)
- Tracks conversion statistics (number of Cyrillic characters converted)
- Fast processing (typically <2ms for standard documents)
- Database persistence of all conversions
- RESTful API with comprehensive endpoints

## Cyrillic-to-Latin Mapping

The module uses standard Serbian transliteration:

### Lowercase
- а→a, б→b, в→v, г→g, д→d, ђ→đ, е→e, ж→ž, з→z, и→i
- ј→j, к→k, л→l, љ→lj, м→m, н→n, њ→nj, о→o, п→p, р→r
- с→s, т→t, ћ→ć, у→u, ф→f, х→h, ц→c, ч→č, џ→dž, ш→š

### Uppercase
- А→A, Б→B, В→V, Г→G, Д→D, Ђ→Đ, Е→E, Ж→Ž, З→Z, И→I
- Ј→J, К→K, Л→L, Љ→Lj, М→M, Н→N, Њ→Nj, О→O, П→P, Р→R
- С→S, Т→T, Ћ→Ć, У→U, Ф→F, Х→H, Ц→C, Ч→Č, Џ→Dž, Ш→Š

## API Endpoints

### Health Check
```http
GET /health
```

Returns module health status.

**Response:**
```json
{
  "status": "healthy",
  "module": "latinizer",
  "port": 8103,
  "timestamp": "2026-06-06T14:25:00Z"
}
```

### Latinize Text
```http
POST /api/latinize
Content-Type: application/json

{
  "text": "Закон о раду регулише права и обавезе запослених."
}
```

**Response:**
```json
{
  "job_id": 1,
  "latinized_text": "Zakon o radu regulise prava i obaveze zaposlenih.",
  "input_length": 52,
  "output_length": 52,
  "cyrillic_chars_converted": 45,
  "processing_time_ms": 1.23,
  "created_at": "2026-06-06T14:25:00Z"
}
```

### Get Job by ID
```http
GET /api/jobs/{job_id}
```

Retrieves a specific latinization job.

### List Jobs
```http
GET /api/jobs?limit=10&offset=0
```

Lists latinization jobs with pagination.

### Delete Job
```http
DELETE /api/jobs/{job_id}
```

Deletes a specific job.

### Get Statistics
```http
GET /api/stats
```

Returns latinization statistics.

**Response:**
```json
{
  "total_jobs": 150,
  "total_chars_processed": 125000,
  "total_cyrillic_converted": 98000,
  "avg_processing_time_ms": 1.45
}
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install from project root
pip install -e .
```

## Usage

### Starting the Module

```bash
# From project root
python -m modules.latinizer.main
```

The module will start on port 8103.

### Using the Service Directly

```python
from modules.latinizer.service import service

# Latinize text
result = service.latinize("Закон о раду")
print(result["latinized_text"])  # "Zakon o radu"
print(result["cyrillic_chars_converted"])  # 10

# Check if text contains Cyrillic
has_cyrillic = service.is_cyrillic("Закон о раду")  # True

# Count Cyrillic characters
count = service.get_cyrillic_count("Закон о раду")  # 10
```

### Using the API

```python
import requests

# Latinize text
response = requests.post(
    "http://localhost:8103/api/latinize",
    json={"text": "Закон о раду"}
)
result = response.json()
print(result["latinized_text"])
```

## Database Schema

### LatinizerJob Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| input_text | Text | Original text (may contain Cyrillic) |
| output_text | Text | Latinized text |
| cyrillic_chars_converted | Integer | Number of Cyrillic characters converted |
| processing_time_ms | Float | Processing time in milliseconds |
| created_at | DateTime | Job creation timestamp |

## Pipeline Integration

The Latinizer module is Module 3 in the processing pipeline:

```
Module 1: File Reader (8101)
    ↓ Extract text from PDF/DOCX/TXT
Module 2: Text Normalizer (8102)
    ↓ Clean whitespace, newlines, encoding
Module 3: Latinizer (8103) ← YOU ARE HERE
    ↓ Convert Cyrillic → Latin
Module 4: Embedding Generator (8104)
    ↓ Generate embeddings (works better with Latin)
...
```

### Why Latinization is Important

The BAAI/bge-m3 embedding model, while multilingual, performs better with Latin script for Serbian text. By converting Cyrillic to Latin before embedding generation, we achieve:

1. **Better embedding quality**: More accurate semantic representations
2. **Improved similarity matching**: Better document comparison
3. **Consistent processing**: Uniform script across all documents

## Configuration

Module configuration is managed through [`config.yaml`](../../config.yaml):

```yaml
modules:
  latinizer:
    port: 8103
    database: "data/databases/latinizer.db"
    log_file: "logs/latinizer.log"
```

## Logging

Logs are written to `logs/latinizer.log` with daily rotation. Log level is configured in `config.yaml`.

Example log entries:
```
2026-06-06 14:25:00 [INFO] Latinizer service initialized
2026-06-06 14:25:01 [INFO] Received latinization request for 52 characters
2026-06-06 14:25:01 [DEBUG] Latinized 52 chars, converted 45 Cyrillic chars in 1.23ms
2026-06-06 14:25:01 [INFO] Latinization job 1 completed successfully
```

## Performance

- **Processing Speed**: ~1-2ms for typical documents
- **Throughput**: Can process thousands of characters per second
- **Memory**: Minimal memory footprint (no ML models)
- **Scalability**: Stateless service, easily horizontally scalable

## Testing

```bash
# Run tests
pytest modules/latinizer/tests/

# Run with coverage
pytest modules/latinizer/tests/ --cov=modules.latinizer
```

## Error Handling

The module handles various error scenarios:

- **Invalid input**: Returns 422 Unprocessable Entity
- **Database errors**: Returns 500 Internal Server Error with details
- **Job not found**: Returns 404 Not Found

All errors are logged with full stack traces for debugging.

## Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation

## Development

### Adding New Transliteration Rules

To add or modify transliteration rules, edit the `CYRILLIC_TO_LATIN` dictionary in [`service.py`](service.py:26):

```python
CYRILLIC_TO_LATIN = {
    'а': 'a',
    'б': 'b',
    # Add new mappings here
}
```

### Testing Transliteration

```python
# Test the service directly
python -m modules.latinizer.service
```

This will run example conversions and display results.

## Future Enhancements

Potential improvements for future versions:

1. **Batch processing**: Process multiple texts in one request
2. **Reverse conversion**: Latin to Cyrillic
3. **Custom mappings**: User-defined transliteration rules
4. **Language detection**: Auto-detect if text is Cyrillic or Latin
5. **Mixed script handling**: Better handling of mixed Cyrillic/Latin text

## License

Part of the GROOVE.AI project.

## Contact

For issues or questions about this module, please refer to the main project documentation.