# ZAIKON - Complete API Specification

## Base URL
```
http://localhost:8100/api/v1
```

## Authentication
Currently no authentication required (development mode).
For production, implement JWT-based authentication.

---

## Corpus Management

### Create Corpus
**Endpoint**: `POST /corpora`

**Request Body**:
```json
{
  "name": "Radni odnosi",
  "description": "Corpus of labor law documents"
}
```

**Response** (200 OK):
```json
{
  "corpus_id": "uuid",
  "name": "Radni odnosi",
  "description": "Corpus of labor law documents",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "metadata": {}
}
```

### List Corpora
**Endpoint**: `GET /corpora`

**Response** (200 OK):
```json
{
  "corpora": [
    {
      "corpus_id": "uuid",
      "name": "Radni odnosi",
      "description": "Corpus of labor law documents",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z",
      "document_count": 15,
      "assertion_count": 342
    }
  ]
}
```

### Get Corpus Details
**Endpoint**: `GET /corpora/{corpus_id}`

**Response** (200 OK):
```json
{
  "corpus_id": "uuid",
  "name": "Radni odnosi",
  "description": "Corpus of labor law documents",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "metadata": {},
  "statistics": {
    "document_count": 15,
    "assertion_count": 342,
    "total_size_bytes": 1048576
  }
}
```

### Import Documents to Corpus
**Endpoint**: `POST /corpora/{corpus_id}/import-folder`

**Request Body**:
```json
{
  "corpus_id": "uuid",
  "folder_uri": "file:///path/to/documents",
  "folder_path": "/path/to/documents",
  "file_pattern": "*.txt"
}
```

**Response** (200 OK):
```json
{
  "import_job": {
    "import_job_id": "uuid",
    "corpus_id": "uuid",
    "status": "completed",
    "started_at": "2024-01-01T12:00:00Z",
    "completed_at": "2024-01-01T12:05:00Z"
  },
  "report": {
    "source_files": [
      {
        "source_uri": "file:///path/to/doc1.txt",
        "filename": "doc1.txt",
        "import_status": "completed",
        "document_id": "uuid",
        "assertions_count": 23
      }
    ],
    "summary": {
      "total_files": 5,
      "successful": 5,
      "failed": 0,
      "total_documents": 5,
      "total_assertions": 115
    }
  }
}
```

### List Corpus Documents
**Endpoint**: `GET /corpora/{corpus_id}/documents`

**Query Parameters**:
- `limit` (optional): Number of documents to return (default: 50)
- `offset` (optional): Offset for pagination (default: 0)

**Response** (200 OK):
```json
{
  "documents": [
    {
      "document_id": "uuid",
      "corpus_id": "uuid",
      "source_uri": "file:///path/to/doc.txt",
      "filename": "zakon_o_radu.txt",
      "title": "Zakon o radu",
      "document_type": "zakon",
      "created_at": "2024-01-01T12:00:00Z",
      "assertion_count": 23
    }
  ],
  "total": 15,
  "limit": 50,
  "offset": 0
}
```

### List Corpus Assertions
**Endpoint**: `GET /corpora/{corpus_id}/assertions`

**Query Parameters**:
- `document_id` (optional): Filter by document
- `limit` (optional): Number of assertions to return (default: 100)
- `offset` (optional): Offset for pagination (default: 0)

**Response** (200 OK):
```json
{
  "assertions": [
    {
      "assertion_id": "uuid",
      "document_id": "uuid",
      "section_id": "uuid",
      "text": "Poslodavac je dužan da...",
      "action": "obaveza",
      "object": "poslodavac",
      "domain": "radni_odnosi",
      "modality": "must",
      "conditions": [],
      "exceptions": []
    }
  ],
  "total": 342,
  "limit": 100,
  "offset": 0
}
```

---

## Draft Review Management

### Create Draft Review
**Endpoint**: `POST /draft-reviews`

**Request Body**:
```json
{
  "title": "Pravilnik o radu - Draft",
  "content_text": "Član 1\nPoslodavac je dužan...",
  "selected_corpus_id": "uuid"
}
```

