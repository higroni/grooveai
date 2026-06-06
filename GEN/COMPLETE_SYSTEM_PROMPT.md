# ZAIKON - Complete System Regeneration Prompt

## Project Overview

ZAIKON is an AI-assisted legislative compliance review platform that helps legal professionals analyze draft regulations against existing legal corpus to detect conflicts, inconsistencies, and compliance issues.

## Core Functionality

### 1. Corpus Management
- Import legal documents (TXT, PDF, DOCX) into corpus collections
- Parse documents to extract legal structure (articles, paragraphs, sections)
- Extract normative assertions from legal text
- Store documents and assertions in SQLite database
- Build multiple indexes (keyword, vector, structure, reference graph)

### 2. Draft Review
- Parse draft regulation text
- Extract assertions from draft
- Compare draft assertions against corpus assertions
- Detect 127 types of legal conflicts across 8 categories
- Generate detailed findings with severity levels

### 3. Conflict Detection
- Slot-based matching (action, object, domain, modality)
- Candidate scoring with minimum threshold (0.25)
- Support for 127 conflict types organized in 8 categories
- Configurable conflict rules with active/inactive states

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: SQLite (centralized at `data/zaikon.db`)
- **Vector Store**: Qdrant (embedded mode at `data/qdrant_storage/`)
- **LLM Integration**: Ollama (local) with configurable models
- **Document Processing**: PyPDF2, python-docx, pdfplumber
- **API**: RESTful with OpenAPI documentation

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Custom components
- **State Management**: React hooks
- **API Client**: Fetch API

## Architecture

### Pipeline Architecture
The system uses a modular pipeline architecture where each operation is broken down into steps:

```
PipelineContext (inputs + artifacts)
  ↓
Step 1 (validates requirements, produces artifacts)
  ↓
Step 2 (validates requirements, produces artifacts)
  ↓
...
  ↓
Final Step (produces final artifacts)
```

### Key Pipeline Chains

#### 1. File-by-File Import Chain
```
ScanFolderStep
  ↓
DetectFileTypesStep
  ↓
InitializeImportProgressStep
  ↓
ProcessFilesWithProgressStep (per-file processing)
  ├─ ExtractTextStep
  ├─ NormalizeTextStep
  ├─ IdentifyLegalDocumentsStep
  ├─ ParseLegalStructureStep
  ├─ ConvertToCanonicalJsonStep
  ├─ ExtractNormativeAssertionsStep
  ├─ StoreAssertionsStep
  ├─ ExtractReferencesStep
  ├─ ResolveReferencesStep
  ├─ ExtractDefinitionsStep
  ├─ StoreDocumentsStep
  ├─ BuildKeywordIndexStep
  ├─ BuildVectorIndexStep
  ├─ BuildStructureIndexStep
  └─ BuildReferenceGraphStep
  ↓
AggregateIndexReportsStep
  ↓
GenerateImportReportStep
```

#### 2. Draft Review Chain
```
ParseDraftTextStep
  ↓
ExtractDraftAssertionsStep
  ↓
DetectConflictsStep
  ↓
StoreFindingsStep
  ↓
GenerateDraftReportStep
```

### Data Models

#### Canonical Document
```python
{
  "document_id": "uuid",
  "source_uri": "file:///path/to/doc.txt",
  "filename": "zakon_o_radu.txt",
  "title": "Zakon o radu",
  "document_type": "zakon",
  "sections": [
    {
      "section_id": "uuid",
      "section_type": "clan",
      "ordinal": 1,
      "title": "Član 1",
      "content": "...",
      "subsections": [...]
    }
  ]
}
```

#### Normative Assertion
```python
{
  "assertion_id": "uuid",
  "document_id": "uuid",
  "section_id": "uuid",
  "text": "Poslodavac je dužan da...",
  "action": "obaveza",
  "object": "poslodavac",
  "domain": "radni_odnosi",
  "modality": "must",
  "conditions": [...],
  "exceptions": [...]
}
```

#### Conflict Finding
```python
{
  "finding_id": "uuid",
  "draft_id": "uuid",
  "conflict_type": "contradictory_obligation",
  "category": "normative_conflicts",
  "severity": "high",
  "draft_assertion_id": "uuid",
  "corpus_assertion_id": "uuid",
  "explanation": "...",
  "recommendation": "..."
}
```

