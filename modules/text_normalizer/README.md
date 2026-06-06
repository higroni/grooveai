# Text Normalizer Module

**Port**: 8102  
**Purpose**: Normalize text by removing extra whitespace, fixing encoding, etc.

## Features

- Remove extra whitespace (spaces, tabs)
- Normalize newlines (CRLF, CR, LF)
- Fix common encoding issues (BOM, zero-width characters, etc.)
- Configurable normalization options
- Stores job history in SQLite database
- Provides CRUD API for job management

## Installation

```bash
pip install -r requirements.txt
```

## Running the Module

```bash
# From project root
python -m modules.text_normalizer.main
```

The module will start on port 8102 (configurable in config.yaml).

## API Endpoints

### POST /api/normalize
Normalize text.

**Request**:
```json
{
  "text": "Zakon   o  radu\n\n\nČlan 1",
  "options": {
    "remove_extra_whitespace": true,
    "normalize_newlines": true,
    "fix_encoding": true
  }
}
```

**Response**:
```json
{
  "module": "text-normalizer",
  "status": "success",
  "job_id": "uuid-job2",
  "output": {
    "normalized_text": "Zakon o radu\nČlan 1",
    "changes_made": ["removed_extra_whitespace", "normalized_newlines"]
  },
  "metadata": {
    "processing_time_ms": 12,
    "original_length": 28,
    "normalized_length": 20
  }
}
```

### GET /api/jobs/{job_id}
Get job details by ID.

### GET /api/jobs
List all jobs (with pagination).

**Query Parameters**:
- `limit`: Maximum number of jobs (default: 100)
- `offset`: Number of jobs to skip (default: 0)

### DELETE /api/jobs/{job_id}
Delete a job.

## Database Schema

```sql
CREATE TABLE text_normalizer_jobs (
    job_id TEXT PRIMARY KEY,
    input_text TEXT NOT NULL,
    output_text TEXT NOT NULL,
    changes_made TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP
);
```

## Configuration

All configuration is read from `config.yaml`:

```python
from shared.config_loader import config

# Get module port
port = config.get_module_port("text_normalizer")  # 8102

# Get database URL
db_url = config.get_database_url("text_normalizer")
```

## Normalization Options

### remove_extra_whitespace
- Replaces tabs with spaces
- Removes multiple consecutive spaces
- Trims whitespace from start/end of lines
- Trims whitespace from entire text

### normalize_newlines
- Converts CRLF (\\r\\n) to LF (\\n)
- Converts CR (\\r) to LF (\\n)
- Reduces 3+ consecutive newlines to 2

### fix_encoding
- Removes BOM (Byte Order Mark)
- Removes zero-width spaces
- Converts non-breaking spaces to regular spaces

## Example Usage

```python
import requests

url = "http://localhost:8102/api/normalize"
payload = {
    "text": "Zakon   o  radu\\n\\n\\nČlan 1",
    "options": {
        "remove_extra_whitespace": true,
        "normalize_newlines": true,
        "fix_encoding": true
    }
}

response = requests.post(url, json=payload)
print(response.json())
```

## Integration with Module 1

Text Normalizer can be used after File Reader to clean up extracted text:

```python
# Step 1: Read file
file_response = requests.post("http://localhost:8101/api/read", json={
    "file_path": "document.pdf",
    "file_type": "pdf"
})
extracted_text = file_response.json()["output"]["text"]

# Step 2: Normalize text
normalize_response = requests.post("http://localhost:8102/api/normalize", json={
    "text": extracted_text
})
normalized_text = normalize_response.json()["output"]["normalized_text"]