` - Sadržaj
   - `<p>` - Paragraf teksta

---

## Database Schema

### Table: `legal_parser_jobs`

```sql
CREATE TABLE legal_parser_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input_text TEXT NOT NULL,                    -- Latinized text from Module 3
    canonical_json TEXT NOT NULL,                -- JSON format (runtime)
    akoma_ntoso_xml TEXT NOT NULL,               -- XML format (interoperability)
    total_units INTEGER NOT NULL,                -- Total legal units parsed
    total_articles INTEGER NOT NULL,             -- Number of articles
    total_paragraphs INTEGER NOT NULL,           -- Number of paragraphs
    total_points INTEGER NOT NULL,               -- Number of points
    document_title TEXT,                         -- Extracted title
    document_type TEXT DEFAULT 'law',            -- Document type
    language_code TEXT DEFAULT 'sr',             -- Language code
    processing_time_ms REAL NOT NULL,            -- Processing time
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
```sql
CREATE INDEX idx_legal_parser_created_at ON legal_parser_jobs(created_at);
CREATE INDEX idx_legal_parser_document_type ON legal_parser_jobs(document_type);
```

---

## Parsing Strategy

### 1. Serbian Legal Document Patterns

**Article (Član):**
```regex
^Član\s+(\d+[a-z]?)\.?\s*$
^Član\s+(\d+[a-z]?)\.?\s+(.+)$  # with heading
```

**Paragraph (Stav):**
```regex
^\((\d+)\)\s+(.+)$
```

**Point (Tačka):**
```regex
^(\d+)\)\s+(.+)$
```

**Subpoint (Podtačka):**
```regex
^\((\d+)\)\s+(.+)$  # within a point
```

**Indent (Alineja):**
```regex
^[-–—]\s+(.+)$
```

### 2. Parsing Algorithm

```python
def parse_legal_document(text: str) -> CanonicalDocument:
    """
    Parse Serbian legal document into Akoma Ntoso structure.
    
    Steps:
    1. Extract document metadata (title, type, date)
    2. Split text into lines
    3. Identify legal units using regex patterns
    4. Build hierarchical structure
    5. Generate UUIDs for each unit
    6. Create canonical JSON
    7. Export to Akoma Ntoso XML
    """
    lines = text.split('\n')
    legal_units = []
    current_article = None
    current_paragraph = None
    current_point = None
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        # Check for article
        if match := re.match(r'^Član\s+(\d+[a-z]?)\.?\s*$', line):
            current_article = create_article(match, line_num)
            legal_units.append(current_article)
            current_paragraph = None
            current_point = None
            
        # Check for article with heading
        elif match := re.match(r'^Član\s+(\d+[a-z]?)\.?\s+(.+)$', line):
            current_article = create_article_with_heading(match, line_num)
            legal_units.append(current_article)
            current_paragraph = None
            current_point = None
            
        # Check for paragraph
        elif match := re.match(r'^\((\d+)\)\s+(.+)$', line):
            if current_article:
                current_paragraph = create_paragraph(
                    match, line_num, current_article
                )
                legal_units.append(current_paragraph)
                current_point = None
                
        # Check for point
        elif match := re.match(r'^(\d+)\)\s+(.+)$', line):
            if current_paragraph:
                current_point = create_point(
                    match, line_num, current_paragraph
                )
                legal_units.append(current_point)
                
        # Check for indent
        elif match := re.match(r'^[-–—]\s+(.+)$', line):
            if current_paragraph:
                indent = create_indent(
                    match, line_num, current_paragraph
                )
                legal_units.append(indent)
    
    return build_canonical_document(legal_units)
```

### 3. UUID Generation

```python
from uuid import NAMESPACE_URL, uuid5

def generate_legal_unit_id(source_uri: str, path: str) -> str:
    """Generate deterministic UUID for legal unit."""
    return str(uuid5(NAMESPACE_URL, f"{source_uri}#{path}"))

# Example:
# source_uri = "file:///documents/zakon_o_radu.pdf"
# path = "article:1/paragraph:1"
# uuid = uuid5(NAMESPACE_URL, "file:///documents/zakon_o_radu.pdf#article:1/paragraph:1")
```