### Database Schema

#### Core Tables
```sql
-- Corpora
CREATE TABLE corpora (
    corpus_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT  -- JSON
);

-- Documents
CREATE TABLE corpus_documents (
    document_id TEXT PRIMARY KEY,
    corpus_id TEXT NOT NULL,
    source_uri TEXT NOT NULL,
    filename TEXT NOT NULL,
    title TEXT,
    document_type TEXT,
    canonical_json TEXT NOT NULL,  -- Full CanonicalDocument as JSON
    created_at TEXT NOT NULL,
    FOREIGN KEY (corpus_id) REFERENCES corpora(corpus_id)
);

-- Assertions
CREATE TABLE corpus_assertions (
    assertion_id TEXT PRIMARY KEY,
    corpus_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    assertion_json TEXT NOT NULL,  -- Full assertion as JSON
    created_at TEXT NOT NULL,
    FOREIGN KEY (corpus_id) REFERENCES corpora(corpus_id),
    FOREIGN KEY (document_id) REFERENCES corpus_documents(document_id)
);

-- Draft Reviews
CREATE TABLE draft_reviews (
    pipeline_run_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content_text TEXT NOT NULL,
    selected_corpus_id TEXT,
    status TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (selected_corpus_id) REFERENCES corpora(corpus_id)
);

-- Draft Artifacts (stores pipeline artifacts as JSON)
CREATE TABLE draft_artifacts (
    pipeline_run_id TEXT NOT NULL,
    artifact_name TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    payload TEXT NOT NULL,  -- JSON
    created_at TEXT NOT NULL,
    PRIMARY KEY (pipeline_run_id, artifact_name),
    FOREIGN KEY (pipeline_run_id) REFERENCES draft_reviews(pipeline_run_id)
);

-- Findings
CREATE TABLE findings (
    finding_id TEXT PRIMARY KEY,
    draft_id TEXT NOT NULL,
    conflict_type TEXT NOT NULL,
    category TEXT NOT NULL,
    severity TEXT NOT NULL,
    draft_assertion_id TEXT,
    corpus_assertion_id TEXT,
    explanation TEXT,
    recommendation TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (draft_id) REFERENCES draft_reviews(pipeline_run_id)
);

-- Import Progress Tracking
CREATE TABLE import_file_progress (
    corpus_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    status TEXT NOT NULL,
    document_id TEXT,
    assertions_count INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TEXT,
    completed_at TEXT,
    PRIMARY KEY (corpus_id, filename)
);
```

## API Endpoints

### Corpus Management
- `POST /api/v1/corpora` - Create new corpus
- `GET /api/v1/corpora` - List all corpora
- `GET /api/v1/corpora/{corpus_id}` - Get corpus details
- `POST /api/v1/corpora/{corpus_id}/import-folder` - Import documents
- `GET /api/v1/corpora/{corpus_id}/documents` - List corpus documents
- `GET /api/v1/corpora/{corpus_id}/assertions` - List corpus assertions

### Draft Reviews
- `POST /api/v1/draft-reviews` - Create draft review
- `GET /api/v1/draft-reviews` - List draft reviews
- `GET /api/v1/draft-reviews/{draft_id}` - Get draft details
- `POST /api/v1/draft-reviews/{draft_id}/run` - Start pipeline processing
- `GET /api/v1/draft-reviews/{draft_id}/findings` - Get conflict findings

### Configuration
- `GET /api/v1/llm/settings` - Get LLM settings
- `PUT /api/v1/llm/settings` - Update LLM settings
- `GET /api/v1/ontology/settings` - Get ontology settings
- `PUT /api/v1/ontology/settings` - Update ontology settings

## Conflict Detection System

### 8 Conflict Categories

1. **Normative Conflicts** (16 types)
   - Contradictory obligations, prohibitions, permissions
   - Conflicting definitions, scope, jurisdiction
   - Incompatible procedures, standards

2. **Temporal Conflicts** (15 types)
   - Retroactive vs prospective application
   - Conflicting effective dates, deadlines
   - Transitional period conflicts