**Response** (200 OK):
```json
{
  "draft_review": {
    "pipeline_run_id": "uuid",
    "title": "Pravilnik o radu - Draft",
    "selected_corpus_id": "uuid",
    "status": "created",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

### Start Draft Review Pipeline
**Endpoint**: `POST /draft-reviews/{draft_id}/run`

**Response** (200 OK):
```json
{
  "pipeline_run_id": "uuid",
  "status": "running",
  "started_at": "2024-01-01T12:00:00Z"
}
```

### Get Draft Review Status
**Endpoint**: `GET /draft-reviews/{draft_id}`

**Response** (200 OK):
```json
{
  "pipeline_run_id": "uuid",
  "title": "Pravilnik o radu - Draft",
  "selected_corpus_id": "uuid",
  "status": "completed",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:05:00Z",
  "statistics": {
    "total_assertions": 15,
    "total_findings": 8,
    "critical_findings": 1,
    "high_findings": 3,
    "medium_findings": 3,
    "low_findings": 1
  }
}
```

### List Draft Reviews
**Endpoint**: `GET /draft-reviews`

**Query Parameters**:
- `corpus_id` (optional): Filter by corpus
- `status` (optional): Filter by status
- `limit` (optional): Number of drafts to return (default: 50)
- `offset` (optional): Offset for pagination (default: 0)

**Response** (200 OK):
```json
{
  "draft_reviews": [
    {
      "pipeline_run_id": "uuid",
      "title": "Pravilnik o radu - Draft",
      "selected_corpus_id": "uuid",
      "status": "completed",
      "created_at": "2024-01-01T12:00:00Z",
      "finding_count": 8
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

### Get Draft Findings
**Endpoint**: `GET /draft-reviews/{draft_id}/findings`

**Query Parameters**:
- `category` (optional): Filter by conflict category
- `severity` (optional): Filter by severity
- `limit` (optional): Number of findings to return (default: 100)
- `offset` (optional): Offset for pagination (default: 0)

**Response** (200 OK):
```json
{
  "findings": [
    {
      "finding_id": "uuid",
      "draft_id": "uuid",
      "conflict_type": "contradictory_obligation",
      "category": "normative_conflicts",
      "severity": "high",
      "draft_assertion": {
        "assertion_id": "uuid",
        "text": "Poslodavac je dužan da isplati naknadu u roku od 15 dana",
        "action": "obaveza",
        "object": "poslodavac",
        "domain": "radni_odnosi"
      },
      "corpus_assertion": {
        "assertion_id": "uuid",
        "document_id": "uuid",
        "text": "Poslodavac je dužan da isplati naknadu u roku od 30 dana",
        "action": "obaveza",
        "object": "poslodavac",
        "domain": "radni_odnosi"
      },
      "explanation": "Draft requires payment within 15 days, but corpus requires 30 days",
      "recommendation": "Align payment deadline with existing regulation or provide justification",
      "created_at": "2024-01-01T12:05:00Z"
    }
  ],
  "total": 8,
  "limit": 100,
  "offset": 0,
  "summary": {
    "by_category": {
      "normative_conflicts": 3,
      "temporal_conflicts": 2,
      "procedural_conflicts": 2,
      "hierarchical_conflicts": 1
    },
    "by_severity": {
      "critical": 1,
      "high": 3,
      "medium": 3,
      "low": 1
    }
  }
}
```

### Get Draft Artifacts
**Endpoint**: `GET /draft-reviews/{draft_id}/artifacts`

**Response** (200 OK):
```json
{
  "artifacts": [
    {
      "artifact_name": "parsed_draft",
      "artifact_type": "parsed_draft",
      "created_at": "2024-01-01T12:00:00Z"
    },
    {
      "artifact_name": "draft_assertions",
      "artifact_type": "draft_assertions",
      "created_at": "2024-01-01T12:01:00Z"
    },
    {
      "artifact_name": "conflict_findings",
      "artifact_type": "conflict_findings",
      "created_at": "2024-01-01T12:05:00Z"
    }
  ]
}
```

### Get Specific Artifact
**Endpoint**: `GET /draft-reviews/{draft_id}/artifacts/{artifact_name}`

**Response** (200 OK):
```json
{
  "artifact_name": "draft_assertions",
  "artifact_type": "draft_assertions",
  "payload": {
    "assertions": [
      {
        "assertion_id": "uuid",
        "text": "Poslodavac je dužan...",
        "action": "obaveza",
        "object": "poslodavac"
      }
    ]
  },
  "created_at": "2024-01-01T12:01:00Z"
}
```

---

## Configuration Management

### Get LLM Settings
**Endpoint**: `GET /llm/settings`

**Response** (200 OK):
```json
{
  "base_url": "http://localhost:11434",
  "model": "llama3.2:latest",
  "temperature": 0.7,
  "max_tokens": 2000,
  "timeout": 60
}
```

### Update LLM Settings
**Endpoint**: `PUT /llm/settings`

**Request Body**:
```json
{
  "base_url": "http://localhost:11434",
  "model": "llama3.2:latest",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Response** (200 OK):
```json
{
  "base_url": "http://localhost:11434",
  "model": "llama3.2:latest",
  "temperature": 0.7,
  "max_tokens": 2000,
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Get Ontology Settings
**Endpoint**: `GET /ontology/settings`

**Response** (200 OK):
```json
{
  "active_ontology": "labor_law_minimal",
  "language": "sr",
  "actions": ["obaveza", "zabrana", "dozvola"],
  "domains": ["radni_odnosi", "socijalno_osiguranje"],
  "modalities": ["must", "may", "must_not"]
}
```

### Update Ontology Settings
**Endpoint**: `PUT /ontology/settings`

**Request Body**:
```json
{
  "active_ontology": "labor_law_minimal",
  "language": "sr"
}
```

**Response** (200 OK):
```json
{
  "active_ontology": "labor_law_minimal",
  "language": "sr",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Get Conflict Rules
**Endpoint**: `GET /conflicts/rules`

**Query Parameters**:
- `category` (optional): Filter by category
- `active_only` (optional): Return only active rules (default: false)

**Response** (200 OK):
```json
{
  "rules": [
    {
      "rule_id": "contradictory_obligation",
      "category": "normative_conflicts",
      "name": "Contradictory Obligation",
      "description": "Draft imposes obligation that contradicts existing obligation",
      "severity": "high",
      "active": true,
      "detection_logic": {
        "draft_action": "obaveza",
        "corpus_action": "obaveza",
        "same_object": true,
        "different_modality": true
      }
    }
  ],
  "total": 127
}
```

### Update Conflict Rule
**Endpoint**: `PUT /conflicts/rules/{rule_id}`

**Request Body**:
```json
{
  "active": false,
  "severity": "medium"
}
```

**Response** (200 OK):
```json
{
  "rule_id": "contradictory_obligation",
  "active": false,
  "severity": "medium",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

---

## Search & Query

### Search Documents
**Endpoint**: `POST /search/documents`

**Request Body**:
```json
{
  "query": "radni odnos",
  "corpus_id": "uuid",
  "limit": 10,
  "search_type": "hybrid"
}
```

**Response** (200 OK):
```json
{
  "results": [
    {
      "document_id": "uuid",
      "title": "Zakon o radu",
      "filename": "zakon_o_radu.txt",
      "score": 0.95,
      "highlights": [
        "...radni odnos se zasniva..."
      ]
    }
  ],
  "total": 5,
  "query_time_ms": 45
}
```

### Search Assertions
**Endpoint**: `POST /search/assertions`

**Request Body**:
```json
{
  "query": "obaveza poslodavca",
  "corpus_id": "uuid",
  "filters": {
    "action": "obaveza",
    "domain": "radni_odnosi"
  },
  "limit": 20
}
```

**Response** (200 OK):
```json
{
  "results": [
    {
      "assertion_id": "uuid",
      "document_id": "uuid",
      "text": "Poslodavac je dužan da...",
      "action": "obaveza",
      "object": "poslodavac",
      "domain": "radni_odnosi",
      "score": 0.92
    }
  ],
  "total": 15,
  "query_time_ms": 32
}
```

---

## Health & Status

### Health Check
**Endpoint**: `GET /health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "services": {
    "database": "healthy",
    "qdrant": "healthy",
    "llm": "healthy"
  }
}
```

### System Status
**Endpoint**: `GET /status`

**Response** (200 OK):
```json
{
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "statistics": {
    "total_corpora": 5,
    "total_documents": 75,
    "total_assertions": 1523,
    "total_draft_reviews": 25,
    "total_findings": 187
  },
  "database": {
    "size_mb": 45.2,
    "connection_pool": {
      "active": 2,
      "idle": 8,
      "max": 10
    }
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request body: missing required field 'name'"
}
```

### 404 Not Found
```json
{
  "detail": "Corpus not found: uuid"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: database connection failed"
}
```

---

## Rate Limiting
- Default: 100 requests per minute per IP
- Burst: 20 requests
- Headers:
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)

---

## Pagination
All list endpoints support pagination:
- `limit`: Number of items per page (default: 50, max: 1000)
- `offset`: Number of items to skip (default: 0)

Response includes:
```json
{
  "items": [...],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

---

## Filtering
Many endpoints support filtering via query parameters:
- `corpus_id`: Filter by corpus
- `document_id`: Filter by document
- `status`: Filter by status
- `category`: Filter by category
- `severity`: Filter by severity
- `created_after`: Filter by creation date (ISO 8601)
- `created_before`: Filter by creation date (ISO 8601)

---

## Sorting
List endpoints support sorting:
- `sort_by`: Field to sort by (e.g., "created_at", "name")
- `sort_order`: "asc" or "desc" (default: "desc")

Example:
```
GET /draft-reviews?sort_by=created_at&sort_order=desc
```

---

## WebSocket Support (Future)
For real-time updates during long-running operations:

```javascript
const ws = new WebSocket('ws://localhost:8100/ws/import/{import_job_id}');

ws.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  console.log(`Progress: ${progress.percentage}%`);
};
```

---

This API specification provides complete endpoint definitions for the ZAIKON system.