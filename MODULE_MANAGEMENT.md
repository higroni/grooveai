# GROOVE.AI - Module Management Guide

## Overview

This guide explains how to manage and test the GROOVE.AI microservice modules.

## Implemented Modules

Currently implemented modules:

1. **Module 1: File Reader** (Port 8101)
   - Reads PDF, DOCX, TXT files
   - Extracts text content

2. **Module 2: Text Normalizer** (Port 8102)
   - Normalizes whitespace
   - Removes special characters
   - Standardizes text formatting

3. **Module 3: Latinizer** (Port 8103)
   - Converts Cyrillic to Latin script
   - Handles Serbian language specifics

4. **Module 4: Legal Parser** (Port 8105)
   - Parses legal document structure
   - Extracts articles, paragraphs, points
   - Generates Akoma Ntoso-compatible JSON

6. **Module 6: Assertion Extractor** (Port 8106)
   - Extracts legal assertions from text
   - Pattern matching for Serbian legal indicators
   - Confidence scoring (0-1 scale)

## Management Scripts

### Windows Batch Files

#### `restart_all_modules.bat`
Stops all running modules and starts them fresh.

**Usage:**
```batch
restart_all_modules.bat
```

**What it does:**
1. Kills all Python processes on module ports (8101, 8102, 8103, 8105, 8107)
2. Starts each module in a separate CMD window
3. Waits for modules to initialize
4. Checks health of all modules

#### `stop_all_modules.bat`
Stops all running modules.

**Usage:**
```batch
stop_all_modules.bat
```

**What it does:**
1. Finds processes listening on module ports
2. Terminates those processes

### Manual Module Management

#### Starting Individual Modules

```batch
# Module 1: File Reader
python modules/file_reader/main.py

# Module 2: Text Normalizer
python modules/text_normalizer/main.py

# Module 3: Latinizer
python modules/latinizer/main.py

# Module 4: Legal Parser
python modules/legal_parser/main.py

# Module 6: Assertion Extractor
python modules/assertion_extractor/main.py
```

#### Checking Module Health

```bash
# Check all modules
curl http://localhost:8101/health
curl http://localhost:8102/health
curl http://localhost:8103/health
curl http://localhost:8105/health
curl http://localhost:8106/health
```

Or use Python:
```python
import requests

modules = [
    ('File Reader', 8101),
    ('Text Normalizer', 8102),
    ('Latinizer', 8103),
    ('Legal Parser', 8105),
    ('Assertion Extractor', 8106)
]

for name, port in modules:
    try:
        r = requests.get(f'http://localhost:{port}/health', timeout=2)
        if r.status_code == 200:
            print(f'[OK] {name} (port {port})')
        else:
            print(f'[ERROR] {name} (port {port}) - Status {r.status_code}')
    except:
        print(f'[ERROR] {name} (port {port}) - Not responding')
```

## Testing

### Individual Module Tests

Each module has its own test file:

```batch
# Module 6: Assertion Extractor
python test_module6_simple.py
```

### Integration Tests

#### Full Pipeline Test (Modules 1 → 2 → 3 → 4 → 6)

Tests the complete pipeline from PDF to extracted assertions:

```batch
python test_pipeline_modules_1_2_3_4_6.py
```

**What it tests:**
1. File Reader: Reads PDF file
2. Text Normalizer: Normalizes extracted text
3. Latinizer: Converts Cyrillic to Latin
4. Legal Parser: Parses legal structure
5. Assertion Extractor: Extracts assertions from articles

**Output files:**
- `pipeline_output_with_assertions.json` - Complete pipeline output
- `pipeline_output_assertions.txt` - Readable assertions text

#### Partial Pipeline Tests

```batch
# Modules 1 → 2 → 3 → 4
python test_pipeline_modules_1_2_3_4.py

# Modules 1 → 2 → 3
python test_pipeline_modules_1_2_3.py
```

## Troubleshooting

### Module Won't Start

1. **Check if port is already in use:**
   ```batch
   netstat -ano | findstr :8101
   ```

2. **Kill process on port:**
   ```batch
   # Find PID from netstat output, then:
   taskkill /F /PID <PID>
   ```

3. **Check module logs:**
   - Logs are in `data/logs/` directory
   - Each module has its own log file

### Module Health Check Fails

1. **Wait for initialization:**
   - Modules need 5-10 seconds to start
   - Check the CMD window for startup messages

2. **Check for errors:**
   - Look at the module's CMD window
   - Check log files in `data/logs/`

3. **Verify dependencies:**
   ```batch
   pip install -r modules/<module_name>/requirements.txt
   ```

### Integration Test Fails

1. **Ensure all modules are running:**
   ```batch
   restart_all_modules.bat
   ```

2. **Wait for initialization:**
   - Wait 10 seconds after starting modules
   - Check health endpoints

3. **Check test file path:**
   - Default test file: `DOCUMENTS/DEV/onedoc/radni_odnosi_0001_000001.pdf`
   - Configured in `config.yaml`

## Configuration

Module ports and settings are configured in `config.yaml`:

```yaml
network:
  modules:
    file_reader:
      host: "0.0.0.0"
      port: 8101
    text_normalizer:
      host: "0.0.0.0"
      port: 8102
    # ... etc
```

## Development Workflow

### Typical Development Session

1. **Start all modules:**
   ```batch
   restart_all_modules.bat
   ```

2. **Make code changes**

3. **Restart affected module:**
   - Close its CMD window
   - Run module manually:
     ```batch
     python modules/<module_name>/main.py
     ```

4. **Run tests:**
   ```batch
   python test_module6_simple.py
   python test_pipeline_modules_1_2_3_4_6.py
   ```

5. **Stop all modules when done:**
   ```batch
   stop_all_modules.bat
   ```

### Adding a New Module

1. Create module directory: `modules/<module_name>/`
2. Implement required files:
   - `__init__.py`
   - `models.py` (Pydantic + SQLAlchemy)
   - `service.py` (Business logic)
   - `database.py` (Database operations)
   - `api.py` (FastAPI endpoints)
   - `main.py` (Entry point)
   - `requirements.txt`
   - `README.md`

3. Add port to `config.yaml`
4. Update `restart_all_modules.bat`
5. Create integration test

## API Documentation

Each module exposes a FastAPI interface with automatic documentation:

- **Swagger UI:** `http://localhost:<port>/docs`
- **ReDoc:** `http://localhost:<port>/redoc`

Example:
- Module 6 Swagger: http://localhost:8107/docs

## Database

Each module has its own SQLite database in `data/databases/`:

- `file_reader.db`
- `text_normalizer.db`
- `latinizer.db`
- `legal_parser.db`
- `assertion_extractor.db`

## Logs

Logs are stored in `data/logs/` with daily rotation:

- `file_reader_YYYYMMDD.log`
- `text_normalizer_YYYYMMDD.log`
- `latinizer_YYYYMMDD.log`
- `legal_parser_YYYYMMDD.log`
- `assertion_extractor_YYYYMMDD.log`

## Next Steps

Planned modules:
- Module 7: Entity Recognizer (port 8108)
- Module 8: Conflict Detector (port 8118)
- Module 9: Compliance Checker (port 8109)
- Module 10: Embedding Generator (port 8104)

---

**Made with Bob**