3. **Hierarchical Conflicts** (18 types)
   - Constitutional violations
   - International law conflicts
   - Regulatory hierarchy violations

4. **Procedural Conflicts** (16 types)
   - Conflicting procedures, requirements
   - Incompatible documentation, notification
   - Appeal process conflicts

5. **Scope Conflicts** (17 types)
   - Overlapping jurisdiction, authority
   - Conflicting territorial, personal scope
   - Subject matter conflicts

6. **Penalty Conflicts** (14 types)
   - Conflicting sanctions, fines
   - Incompatible enforcement mechanisms
   - Double jeopardy issues

7. **Definitional Conflicts** (16 types)
   - Inconsistent terminology
   - Conflicting interpretations
   - Ambiguous references

8. **Implementation Conflicts** (15 types)
   - Resource allocation conflicts
   - Incompatible timelines
   - Contradictory reporting requirements

### Conflict Detection Algorithm

```python
def detect_conflicts(draft_assertion, corpus_assertions):
    candidates = []
    
    for corpus_assertion in corpus_assertions:
        # Calculate similarity score
        score = calculate_similarity(draft_assertion, corpus_assertion)
        
        # Minimum threshold
        if score < 0.25:
            continue
            
        # Require action or deadline match
        if not (matches_action(draft, corpus) or matches_deadline(draft, corpus)):
            continue
            
        candidates.append((corpus_assertion, score))
    
    # Sort by score descending
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Apply conflict rules
    findings = []
    for corpus_assertion, score in candidates:
        for rule in active_conflict_rules:
            if rule.matches(draft_assertion, corpus_assertion):
                finding = create_finding(
                    draft_assertion=draft_assertion,
                    corpus_assertion=corpus_assertion,
                    rule=rule,
                    score=score
                )
                findings.append(finding)
    
    return findings
```

## Critical Implementation Details

### 1. Assertion Storage
**CRITICAL**: Assertions MUST be stored during import. The `StoreAssertionsStep` is called within the per-file processing loop in `ProcessFilesWithProgressStep`, NOT in the main chain.

```python
# CORRECT: StoreAssertionsStep in per-file chain
def _process_single_file(self, file_item, context):
    steps = [
        ExtractTextStep(),
        # ... other steps ...
        ExtractNormativeAssertionsStep(),
        StoreAssertionsStep(),  # ← HERE, not in main chain
        # ... more steps ...
    ]
```

### 2. Artifact Flow
Each step validates required artifacts before running:

```python
class StoreAssertionsStep(PipelineStep):
    requires = ("normative_assertions",)
    produces = ("stored_assertions_report",)
    
    def run(self, context):
        # Validate artifact exists
        assertions = context.get_artifact("normative_assertions")
        if not assertions:
            # Handle missing artifact
            return context
        
        # Process and store
        # ...
```

### 3. Database Paths
**CRITICAL**: Use centralized database path from settings:

```python
from zaikon.core.config import settings

# CORRECT
db_path = settings.database_path  # "data/zaikon.db"

# WRONG - creates separate databases
db_path = "zaikon.db"
```

### 4. Legal Document Parsing
The parser must handle both Latin and Cyrillic Serbian text:

```python
# Article patterns
ARTICLE_PATTERNS = [
    r'^Član\s+(\d+)',           # Latin
    r'^Члан\s+(\d+)',           # Cyrillic
    r'^Article\s+(\d+)',        # English
]

# Paragraph patterns
PARAGRAPH_PATTERNS = [
    r'^\((\d+)\)',              # (1), (2), etc.
    r'^(\d+)\)',                # 1), 2), etc.
]
```

### 5. Error Handling
All pipeline steps must handle errors gracefully:

```python
def run(self, context):
    try:
        # Step logic
        pass
    except Exception as e:
        context.log("ERROR", f"Step failed: {str(e)}", self.step_name)
        # Create empty artifact to allow pipeline to continue
        context.add_artifact(
            self.artifact(
                name=self.produces[0],
                artifact_type=self.produces[0],
                payload={}
            )
        )
    return context
```

## File Structure

