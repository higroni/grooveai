# Module 4: Legal Parser - Akoma Ntoso Compatible Data Model

**Port:** 8104  
**Status:** Design Phase  
**Last Updated:** 2026-06-06

---

## Overview

Module 4 (Legal Parser) parsira strukturu srpskih pravnih dokumenata i kreira **Akoma Ntoso-kompatibilan data model** u JSON formatu. XML export/import je opciona funkcionalnost koja se može dodati kasnije.

### Key Design Principles

1. **JSON-Only Storage:**
   - Čuvamo samo JSON format (brzo, efikasno)
   - Nema XML generisanja u runtime-u
   - Štedi vreme i storage

2. **Akoma Ntoso-Compatible Structure:**
   - Data model prati Akoma Ntoso standard
   - Objekti i atributi odgovaraju Akoma Ntoso elementima
   - Future-ready za XML export/import

3. **Serbian Legal Structure:**
   - Član (Article) → `unit_type: "article"`
   - Stav (Paragraph) → `unit_type: "paragraph"`
   - Tačka (Point) → `unit_type: "point"`
   - Podtačka (Subpoint) → `unit_type: "list"`
   - Alineja (Indent) → `unit_type: "indent"`

---

## Data Model (Akoma Ntoso Compatible)

### LegalUnit (Core Entity)

```python
class LegalUnit:
    """
    Akoma Ntoso-compatible legal unit.
    Maps directly to Akoma Ntoso XML elements.
    """
    legal_unit_id: str              # UUID (deterministic from path)
    parent_legal_unit_id: str | None  # Parent UUID (hierarchy)
    
    # Akoma Ntoso core fields
    unit_type: str                  # article, paragraph, point, list, indent
    number: str                     # "1", "2", "1a", etc.
    ordinal: int                    # Sequential order (1, 2, 3...)
    heading: str | None             # Naslov (e.g., "Predmet zakona")
    content_text: str               # Sadržaj teksta
    path: str                       # Hierarchical path (e.g., "article:1/paragraph:1")
    
    # Akoma Ntoso metadata
    akoma_eid: str                  # Akoma Ntoso eId (e.g., "article_1__para_1")
    akoma_wid: str | None           # Akoma Ntoso wId (optional)
    
    # Additional metadata
    metadata: dict                  # Flexible metadata storage
```

### Document (Container)

```python
class Document:
    """
    Akoma Ntoso-compatible document container.
    Maps to <act> element in Akoma Ntoso.
    """
    source_uri: str                 # File path or URL
    filename: str                   # Original filename
    document_type: str              # "law", "regulation", "decree", etc.
    title: str | None               # Document title
    language_code: str              # "sr" (Serbian)
    
    # Legal units (hierarchical)
    legal_units: list[LegalUnit]    # All parsed legal units
    
    # Document metadata (FRBR-compatible)
    metadata: dict                  # Publication date, official gazette, etc.
```

### Akoma Ntoso eId Format

```python
# Examples of eId generation:
article_1                           # Član 1
article_1__para_1                   # Član 1, stav 1
article_1__para_1__point_1          # Član 1, stav 1, tačka 1
article_1__para_1__point_1__list_1  # Član 1, stav 1, tačka 1, podtačka 1
article_1__para_1__indent_1         # Član 1, stav 1, alineja 1
```

---

## Database Schema (Simplified)

### Table: `legal_parser_jobs`

