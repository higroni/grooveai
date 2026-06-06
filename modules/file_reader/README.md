# File Reader Module

**Port**: 8101  
**Purpose**: Read PDF, DOCX, and TXT files and extract raw text

## Features

- Reads PDF files using PyPDF2
- Reads DOCX files using python-docx
- Reads TXT files with automatic encoding detection
- Stores job history in SQLite database
- Provides CRUD API for job management

## Installation

```bash
pip install -r requirements.txt
```

## Running the Module

```bash
# From project root
python -m modules.file_reader.main
```

The module will start on port 8101 (configurable in config.yaml).

## Testing

### Automated Unit Tests

Run all unit tests with coverage:

```bash
# Run all tests
python modules/file_reader/run_tests.py

# Or use pytest directly
pytest modules/file_reader/tests -v --cov=modules.file_reader

# Run specific test file
pytest modules/file_reader/tests/test_service.py -v

# Run specific test
pytest modules/file_reader/tests/test_service.py::TestFileReaderService::test_read_txt_file -v
```

### Manual Testing

```bash
# Test with sample file
python modules/file_reader/test_module.py
```

### Test Coverage

The test suite includes:
- **Service Tests** (test_service.py): 15+ unit tests covering file reading logic
- **API Tests** (test_api.py): 20+ integration tests covering all API endpoints
- **Coverage Target**: 80%+ code coverage

Test categories:
- File reading (PDF, DOCX, TXT)
- Encoding detection
- Error handling
- API endpoints (CRUD operations)
- Database persistence
- Edge cases (empty files, special characters, Cyrillic text)

## API Endpoints

### POST /api/read
Read a file and extract text.

**Request**:
```json
{
  "file_path": "/path/to/document.pdf",
  "file_type": "pdf"
}
```

**Response**:
```json
{
  "module": "file-reader",
  "status": "success",
  "job_id": "uuid-job1",
  "output": {
    "text": "Extracted text...",
    "encoding": "utf-8",
    "char_count": 15234,
    "page_count": 45
  },
  "metadata": {
    "processing_time_ms": 234,
    "file_path": "/path/to/document.pdf"
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
CREATE TABLE file_reader_jobs (
    job_id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    status TEXT NOT NULL,
    output_text TEXT,
    char_count INTEGER,
    page_count INTEGER,
    processing_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

## Configuration

All configuration is read from `config.yaml`:

```python
from shared.config_loader import config

# Get module port
port = config.get_module_port("file_reader")  # 8101

# Get database URL
db_url = config.get_database_url("file_reader")

# Get sample file for testing
sample_file = config.get_sample_file()
```

## Supported File Types

- **PDF**: Uses PyPDF2 for text extraction
- **DOCX**: Uses python-docx for text extraction
- **TXT**: Automatic encoding detection (UTF-8, UTF-8-BOM, CP1252, Latin-1)

## Error Handling

- `404`: File not found
- `400`: Invalid file type or parameters
- `500`: Internal processing error

All errors are logged and stored in the database.