```
ZAIKON/
├── backend/
│   └── zaikon/
│       ├── main.py                    # FastAPI app entry point
│       ├── core/
│       │   ├── config.py              # Settings and configuration
│       │   ├── schemas.py             # Pydantic models
│       │   └── time.py                # Time utilities
│       ├── api/
│       │   └── routers/
│       │       ├── corpus.py          # Corpus endpoints
│       │       ├── draft_reviews.py   # Draft review endpoints
│       │       ├── conflicts.py       # Conflict detection endpoints
│       │       └── ...
│       ├── modules/
│       │   ├── corpus/
│       │   │   ├── service.py         # Corpus business logic
│       │   │   └── store.py           # Corpus database operations
│       │   ├── draft_reviews/
│       │   │   ├── service.py         # Draft review logic
│       │   │   └── store.py           # Draft database operations
│       │   ├── conflicts/
│       │   │   └── service.py         # Conflict detection logic
│       │   ├── assertions/
│       │   │   ├── service.py         # Assertion extraction
│       │   │   └── store.py           # Assertion storage
│       │   ├── legal_parser/
│       │   │   └── service.py         # Legal document parsing
│       │   └── ontology/
│       │       └── service.py         # Ontology management
│       └── pipeline/
│           ├── base.py                # Pipeline base classes
│           ├── chains.py              # Pipeline chains
│           └── steps/
│               ├── corpus/
│               │   ├── file_by_file_import.py
│               │   └── folder_import.py
│               └── draft/
│                   └── review_steps.py
├── frontend/
│   ├── src/
│   │   ├── App.tsx                    # Main app component
│   │   ├── api.ts                     # API client
│   │   ├── types.ts                   # TypeScript types
│   │   └── components/
│   │       ├── CorpusManagement.tsx
│   │       ├── DraftReview.tsx
│   │       ├── ConflictFindings.tsx
│   │       └── ...
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── data/
│   ├── zaikon.db                      # SQLite database
│   └── qdrant_storage/                # Qdrant vector store
├── DOCUMENTS/                         # Test documents
├── scripts/                           # Utility scripts
├── requirements.txt
└── README.md
```

## Implementation Steps

### Phase 1: Core Infrastructure
1. Set up FastAPI backend with SQLite database
2. Implement pipeline architecture (base classes, context, artifacts)
3. Create database schema and stores
4. Implement configuration management

### Phase 2: Document Processing
1. Implement legal document parser (Latin/Cyrillic support)
2. Create canonical document model
3. Implement text extraction (TXT, PDF, DOCX)
4. Build document normalization

### Phase 3: Corpus Management
1. Implement corpus CRUD operations
2. Create file-by-file import pipeline
3. Implement assertion extraction service
4. Build indexing steps (keyword, vector, structure)
5. Implement assertion storage

### Phase 4: Draft Review
1. Implement draft parsing
2. Create draft assertion extraction
3. Build conflict detection algorithm
4. Implement finding storage
5. Create draft review pipeline

### Phase 5: Conflict Detection
1. Define 127 conflict types
2. Implement conflict rules
3. Create slot-based matching
4. Build candidate scoring
5. Implement severity calculation

### Phase 6: Frontend
1. Set up React + Vite project
2. Create API client
3. Build corpus management UI
4. Implement draft review interface
5. Create findings display

### Phase 7: Testing & Optimization
1. Create test corpus
2. Build test scripts
3. Implement performance monitoring
4. Optimize database queries
5. Add caching where appropriate

## Common Pitfalls to Avoid

### 1. Assertion Storage
❌ **WRONG**: Adding `StoreAssertionsStep` to main import chain
```python
FileByFileImportChain(steps=[
    ...,
    ProcessFilesWithProgressStep(),
    StoreAssertionsStep(),  # ← WRONG! No assertions artifact here
    ...
])
```

✅ **CORRECT**: `StoreAssertionsStep` is already in per-file chain
```python
# Inside ProcessFilesWithProgressStep._process_single_file()
steps = [
    ...,
    ExtractNormativeAssertionsStep(),
    StoreAssertionsStep(),  # ← CORRECT! Has assertions artifact
    ...
]
```

### 2. Database Paths
❌ **WRONG**: Hardcoded or relative paths
```python
db_path = "zaikon.db"  # Creates DB in current directory
```