```sql
CREATE TABLE legal_parser_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Input
    input_text TEXT NOT NULL,                    -- Latinized text from Module 3
    source_uri TEXT NOT NULL,                    -- File path
    filename TEXT NOT NULL,                      -- Original filename
    
    -- Output (JSON only)
    canonical_json TEXT NOT NULL,                -- Akoma Ntoso-compatible JSON
    
    -- Statistics
    total_units INTEGER NOT NULL,                -- Total legal units parsed
    total_articles INTEGER NOT NULL,             -- Number of articles
    total_paragraphs INTEGER NOT NULL,           -- Number of paragraphs
    total_points INTEGER NOT NULL,               -- Number of points
    
    -- Document metadata
    document_title TEXT,                         -- Extracted title
    document_type TEXT DEFAULT 'law',            -- Document type
    language_code TEXT DEFAULT 'sr',             -- Language code
    
    -- Processing metadata
    processing_time_ms REAL NOT NULL,            -- Processing time
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
```sql
CREATE INDEX idx_legal_parser_created_at ON legal_parser_jobs(created_at);
CREATE INDEX idx_legal_parser_document_type ON legal_parser_jobs(document_type);
CREATE INDEX idx_legal_parser_filename ON legal_parser_jobs(filename);
```

---

## JSON Output Format (Akoma Ntoso Compatible)

### Example Output

```json
{
  "module": "legal-parser",
  "status": "success",
  "job_id": 1,
  "output": {
    "document": {
      "source_uri": "file:///documents/zakon_o_radu.pdf",
      "filename": "zakon_o_radu.pdf",
      "document_type": "law",
      "title": "Zakon o radu",
      "language_code": "sr",
      "metadata": {
        "publication_date": "2005-03-15",
        "official_gazette": "Službeni glasnik RS br. 24/2005",
        "enactment_date": "2005-03-15"
      }
    },
    "legal_units": [
      {
        "legal_unit_id": "550e8400-e29b-41d4-a716-446655440000",
        "parent_legal_unit_id": null,
        "unit_type": "article",
        "number": "1",
        "ordinal": 1,
        "heading": "Predmet zakona",
        "content_text": "",
        "path": "article:1",
        "akoma_eid": "article_1",
        "akoma_wid": null,
        "metadata": {}
      },
      {
        "legal_unit_id": "550e8400-e29b-41d4-a716-446655440001",
        "parent_legal_unit_id": "550e8400-e29b-41d4-a716-446655440000",
        "unit_type": "paragraph",
        "number": "1",
        "ordinal": 1,
        "heading": null,
        "content_text": "Ovim zakonom uredjuje se zasnivanje radnog odnosa.",
        "path": "article:1/paragraph:1",
        "akoma_eid": "article_1__para_1",
        "akoma_wid": null,
        "metadata": {}
      },
      {
        "legal_unit_id": "550e8400-e29b-41d4-a716-446655440002",
        "parent_legal_unit_id": "550e8400-e29b-41d4-a716-446655440000",
        "unit_type": "paragraph",
        "number": "2",
        "ordinal": 2,
        "heading": null,
        "content_text": "Ovaj zakon primenjuje se na:",
        "path": "article:1/paragraph:2",
        "akoma_eid": "article_1__para_2",
        "akoma_wid": null,
        "metadata": {}
      },
      {
        "legal_unit_id": "550e8400-e29b-41d4-a716-446655440003",
        "parent_legal_unit_id": "550e8400-e29b-41d4-a716-446655440002",
        "unit_type": "point",
        "number": "1",
        "ordinal": 1,
        "heading": null,
        "content_text": "zaposlene kod poslodavca;",
        "path": "article:1/paragraph:2/point:1",
        "akoma_eid": "article_1__para_2__point_1",
        "akoma_wid": null,
        "metadata": {}
      },
      {
        "legal_unit_id": "550e8400-e29b-41d4-a716-446655440004",
        "parent_legal_unit_id": "550e8400-e29b-41d4-a716-446655440002",
        "unit_type": "point",
        "number": "2",
        "ordinal": 2,
        "heading": null,
        "content_text": "poslodavce.",
        "path": "article:1/paragraph:2/point:2",
        "akoma_eid": "article_1__para_2__point_2",
        "akoma_wid": null,
        "metadata": {}
      }
    ],
    "statistics": {
      "total_units": 5,
      "total_articles": 1,
      "total_paragraphs": 2,
      "total_points": 2,
      "total_lists": 0,
      "total_indents": 0
    }
  },
  "metadata": {
    "processing_time_ms": 145.5,
    "parsing_method": "regex"
  }
}
```

---

## Parsing Strategy

### 1. Serbian Legal Document Patterns

**Article (Član):**
```regex
^Član\s+(\d+[a-z]?)\.?\s*$              # "Član 1."
^Član\s+(\d+[a-z]?)\.?\s+(.+)$          # "Član 1. Predmet zakona"
```

**Paragraph (Stav):**
```regex
^\((\d+)\)\s+(.+)$                      # "(1) Ovim zakonom..."
```

**Point (Tačka):**
```regex
^(\d+)\)\s+(.+)$                        # "1) zaposlene kod poslodavca;"
```

**Subpoint (Podtačka):**
```regex
^\((\d+)\)\s+(.+)$                      # "(1) prva podtačka" (within point)
```

**Indent (Alineja):**
```regex
^[-–—]\s+(.+)$                          # "- prva alineja"
```

### 2. Parsing Algorithm (Simplified)

```python
def parse_legal_document(text: str, source_uri: str, filename: str) -> dict:
    """
    Parse Serbian legal document into Akoma Ntoso-compatible JSON.
    
    Returns:
        dict: Akoma Ntoso-compatible JSON structure
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
        
        # Parse article
        if match := re.match(r'^Član\s+(\d+[a-z]?)\.?\s*(.*)$', line):
            number = match.group(1)
            heading = match.group(2).strip() or None
            
            current_article = {
                "legal_unit_id": generate_uuid(source_uri, f"article:{number}"),
                "parent_legal_unit_id": None,
                "unit_type": "article",
                "number": number,
                "ordinal": len([u for u in legal_units if u["unit_type"] == "article"]) + 1,
                "heading": heading,
                "content_text": "",
                "path": f"article:{number}",
                "akoma_eid": f"article_{number}",
                "akoma_wid": None,
                "metadata": {}
            }
            legal_units.append(current_article)
            current_paragraph = None
            current_point = None
        
        # Parse paragraph
        elif match := re.match(r'^\((\d+)\)\s+(.+)$', line):
            if current_article:
                number = match.group(1)
                content = match.group(2).strip()
                
                article_num = current_article["number"]
                path = f"article:{article_num}/paragraph:{number}"
                
                current_paragraph = {
                    "legal_unit_id": generate_uuid(source_uri, path),
                    "parent_legal_unit_id": current_article["legal_unit_id"],
                    "unit_type": "paragraph",
                    "number": number,
                    "ordinal": int(number),
                    "heading": None,
                    "content_text": content,
                    "path": path,
                    "akoma_eid": f"{current_article['akoma_eid']}__para_{number}",
                    "akoma_wid": None,
                    "metadata": {}
                }
                legal_units.append(current_paragraph)
                current_point = None
        
        # Parse point
        elif match := re.match(r'^(\d+)\)\s+(.+)$', line):
            if current_paragraph:
                number = match.group(1)
                content = match.group(2).strip()
                
                path = f"{current_paragraph['path']}/point:{number}"
                
                current_point = {
                    "legal_unit_id": generate_uuid(source_uri, path),
                    "parent_legal_unit_id": current_paragraph["legal_unit_id"],
                    "unit_type": "point",
                    "number": number,
                    "ordinal": int(number),
                    "heading": None,
                    "content_text": content,
                    "path": path,
                    "akoma_eid": f"{current_paragraph['akoma_eid']}__point_{number}",
                    "akoma_wid": None,
                    "metadata": {}
                }
                legal_units.append(current_point)
    
    # Build document structure
    document = {
        "source_uri": source_uri,
        "filename": filename,
        "document_type": "law",
        "title": extract_title(text),
        "language_code": "sr",
        "metadata": extract_metadata(text)
    }
    
    # Calculate statistics
    statistics = {
        "total_units": len(legal_units),
        "total_articles": len([u for u in legal_units if u["unit_type"] == "article"]),
        "total_paragraphs": len([u for u in legal_units if u["unit_type"] == "paragraph"]),
        "total_points": len([u for u in legal_units if u["unit_type"] == "point"]),
        "total_lists": len([u for u in legal_units if u["unit_type"] == "list"]),
        "total_indents": len([u for u in legal_units if u["unit_type"] == "indent"])
    }
    
    return {
        "document": document,
        "legal_units": legal_units,
        "statistics": statistics
    }
```

### 3. UUID Generation (Deterministic)

```python
from uuid import NAMESPACE_URL, uuid5

def generate_uuid(source_uri: str, path: str) -> str:
    """
    Generate deterministic UUID for legal unit.
    Same source_uri + path always produces same UUID.
    """
    return str(uuid5(NAMESPACE_URL, f"{source_uri}#{path}"))

# Example:
# source_uri = "file:///documents/zakon_o_radu.pdf"
# path = "article:1/paragraph:1"
# uuid = "550e8400-e29b-41d4-a716-446655440001" (always the same)
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
    """
    type_map = {
        "article": "article",
        "paragraph": "para",
        "point": "point",
        "list": "list",
        "indent": "indent"
    }
    
    short_type = type_map.get(unit_type, unit_type)
    
    if parent_eid:
        return f"{parent_eid}__{short_type}_{number}"
    return f"{short_type}_{number}"