### 4. Akoma Ntoso eId Generation

```python
def generate_akoma_eid(unit_type: str, number: str, parent_eid: str = None) -> str:
    """
    Generate Akoma Ntoso eId.
    
    Examples:
    - article_1
    - article_1__para_1
    - article_1__para_1__point_1
    - article_1__para_1__indent_1
    """
    if parent_eid:
        return f"{parent_eid}__{unit_type}_{number}"
    return f"{unit_type}_{number}"
```

---

## API Endpoints

### 1. Parse Legal Document
```http
POST /api/parse
Content-Type: application/json

{
  "text": "Clan 1.\nPredmet zakona\n(1) Ovim zakonom...",
  "source_uri": "file:///path/to/document.pdf",
  "filename": "zakon_o_radu.pdf",
  "document_type": "law",
  "language_code": "sr"
}

Response 200:
{
  "module": "legal-parser",
  "status": "success",
  "job_id": 1,
  "output": {
    "canonical_json": {...},
    "akoma_ntoso_xml": "<?xml version=\"1.0\"...>"
  },
  "metadata": {
    "processing_time_ms": 150,
    "units_parsed": 45
  }
}
```

### 2. Get Job
```http
GET /api/jobs/{job_id}

Response 200:
{
  "job_id": 1,
  "canonical_json": {...},
  "akoma_ntoso_xml": "<?xml version=\"1.0\"...>",
  "total_units": 45,
  "total_articles": 10,
  "total_paragraphs": 25,
  "total_points": 10,
  "document_title": "Zakon o radu",
  "processing_time_ms": 150,
  "created_at": "2026-06-06T14:00:00Z"
}
```

### 3. Export Akoma Ntoso XML
```http
GET /api/jobs/{job_id}/akoma-ntoso

Response 200:
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
  ...
</akomaNtoso>
```

### 4. Import Akoma Ntoso XML
```http
POST /api/import-akoma-ntoso
Content-Type: application/json

{
  "xml_text": "<?xml version=\"1.0\"...>",
  "source_uri": "file:///path/to/document.pdf",
  "filename": "zakon_o_radu.pdf"
}

Response 200:
{
  "module": "legal-parser",
  "status": "success",
  "job_id": 2,
  "output": {
    "canonical_json": {...},
    "akoma_ntoso_xml": "<?xml version=\"1.0\"...>"
  }
}
```

### 5. List Jobs
```http
GET /api/jobs?page=1&page_size=10

Response 200:
{
  "jobs": [...],
  "total": 100,
  "page": 1,
  "page_size": 10
}
```

### 6. Delete Job
```http
DELETE /api/jobs/{job_id}

Response 200:
{
  "message": "Job deleted successfully"
}
```

### 7. Statistics
```http
GET /api/stats

Response 200:
{
  "total_jobs": 100,
  "total_units_parsed": 4500,
  "total_articles": 1000,
  "total_paragraphs": 2500,
  "total_points": 1000,
  "avg_processing_time_ms": 145.5
}
```

### 8. Health Check
```http
GET /health

Response 200:
{
  "status": "healthy",
  "module": "legal-parser",
  "version": "1.0.0"
}
```

---

## Implementation Files

### Module Structure
```
modules/legal_parser/
├── __init__.py
├── main.py                    # FastAPI entry point (port 8104)
├── api.py                     # API endpoints
├── service.py                 # Business logic (parsing)
├── akoma_ntoso.py            # Akoma Ntoso XML generation/parsing
├── database.py                # Database operations
├── models.py                  # SQLAlchemy models
├── schemas.py                 # Pydantic schemas
├── patterns.py                # Regex patterns for Serbian legal text
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
└── tests/
    ├── __init__.py
    ├── conftest.py            # Pytest fixtures
    ├── test_service.py        # Unit tests (parsing logic)
    ├── test_akoma_ntoso.py   # Akoma Ntoso tests
    ├── test_database.py       # Database persistence tests
    └── pytest.ini             # Pytest configuration
```