✅ **CORRECT**: Use centralized settings
```python
from zaikon.core.config import settings
db_path = settings.database_path  # "data/zaikon.db"
```

### 3. Artifact Validation
❌ **WRONG**: Assuming artifacts exist
```python
def run(self, context):
    assertions = context.get_artifact("normative_assertions").payload
    # ← Crashes if artifact is None
```

✅ **CORRECT**: Always validate
```python
def run(self, context):
    artifact = context.get_artifact("normative_assertions")
    if not artifact:
        # Handle missing artifact
        return context
    assertions = artifact.payload
```

### 4. Error Handling
❌ **WRONG**: Letting exceptions crash pipeline
```python
def run(self, context):
    result = risky_operation()  # ← Crashes entire pipeline
    return context
```

✅ **CORRECT**: Catch and log errors
```python
def run(self, context):
    try:
        result = risky_operation()
    except Exception as e:
        context.log("ERROR", f"Failed: {e}", self.step_name)
        # Create empty artifact to continue
    return context
```

### 5. Unicode Handling
❌ **WRONG**: Assuming ASCII
```python
with open(file, "r") as f:  # ← Fails on Cyrillic
    text = f.read()
```

✅ **CORRECT**: Always specify UTF-8
```python
with open(file, "r", encoding="utf-8") as f:
    text = f.read()
```

## Testing Strategy

### Unit Tests
- Test each pipeline step independently
- Mock dependencies (database, LLM, etc.)
- Verify artifact production

### Integration Tests
- Test complete pipeline chains
- Use test database
- Verify end-to-end flow

### System Tests
- Import real legal documents
- Create draft reviews
- Verify conflict detection
- Check database consistency

## Performance Considerations

### Database
- Index frequently queried columns (corpus_id, document_id)
- Use prepared statements
- Batch insert operations
- Regular VACUUM operations

### Vector Search
- Configure Qdrant for optimal performance
- Use appropriate vector dimensions
- Implement result caching

### LLM Calls
- Cache repeated queries
- Batch similar requests
- Use streaming for long responses
- Implement timeout handling

## Deployment

### Development
```bash
# Backend
cd backend
python -m uvicorn zaikon.main:app --reload --port 8100

# Frontend
cd frontend
npm run dev
```

### Production
```bash
# Backend
cd backend
gunicorn zaikon.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
cd frontend
npm run build
# Serve dist/ with nginx or similar
```

## Configuration

### Environment Variables
```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# Database
DATABASE_PATH=data/zaikon.db

# Qdrant
QDRANT_PATH=data/qdrant_storage
QDRANT_COLLECTION=corpus_legal_units

# API
API_HOST=0.0.0.0
API_PORT=8100
```

## Monitoring & Logging

### Logging Levels
- **DEBUG**: Detailed pipeline step execution
- **INFO**: Normal operations (imports, reviews)
- **WARNING**: Recoverable issues (missing artifacts)
- **ERROR**: Failures requiring attention

### Metrics to Track
- Import success/failure rate
- Average processing time per document
- Conflict detection accuracy
- Database size growth
- API response times

## Support & Maintenance

### Regular Tasks
- Database backup (daily)
- Log rotation (weekly)
- Performance monitoring (continuous)
- Dependency updates (monthly)

### Troubleshooting
1. Check logs for errors
2. Verify database integrity
3. Test LLM connectivity
4. Validate document formats
5. Review pipeline artifacts

---

## Quick Start Example

```python
# 1. Create corpus
corpus = create_corpus(name="Radni odnosi", description="Labor law corpus")

# 2. Import documents
import_folder(
    corpus_id=corpus.corpus_id,
    folder_uri="file:///path/to/documents",
    file_pattern="*.txt"
)

# 3. Create draft review
draft = create_draft_review(
    title="Pravilnik o radu",
    content_text=draft_text,
    selected_corpus_id=corpus.corpus_id
)

# 4. Run conflict detection
run_draft_pipeline(draft_id=draft.pipeline_run_id)

# 5. Get findings
findings = get_findings(draft_id=draft.pipeline_run_id)
```

---

This prompt provides complete specifications for regenerating the ZAIKON system from scratch. Follow the implementation phases in order, paying special attention to the critical implementation details and common pitfalls sections.