```

---

## API Endpoints

### 1. Parse Legal Document
```http
POST /api/parse
Content-Type: application/json

{
  "text": "Clan 1.\nPredmet zakona\n(1) Ovim zakonom...",
  "source_uri": "file:///documents/zakon_o_radu.pdf",
  "filename": "zakon_o_radu.pdf"
}

Response 200:
{
  "module": "legal-parser",
  "status": "success",
  "job_id": 1,
  "output": {
    "document": {...},
    "legal_units": [...],
    "statistics": {...}
  },
  "metadata": {
    "processing_time_ms": 145.5
  }
}
```

### 2. Get Job
```http
GET /api/jobs/{job_id}

Response 200:
{
  "job_id": 1,
  "document": {...},
  "legal_units": [...],
  "statistics": {...},
  "processing_time_ms": 145.5,
  "created_at": "2026-06-06T14:00:00Z"
}
```

### 3. List Jobs
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

### 4. Delete Job
```http
DELETE /api/jobs/{job_id}

Response 200:
{
  "message": "Job deleted successfully"
}
```

### 5. Statistics
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

### 6. Health Check
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
├── database.py                # Database operations
├── models.py                  # SQLAlchemy models
├── schemas.py                 # Pydantic schemas (Akoma Ntoso compatible)
├── patterns.py                # Regex patterns for Serbian legal text
├── utils.py                   # UUID generation, eId generation
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
└── tests/
    ├── __init__.py
    ├── conftest.py            # Pytest fixtures
    ├── test_service.py        # Unit tests (parsing logic)
    ├── test_database.py       # Database persistence tests
    ├── test_utils.py          # UUID/eId generation tests
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
- Test UUID generation (deterministic)
- Test eId generation

### 2. Database Tests
- Test job creation
- Test job retrieval
- Test job deletion
- Test statistics
- Test pagination
- **Test JSON persistence**

### 3. Integration Tests
- Test full pipeline (Module 3 → Module 4)
- Test with real Serbian legal documents
- Test with complex hierarchies
- Test with edge cases

### 4. Test Coverage Target
- **80%+ code coverage**
- All critical paths tested
- Edge cases covered

---

## Performance Targets

- **Parsing Speed:** <200ms for typical document (100 articles)
- **Memory Usage:** <100MB for large documents (1000+ articles)
- **Database Operations:** <10ms for CRUD operations
- **JSON Serialization:** <20ms for typical document

---

## Future: XML Export/Import (Optional)

Kada bude potrebno, lako se može dodati XML export/import funkcionalnost:

### Export to Akoma Ntoso XML
```python
def export_to_akoma_ntoso_xml(document: dict, legal_units: list) -> str:
    """
    Convert Akoma Ntoso-compatible JSON to XML.
    Uses existing data model - no changes needed.
    """
    # Generate XML from JSON structure
    # All fields already map to Akoma Ntoso elements
    pass
