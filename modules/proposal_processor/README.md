# Proposal Processor Module

This module processes legal proposal documents (PDF, DOCX, or text) and prepares them for conflict detection by running them through the same pipeline as existing laws.

## Overview

The Proposal Processor takes a legal proposal in various formats and:
1. Extracts text from the source (file, URL, or direct text)
2. Normalizes the text (latinization)
3. Parses the legal structure
4. Extracts normative content
5. Extracts conditions
6. Extracts assertions
7. Returns structured data ready for conflict detection

## Features

- **Multiple Input Types**: File path, URL, or direct text
- **Same Pipeline**: Uses the same processing pipeline as existing laws
- **Auto-detection**: Automatically detects document title
- **Metadata Tracking**: Tracks author, submission date, processing time
- **Error Handling**: Graceful error handling with partial results
- **Export Format**: Compatible with JSON export format for Qdrant loading

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from modules.proposal_processor import ProposalProcessorService, ProposalInput

# Initialize service
processor = ProposalProcessorService()

# Process from file
proposal_input = ProposalInput(
    source_type="file",
    source="path/to/proposal.pdf",
    title="Predlog zakona o radu",
    author="Ministarstvo rada",
    submission_date="2024-01-15"
)

result = processor.process_proposal(proposal_input)

if result.success:
    print(f"Processed: {result.metadata.title}")
    print(f"Units: {result.metadata.total_units}")
    print(f"Normative: {result.metadata.total_normative}")
else:
    print(f"Errors: {result.errors}")
```

### Process from Text

```python
proposal_input = ProposalInput(
    source_type="text",
    source="""
    ZAKON O RADU
    
    Član 1.
    Ovim zakonom uređuju se radni odnosi...
    """,
    title="Predlog zakona o radu"
)

result = processor.process_proposal(proposal_input)
```

### Process from URL

```python
proposal_input = ProposalInput(
    source_type="url",
    source="https://example.com/proposal.pdf",
    title="Predlog zakona o radu"
)

result = processor.process_proposal(proposal_input)
```

### Export to JSON Format

```python
# Convert to same format as regular documents
json_data = result.to_json_export_format()

# Save to file
import json
with open('proposal_export.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

# Or load directly into Qdrant
from modules.qdrant_loader import QdrantLoaderService, LoaderConfig

config = LoaderConfig(qdrant_url="http://localhost:6333")
loader = QdrantLoaderService(config)

# Create temp JSON file
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)
    temp_path = f.name

# Load into Qdrant
from pathlib import Path
loader.load_document_from_json(Path(temp_path))
```

## Configuration

### Service URLs

By default, the processor connects to local services:

```python
processor = ProposalProcessorService(
    file_reader_url="http://localhost:8001",
    text_normalizer_url="http://localhost:8002",
    legal_parser_url="http://localhost:8003",
    normative_extractor_url="http://localhost:8006",
    condition_extractor_url="http://localhost:8008",
    assertion_extractor_url="http://localhost:8010"
)
```

### ProposalInput Parameters

- `source_type` (required): "file", "text", or "url"
- `source` (required): File path, URL, or text content
- `title` (optional): Proposal title (auto-detected if not provided)
- `document_type` (optional): Document type (default: "predlog_zakona")
- `author` (optional): Proposal author/submitter
- `submission_date` (optional): Submission date
- `skip_ocr` (optional): Skip OCR for scanned documents
- `force_reprocess` (optional): Force reprocessing even if cached

## Output Structure

### ProposalProcessingResult

```python
{
    "metadata": {
        "proposal_id": "proposal_abc123",
        "title": "Predlog zakona o radu",
        "document_type": "predlog_zakona",
        "author": "Ministarstvo rada",
        "submission_date": "2024-01-15",
        "processed_at": "2024-01-20T10:30:00",
        "processing_time_seconds": 12.5,
        "source_type": "file",
        "source": "path/to/proposal.pdf",
        "total_chars": 45000,
        "total_words": 7500,
        "total_units": 120,
        "total_normative": 85
    },
    "legal_units": [
        {
            "legal_unit_id": "proposal_abc123_001",
            "unit_type": "article",
            "content": "...",
            "normative_assertions": [...]
        }
    ],
    "raw_text": "...",
    "latinized_text": "...",
    "success": true,
    "errors": [],
    "warnings": []
}
```

## Integration with Conflict Detection

After processing a proposal, you can:

1. **Load into Qdrant** for semantic search
2. **Compare with existing laws** using conflict detector
3. **Generate conflict report** with severity levels

Example workflow:

```python
# 1. Process proposal
result = processor.process_proposal(proposal_input)

# 2. Load into Qdrant (optional, for persistent storage)
json_data = result.to_json_export_format()
# ... save and load into Qdrant

# 3. Detect conflicts (next module)
from modules.conflict_detector import ConflictDetectorService

detector = ConflictDetectorService()
conflicts = detector.detect_conflicts(result)

# 4. Display results
for conflict in conflicts:
    print(f"{conflict.severity}: {conflict.description}")
```

## Error Handling

The processor includes comprehensive error handling:

```python
result = processor.process_proposal(proposal_input)

if not result.success:
    print("Processing failed:")
    for error in result.errors:
        print(f"  - {error}")

if result.warnings:
    print("Warnings:")
    for warning in result.warnings:
        print(f"  - {warning}")
```

## Pipeline Steps

1. **Text Extraction** (Module 1: File Reader)
   - Extracts text from PDF, DOCX, or other formats
   - Handles OCR for scanned documents

2. **Text Normalization** (Module 2: Text Normalizer)
   - Converts Cyrillic to Latin script
   - Normalizes whitespace and formatting

3. **Legal Parsing** (Module 3: Legal Parser)
   - Identifies legal structure (articles, paragraphs, items)
   - Builds hierarchy tree

4. **Normative Extraction** (Module 6: Normative Extractor)
   - Extracts obligations, prohibitions, rights
   - Identifies normative language patterns

5. **Condition Extraction** (Module 8: Condition Extractor)
   - Extracts conditional clauses
   - Links conditions to normative content

6. **Assertion Extraction** (Module 10: Assertion Extractor)
   - Extracts general assertions
   - Classifies assertion types

## Testing

See `test_proposal_processor.py` for examples:

```bash
python test_proposal_processor.py
```

## Dependencies

- `requests`: HTTP client for service communication
- `pydantic`: Data validation and serialization

## Notes

- All processing services must be running
- Processing time depends on document size and complexity
- Large documents (>100 pages) may take several minutes
- Proposals are flagged with `is_proposal: true` in metadata