---

## Dependencies

```txt
fastapi==0.115.6
uvicorn==0.34.0
sqlalchemy==2.0.36
pydantic==2.10.6
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.28.1
lxml==5.3.0                    # For XML processing (optional, better than ET)
```

---

## Testing Strategy

### 1. Unit Tests (Parsing Logic)
- Test article parsing
- Test paragraph parsing
- Test point parsing
- Test indent parsing
- Test heading extraction
- Test hierarchy building
- Test UUID generation
- Test eId generation

### 2. Akoma Ntoso Tests
- Test XML generation
- Test XML parsing (import)
- Test namespace handling
- Test metadata generation
- Test FRBR structure
- Test round-trip (export → import)

### 3. Database Tests
- Test job creation
- Test job retrieval
- Test job deletion
- Test statistics
- Test pagination
- **Test persistence of both JSON and XML**

### 4. Integration Tests
- Test full pipeline (Module 3 → Module 4)
- Test with real Serbian legal documents
- Test with complex hierarchies
- Test with edge cases

### 5. Test Coverage Target
- **80%+ code coverage**
- All critical paths tested
- Edge cases covered

---

## Performance Targets

- **Parsing Speed:** <200ms for typical document (100 articles)
- **Memory Usage:** <100MB for large documents (1000+ articles)
- **Database Operations:** <10ms for CRUD operations
- **XML Generation:** <50ms for typical document
- **XML Parsing:** <100ms for typical document

---

## Lessons Learned Integration

1. **Database Persistence Testing:**
   - All tests must verify data is correctly stored
   - Test both JSON and XML formats
   - Verify all fields are persisted

2. **Windows UTF-8 Encoding:**
   - Setup UTF-8 encoding in service.py
   - Handle Serbian diacritics correctly
   - Test with real Serbian text

3. **Modular Independence:**
   - Own database, logging, configuration
   - Can run standalone
   - No shared state with other modules

4. **Test Assertions:**
   - Verify correct Serbian legal structure
   - Test with real patterns from documents
   - Don't assume - verify everything

---

## Next Steps

1. **Implementation Phase 1: Core Parsing (Week 1)**
   - Implement patterns.py with regex patterns
   - Implement service.py with parsing logic
   - Implement models.py and database.py
   - Write unit tests for parsing

2. **Implementation Phase 2: Akoma Ntoso (Week 1)**
   - Implement akoma_ntoso.py for XML generation
   - Implement XML import functionality
   - Write Akoma Ntoso tests
   - Test round-trip conversion

3. **Implementation Phase 3: API & Integration (Week 1)**
   - Implement api.py with all endpoints
   - Implement main.py entry point
   - Write integration tests
   - Test with real documents

4. **Implementation Phase 4: Testing & Documentation (Week 1)**
   - Achieve 80%+ test coverage
   - Write comprehensive README.md
   - Test with Module 3 integration
   - Performance optimization

---

## Benefits of Akoma Ntoso

1. **International Standard:**
   - OASIS standard for legal documents
   - Used by parliaments worldwide
   - Interoperability with other systems

2. **Structured Data:**
   - Clear hierarchy
   - Semantic markup
   - Machine-readable

3. **Metadata Rich:**
   - FRBR model (Work, Expression, Manifestation)
   - Publication information
   - References and citations

4. **Versioning Support:**
   - Track amendments
   - Historical versions
   - Temporal validity

5. **Export/Import:**
   - Easy data exchange
   - Integration with legal databases
   - Archival format

---

## References

- [Akoma Ntoso Official Site](http://www.akomantoso.org/)
- [OASIS LegalDocML TC](https://www.oasis-open.org/committees/legaldocml/)
- [Akoma Ntoso 3.0 Specification](http://docs.oasis-open.org/legaldocml/akn-core/v1.0/akn-core-v1.0.html)
- [ZAIKON Canonical Module](../ZAIKON/backend/zaikon/modules/canonical/)

---

*Document created: 2026-06-06*  
*Status: Design Complete, Ready for Implementation*