```

### Import from Akoma Ntoso XML
```python
def import_from_akoma_ntoso_xml(xml_text: str) -> dict:
    """
    Parse Akoma Ntoso XML to JSON.
    Creates same data model as parser.
    """
    # Parse XML and create JSON structure
    # Maps directly to existing data model
    pass
```

---

## Benefits of This Approach

1. **Efficient Storage:**
   - Samo JSON (brzo, kompaktno)
   - Nema duplikacije (JSON + XML)
   - Manje storage prostora

2. **Fast Processing:**
   - Nema XML generisanja u runtime-u
   - Brže parsiranje
   - Brži API responses

3. **Future-Ready:**
   - Data model je Akoma Ntoso kompatibilan
   - XML export/import se lako dodaje
   - Nema potrebe za refaktorisanjem

4. **Standard Compliance:**
   - Prati Akoma Ntoso strukturu
   - Kompatibilan sa standardom
   - Interoperabilan sa drugim sistemima

5. **Flexibility:**
   - JSON je lakši za rad
   - Lakše query-ovanje
   - Lakša integracija sa drugim modulima

---

## References

- [Akoma Ntoso Official Site](http://www.akomantoso.org/)
- [OASIS LegalDocML TC](https://www.oasis-open.org/committees/legaldocml/)
- [Akoma Ntoso 3.0 Specification](http://docs.oasis-open.org/legaldocml/akn-core/v1.0/akn-core-v1.0.html)

---

*Document created: 2026-06-06*  
*Status: Design Complete, Ready for Implementation*