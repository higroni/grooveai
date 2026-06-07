# GROOVE.AI - Modular Microservice Architecture

**Verzija**: 3.0 (Revised)
**Datum**: 2026-06-07
**Pristup**: Nezavisni Moduli + Optimizovana Arhitektura

---

## 📋 Arhitekturni Princip

Svaki modul je **potpuno nezavisan** sa:
- ✅ **Jasnim ulazom/izlazom** (API endpoints)
- ✅ **Sopstvenom bazom podataka** (jedna ili više tabela)
- ✅ **CRUD operacijama** nad svojim podacima
- ✅ **Sopstvenim logerom** i metrikama
- ✅ **Mogućnošću samostalnog pozivanja** ili od strane orkestratora
- ✅ **Jednom funkcijom** (Single Responsibility Principle)

---

## 🏗️ Arhitekturni Dijagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CENTRALNI ORCHESTRATOR                        │
│  - Koordinira module                                             │
│  - Prati progres                                                 │
│  - Upravlja workflow-ima                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   MODULE 1   │      │   MODULE 2   │      │   MODULE 3   │
│              │      │              │      │              │
│ - API        │      │ - API        │      │ - API        │
│ - DB Tables  │      │ - DB Tables  │      │ - DB Tables  │
│ - Logger     │      │ - Logger     │      │ - Logger     │
│ - Metrics    │      │ - Metrics    │      │ - Metrics    │
└──────────────┘      └──────────────┘      └──────────────┘
```

---

## 📦 Spisak Svih Modula (Optimizovana Arhitektura)

### FAZA 1: Document Ingestion (4 modula) - Port 8101-8104
1. **File Reader** (M1, Port 8101) - Čitanje PDF/DOCX/TXT → Raw text
2. **Text Normalizer** (M2, Port 8102) - Normalizacija teksta → Clean text
3. **Latinizer** (M3, Port 8103) - Ćirilica → Latinica
4. **Legal Parser** (M4, Port 8104) - Parsing strukture → Structured JSON (Akoma Ntoso)

### FAZA 2: Content Analysis (4 modula) - Port 8106-8109
6. **Assertion Extractor** (M6, Port 8106) - Ekstrakcija asercija → List of assertions
7. **Entity Recognizer** (M7, Port 8107) - Named entities → Entities dict
8. **Condition Extractor** (M8, Port 8108) - Uslovi/izuzeci → Conditions/exceptions
9. **Assertion Classifier** (M9, Port 8109) - Klasifikacija → Assertion type

### FAZA 3: Knowledge Enrichment (1 modul) - Port 8110
10. **Knowledge Enrichment** (M10, Port 8110) - Obogaćivanje znanjem → Enriched assertions
    - **Ontology Matcher** - Hibridna ontologija (DB + auto-learning) → Matched terms
    - **Reference Resolver** - Rezolucija pravnih referenci → Resolved refs
    - **Definition Extractor** - Ekstrakcija definicija → Term definitions

### FAZA 4: Vector Storage (1 modul) - Port 8111
11. **Vector Store** (M11, Port 8111) - Generisanje i skladištenje vektora
    - Embeddings generation (sentence-transformers)
    - Qdrant storage (production)
    - SQLite audit trail

### FAZA 5: Search & Retrieval (1 modul) - Port 8112
12. **Search Service** (M12, Port 8112) - Hibridna pretraga
    - Vector search (Qdrant)
    - Keyword search (BM25)
    - Hybrid ranking

### FAZA 6: Conflict Detection (4 modula) - Port 8117-8120 (Planirano)
17. **Candidate Finder** (M17) - Find candidates → Scored candidates
18. **Conflict Detector** (M18) - Detect conflicts → Conflict findings
19. **Severity Calculator** (M19) - Calculate severity → Severity score
20. **Recommendation Generator** (M20) - Generate recommendations → Recommendations

---

## 🔌 Detaljne API Specifikacije

### MODULE 1: File Reader

**Base URL**: `http://localhost:8101`

**Endpoint**: `POST /api/read`

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
    "text": "Zakon o radu\nČlan 1\n...",
    "encoding": "utf-8",
    "char_count": 15234,
    "page_count": 45
  },
  "metadata": {
    "processing_time_ms": 234,
    "file_size_bytes": 524288
  }
}
```

**Database Tables**:
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
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

**CRUD Endpoints**:
- `GET /api/jobs/{job_id}` - Get job details
- `GET /api/jobs` - List all jobs
- `DELETE /api/jobs/{job_id}` - Delete job

---

### MODULE 2: Text Normalizer

**Base URL**: `http://localhost:8102`

**Endpoint**: `POST /api/normalize`

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

**Database Tables**:
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

---

### MODULE 3: Latinizer

**Base URL**: `http://localhost:8103`

**Endpoint**: `POST /api/convert`

**Request**:
```json
{
  "text": "Закон о раду\nЧлан 1",
  "source_script": "cyrillic",
  "target_script": "latin"
}
```

**Response**:
```json
{
  "module": "latinizer",
  "status": "success",
  "job_id": "uuid-job3",
  "output": {
    "converted_text": "Zakon o radu\nČlan 1",
    "detected_script": "cyrillic",
    "conversion_confidence": 1.0
  },
  "metadata": {
    "processing_time_ms": 8
  }
}
```

**Database Tables**:
```sql
CREATE TABLE latinizer_jobs (
    job_id TEXT PRIMARY KEY,
    input_text TEXT NOT NULL,
    output_text TEXT NOT NULL,
    source_script TEXT,
    target_script TEXT,
    conversion_confidence REAL,
    processing_time_ms INTEGER,
    created_at TIMESTAMP
);
```

---

### MODULE 4: Legal Parser

**Base URL**: `http://localhost:8104`

**Endpoint**: `POST /api/parse`

**Request**:
```json
{
  "text": "Zakon o radu\nČlan 1\nOvim zakonom...\n(1) Poslodavac je dužan...",
  "language": "sr",
  "document_type": "zakon"
}
```

**Response**:
```json
{
  "module": "legal-parser",
  "status": "success",
  "job_id": "uuid-job4",
  "output": {
    "document": {
      "title": "Zakon o radu",
      "document_type": "zakon",
      "sections": [
        {
          "section_type": "clan",
          "number": 1,
          "title": "Član 1",
          "content": "Ovim zakonom...",
          "subsections": [...]
        }
      ]
    },
    "stats": {
      "total_sections": 1,
      "total_articles": 1,
      "total_paragraphs": 1
    }
  },
  "metadata": {
    "processing_time_ms": 45
  }
}
```

**Database Tables**:
```sql
CREATE TABLE legal_parser_jobs (
    job_id TEXT PRIMARY KEY,
    input_text TEXT NOT NULL,
    output_json TEXT NOT NULL,
    language TEXT,
    document_type TEXT,
    total_sections INTEGER,
    processing_time_ms INTEGER,
    created_at TIMESTAMP
);
```

---

### MODULE 5: Legal Unit Extractor

**Base URL**: `http://localhost:8105`

**Endpoint**: `POST /api/extract`

**Request**:
```json
{
  "document": {
    "title": "Zakon o radu",
    "sections": [...]
  },
  "extract_hierarchy": true
}
```

**Response**:
```json
{
  "module": "legal-unit-extractor",
  "status": "success",
  "job_id": "uuid-job5",
  "output": {
    "legal_units": [
      {
        "unit_id": "uuid-u1",
        "unit_type": "clan",
        "number": 1,
        "title": "Član 1",
        "content": "Ovim zakonom...",
        "parent_id": null
      }
    ],
    "stats": {
      "total_units": 2,
      "by_type": {"clan": 1, "stav": 1}
    }
  },
  "metadata": {
    "processing_time_ms": 23
  }
}
```

**Database Tables**:
```sql
CREATE TABLE legal_unit_extractor_jobs (
    job_id TEXT PRIMARY KEY,
    document_json TEXT NOT NULL,
    output_units TEXT NOT NULL,
    total_units INTEGER,
    processing_time_ms INTEGER,
    created_at TIMESTAMP
);

CREATE TABLE extracted_legal_units (
    unit_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    unit_type TEXT NOT NULL,
    number INTEGER,
    title TEXT,
    content TEXT NOT NULL,
    parent_id TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES legal_unit_extractor_jobs(job_id)
);
```

---

### MODULE 6: Assertion Extractor

**Base URL**: `http://localhost:8106`

**Endpoint**: `POST /api/extract`

**Request**:
```json
{
  "legal_unit": {
    "unit_id": "uuid-u1",
    "content": "Poslodavac je dužan da zaposlenom isplati zaradu."
  },
  "language": "sr"
}
```

**Response**:
```json
{
  "module": "assertion-extractor",
  "status": "success",
  "job_id": "uuid-job6",
  "output": {
    "assertions": [
      {
        "assertion_id": "uuid-a1",
        "text": "Poslodavac je dužan da zaposlenom isplati zaradu",
        "confidence": 0.95
      }
    ],
    "stats": {
      "total_assertions": 1
    }
  },
  "metadata": {
    "processing_time_ms": 67
  }
}
```

**Database Tables**:
```sql
CREATE TABLE assertion_extractor_jobs (
    job_id TEXT PRIMARY KEY,
    legal_unit_id TEXT NOT NULL,
    input_content TEXT NOT NULL,
    output_assertions TEXT NOT NULL,
    total_assertions INTEGER,
    processing_time_ms INTEGER,
    created_at TIMESTAMP
);

CREATE TABLE extracted_assertions (
    assertion_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    text TEXT NOT NULL,
    confidence REAL,
    created_at TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES assertion_extractor_jobs(job_id)
);
```

---

### MODULE 7: Entity Recognizer (NER)

**Base URL**: `http://localhost:8107`

**Endpoint**: `POST /api/recognize`

**Request**:
```json
{
  "text": "Poslodavac je dužan da zaposlenom isplati zaradu",
  "language": "sr",
  "model": "stanza"
}
```

**Response**:
```json
{
  "module": "entity-recognizer",
  "status": "success",
  "job_id": "uuid-job7",
  "output": {
    "entities": {
      "action": "isplata",
      "object": "zarada",
      "subject": "poslodavac",
      "recipient": "zaposleni",
      "modality": "must"
    },
    "raw_entities": [
      {"text": "Poslodavac", "type": "PERSON", "start": 0, "end": 10}
    ]
  },
  "metadata": {
    "processing_time_ms": 123,
    "model_used": "stanza-sr"
  }
}
```

**Database Tables**:
```sql
CREATE TABLE entity_recognizer_jobs (
    job_id TEXT PRIMARY KEY,
    input_text TEXT NOT NULL,
    language TEXT,
    model TEXT,
    output_entities TEXT NOT NULL,
    processing_time_ms INTEGER,
    created_at TIMESTAMP
);
```

---

### MODULE 10: Embedding Generator

**Base URL**: `http://localhost:8110`

**Endpoint**: `POST /api/generate`

**Request**:
```json
{
  "text": "Poslodavac je dužan da isplati zaradu",
  "model": "BAAI/bge-m3"
}
```

**Batch Endpoint**: `POST /api/generate-batch`

**Request**:
```json
{
  "texts": [
    "Poslodavac je dužan...",
    "Zaposleni ima pravo..."
  ],
  "model": "BAAI/bge-m3",
  "batch_size": 32
}
```

**Response**:
```json
{
  "module": "embedding-generator",
  "status": "success",
  "job_id": "uuid-job10",
  "output": {
    "vectors": [
      [0.123, -0.456, ...],
      [0.234, -0.567, ...]
    ],
    "model": "BAAI/bge-m3",
    "dimensions": 1024
  },
  "metadata": {
    "processing_time_ms": 156,
    "batch_size": 2,
    "device": "cuda"
  }
}
```

**Database Tables**:
```sql
CREATE TABLE embedding_generator_jobs (
    job_id TEXT PRIMARY KEY,
    input_texts TEXT NOT NULL,
    model TEXT NOT NULL,
    vectors TEXT NOT NULL,
    dimensions INTEGER,
    processing_time_ms INTEGER,
    device TEXT,
    created_at TIMESTAMP
);
```

---

### MODULE 13: Hybrid Search

**Base URL**: `http://localhost:8113`

**Endpoint**: `POST /api/search`

**Request**:
```json
{
  "query": "poslodavac zarada",
  "weights": {
    "vector": 0.45,
    "keyword": 0.35,
    "graph": 0.20
  },
  "limit": 10,
  "corpus_id": "uuid-c1"
}
```

**Response**:
```json
{
  "module": "hybrid-search",
  "status": "success",
  "job_id": "uuid-job13",
  "output": {
    "results": [
      {
        "assertion_id": "uuid-a1",
        "text": "Poslodavac je dužan da isplati zaradu",
        "score": 0.87,
        "score_breakdown": {
          "vector_score": 0.95,
          "keyword_score": 0.82,
          "graph_score": 0.75
        }
      }
    ],
    "total_found": 1
  },
  "metadata": {
    "processing_time_ms": 142
  }
}
```

**Database Tables**:
```sql
CREATE TABLE hybrid_search_jobs (
    job_id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    weights TEXT NOT NULL,
    corpus_id TEXT,
    results TEXT NOT NULL,
    total_found INTEGER,
    processing_time_ms INTEGER,
    created_at TIMESTAMP
);
```

---

### MODULE 17: Candidate Finder

**Base URL**: `http://localhost:8117`

**Endpoint**: `POST /api/find`

**Request**:
```json
{
  "draft_assertion": {
    "assertion_id": "uuid-da1",
    "text": "Poslodavac mora da isplati zaradu u roku od 7 dana",
    "entities": {
      "action": "isplata",
      "object": "zarada"
    }
  },
  "corpus_id": "uuid-c1",
  "min_similarity": 0.25,
  "limit": 50
}
```

**Response**:
```json
{
  "module": "candidate-finder",
  "status": "success",
  "job_id": "uuid-job17",
  "output": {
    "candidates": [
      {
        "corpus_assertion_id": "uuid-ca1",
        "text": "Poslodavac je dužan da isplati zaradu",
        "similarity_score": 0.87,
        "match_type": "action_object_match"
      }
    ],
    "total_candidates": 2
  },
  "metadata": {
    "processing_time_ms": 234
  }
}
```

**Database Tables**:
```sql
CREATE TABLE candidate_finder_jobs (
    job_id TEXT PRIMARY KEY,
    draft_assertion_id TEXT NOT NULL,
    corpus_id TEXT NOT NULL,
    min_similarity REAL,
    candidates TEXT NOT NULL,
    total_candidates INTEGER,
    processing_time_ms INTEGER,
    created_at TIMESTAMP
);
```

---

### MODULE 18: Conflict Detector

**Base URL**: `http://localhost:8118`

**Endpoint**: `POST /api/detect`

**Request**:
```json
{
  "draft_assertion": {
    "assertion_id": "uuid-da1",
    "text": "Poslodavac mora da isplati zaradu u roku od 7 dana",
    "entities": {
      "action": "isplata",
      "object": "zarada",
      "deadline": "7 dana"
    }
  },
  "corpus_assertion": {
    "assertion_id": "uuid-ca1",
    "text": "Poslodavac je dužan da isplati zaradu u roku od 30 dana",
    "entities": {
      "action": "isplata",
      "object": "zarada",
      "deadline": "30 dana"
    }
  },
  "conflict_rule_set_id": "uuid-crs1"
}
```

**Response**:
```json
{
  "module": "conflict-detector",
  "status": "success",
  "job_id": "uuid-job18",
  "output": {
    "conflicts": [
      {
        "conflict_id": "uuid-cf1",
        "conflict_type": "deadline_conflict",
        "category": "temporal_conflicts",
        "rule_id": "uuid-r15",
        "explanation": "Draft specifies 7 days, corpus specifies 30 days",
        "confidence": 0.95
      }
    ],
    "total_conflicts": 1
  },
  "metadata": {
    "processing_time_ms": 78,
    "rules_checked": 127
  }
}
```

**Database Tables**:
```sql
CREATE TABLE conflict_detector_jobs (
    job_id TEXT PRIMARY KEY,
    draft_assertion_id TEXT NOT NULL,
    corpus_assertion_id TEXT NOT NULL,
    conflict_rule_set_id TEXT NOT NULL,
    conflicts TEXT NOT NULL,
    total_conflicts INTEGER,
    processing_time_ms INTEGER,
    created_at TIMESTAMP
);

CREATE TABLE detected_conflicts (
    conflict_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    conflict_type TEXT NOT NULL,
    category TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    explanation TEXT,
    confidence REAL,
    created_at TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES conflict_detector_jobs(job_id)
);
```

---

## 🎯 Centralni Orchestrator

**Base URL**: `http://localhost:8100`

**Funkcija**: Koordinira module, prati progres, upravlja workflow-ima

### Workflow 1: Import Corpus

**Endpoint**: `POST /api/orchestrator/workflows/import-corpus`

**Request**:
```json
{
  "workflow_name": "import-corpus",
  "corpus_id": "uuid-c1",
  "file_paths": [
    "/path/to/doc1.pdf",
    "/path/to/doc2.docx"
  ],
  "options": {
    "generate_embeddings": true,
    "build_indexes": true,
    "ontology_set_id": "uuid-ont1"
  }
}
```

**Response**:
```json
{
  "workflow_id": "uuid-wf1",
  "status": "running",
  "progress": {
    "current_step": "file-reader",
    "completed_steps": 0,
    "total_steps": 15,
    "percentage": 0
  },
  "websocket_url": "ws://localhost:8100/ws/workflows/uuid-wf1"
}
```

**Workflow Steps**:
```
1. File Reader (8101) → Text
2. Text Normalizer (8102) → Normalized Text
3. Latinizer (8103) → Latin Text
4. Legal Parser (8104) → Structured Document
5. Legal Unit Extractor (8105) → Legal Units
6. For each Legal Unit:
   a. Assertion Extractor (8106) → Assertions
   b. Entity Recognizer (8107) → Entities
   c. Condition Extractor (8108) → Conditions
   d. Assertion Classifier (8109) → Classified Assertions
7. Embedding Generator (8110) - Batch → Vectors
8. Vector Store (8111) → Stored
9. Keyword Indexer (8112) → Indexed
10. Ontology Matcher (8114) → Matched Terms
11. Reference Resolver (8115) → Resolved References
12. Definition Extractor (8116) → Definitions
```

---

### Workflow 2: Analyze Draft

**Endpoint**: `POST /api/orchestrator/workflows/analyze-draft`

**Request**:
```json
{
  "workflow_name": "analyze-draft",
  "draft_text": "Zakon o izmeni zakona o radu\nČlan 1\n...",
  "corpus_id": "uuid-c1",
  "conflict_rule_set_id": "uuid-crs1",
  "options": {
    "generate_recommendations": true,
    "use_llm": true
  }
}
```

**Response**:
```json
{
  "workflow_id": "uuid-wf2",
  "status": "running",
  "progress": {
    "current_step": "legal-parser",
    "completed_steps": 0,
    "total_steps": 10,
    "percentage": 0
  },
  "websocket_url": "ws://localhost:8100/ws/workflows/uuid-wf2"
}
```

**Workflow Steps**:
```
1. Text Normalizer (8102) → Normalized Text
2. Latinizer (8103) → Latin Text
3. Legal Parser (8104) → Structured Document
4. Legal Unit Extractor (8105) → Legal Units
5. For each Legal Unit:
   a. Assertion Extractor (8106) → Assertions
   b. Entity Recognizer (8107) → Entities
   c. Condition Extractor (8108) → Conditions
   d. Assertion Classifier (8109) → Classified Assertions
6. For each Draft Assertion:
   a. Candidate Finder (8117) → Candidates
   b. For each Candidate:
      i. Conflict Detector (8118) → Conflicts
      ii. Severity Calculator (8119) → Severity
      iii. Recommendation Generator (8120) → Recommendations
```

---

### Workflow 3: Search Corpus

**Endpoint**: `POST /api/orchestrator/workflows/search-corpus`

**Request**:
```json
{
  "workflow_name": "search-corpus",
  "query": "poslodavac zarada",
  "corpus_id": "uuid-c1",
  "options": {
    "use_hybrid_search": true,
    "rerank": true,
    "limit": 10
  }
}
```

**Response**:
```json
{
  "workflow_id": "uuid-wf3",
  "status": "completed",
  "results": [
    {
      "assertion_id": "uuid-a1",
      "text": "Poslodavac je dužan da isplati zaradu",
      "score": 0.87,
      "document_id": "uuid-d1"
    }
  ],
  "metadata": {
    "processing_time_ms": 156,
    "total_found": 1
  }
}
```

**Workflow Steps**:
```
1. Hybrid Search (8113) → Results
2. (Optional) Reranker → Reranked Results
```

---

### Orchestrator Database Tables

```sql
CREATE TABLE workflows (
    workflow_id TEXT PRIMARY KEY,
    workflow_name TEXT NOT NULL,
    status TEXT NOT NULL,
    input_params TEXT NOT NULL,
    output_results TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

CREATE TABLE workflow_steps (
    step_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    module_name TEXT NOT NULL,
    module_port INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    status TEXT NOT NULL,
    input_data TEXT,
    output_data TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    processing_time_ms INTEGER,
    error_message TEXT,
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id)
);

CREATE TABLE workflow_progress (
    workflow_id TEXT PRIMARY KEY,
    current_step TEXT,
    completed_steps INTEGER,
    total_steps INTEGER,
    percentage REAL,
    updated_at TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id)
);
```

---

## 📁 Folder Struktura (Modularna)

```
ZAIKON/
├── orchestrator/                  # Port 8100
│   ├── main.py
│   ├── workflows/
│   │   ├── import_corpus.py
│   │   ├── analyze_draft.py
│   │   └── search_corpus.py
│   ├── api/
│   │   └── routers/
│   │       └── orchestrator_router.py
│   ├── database/
│   │   └── orchestrator_db.py
│   └── requirements.txt
│
├── modules/
│   ├── file_reader/               # Port 8101
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── text_normalizer/           # Port 8102
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── latinizer/                 # Port 8103
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── legal_parser/              # Port 8104
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── legal_unit_extractor/     # Port 8105
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── assertion_extractor/      # Port 8106
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── entity_recognizer/        # Port 8107
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── condition_extractor/      # Port 8108
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── assertion_classifier/     # Port 8109
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── embedding_generator/      # Port 8110
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── vector_store/             # Port 8111
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── keyword_indexer/          # Port 8112
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── hybrid_search/            # Port 8113
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── ontology_matcher/         # Port 8114
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── reference_resolver/       # Port 8115
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── definition_extractor/     # Port 8116
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── candidate_finder/         # Port 8117
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── conflict_detector/        # Port 8118
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   ├── severity_calculator/      # Port 8119
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── service.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── requirements.txt
│   │
│   └── recommendation_generator/ # Port 8120
│       ├── main.py
│       ├── api.py
│       ├── service.py
│       ├── database.py
│       ├── logger.py
│       ├── metrics.py
│       └── requirements.txt
│
├── shared/                        # Shared utilities
│   ├── database/
│   │   └── base.py
│   ├── logging/
│   │   └── logger.py
│   ├── metrics/
│   │   └── metrics.py
│   └── models/
│       └── common.py
│
├── data/                          # Data directory
│   ├── databases/                 # SQLite databases per module
│   │   ├── orchestrator.db
│   │   ├── file_reader.db
│   │   ├── text_normalizer.db
│   │   └── ...
│   ├── qdrant_storage/            # Qdrant vector store
│   └── logs/                      # Logs per module
│       ├── orchestrator.log
│       ├── file_reader.log
│       └── ...
│
├── frontend/                      # React frontend
│   └── src/
│
├── docker-compose.yml             # All modules + orchestrator
└── README.md
```

---

## 🚀 Deployment Strategy

### Development (Local)

**Start All Modules**:
```bash
# Terminal 1: Orchestrator
cd orchestrator
python main.py

# Terminal 2: File Reader
cd modules/file_reader
python main.py

# Terminal 3: Text Normalizer
cd modules/text_normalizer
python main.py

# ... (start all 20 modules)
```

### Production (Docker Compose)

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  orchestrator:
    build: ./orchestrator
    ports:
      - "8100:8100"
    environment:
      - DATABASE_PATH=/data/databases/orchestrator.db
    volumes:
      - ./data:/data
    depends_on:
      - file_reader
      - text_normalizer
      # ... all modules

  file_reader:
    build: ./modules/file_reader
    ports:
      - "8101:8101"
    environment:
      - DATABASE_PATH=/data/databases/file_reader.db
    volumes:
      - ./data:/data

  text_normalizer:
    build: ./modules/text_normalizer
    ports:
      - "8102:8102"
    environment:
      - DATABASE_PATH=/data/databases/text_normalizer.db
    volumes:
      - ./data:/data

  # ... (all 20 modules)

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - orchestrator
```

**Start All**:
```bash
docker-compose up -d
```

---

## 📊 Module Template

Svaki modul prati isti template:

**main.py**:
```python
from fastapi import FastAPI
from api import router
from database import init_database
from logger import setup_logger
from metrics import setup_metrics

app = FastAPI(title="Module Name")
logger = setup_logger("module-name")
metrics = setup_metrics("module-name")

# Initialize database
init_database()

# Include router
app.include_router(router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "healthy", "module": "module-name"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8101)
```

**api.py**:
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from service import ModuleService
from logger import get_logger

router = APIRouter()
logger = get_logger("module-name")
service = ModuleService()

class Request(BaseModel):
    # Request fields

class Response(BaseModel):
    # Response fields

@router.post("/endpoint", response_model=Response)
async def endpoint(request: Request):
    try:
        result = service.process(request)
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**service.py**:
```python
from logger import get_logger
from database import get_db_session
import time

logger = get_logger("module-name")

class ModuleService:
    def process(self, request):
        start_time = time.time()
        
        # Processing logic
        result = self._do_processing(request)
        
        # Save to database
        with get_db_session() as session:
            # Save job
            pass
        
        processing_time = int((time.time() - start_time) * 1000)
        logger.info(f"Processing completed in {processing_time}ms")
        
        return result
    
    def _do_processing(self, request):
        # Actual processing logic
        pass
```

**database.py**:
```python
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from datetime import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    job_id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    input_data = Column(Text)
    output_data = Column(Text)
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine("sqlite:///data/databases/module.db")
SessionLocal = sessionmaker(bind=engine)

def init_database():
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

**logger.py**:
```python
import logging
import sys

def setup_logger(module_name: str):
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(f"data/logs/{module_name}.log")
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(module_name: str):
    return logging.getLogger(module_name)
```

**metrics.py**:
```python
from prometheus_client import Counter, Histogram, Gauge
import time

class ModuleMetrics:
    def __init__(self, module_name: str):
        self.requests_total = Counter(
            f'{module_name}_requests_total',
            'Total requests'
        )
        self.processing_time = Histogram(
            f'{module_name}_processing_seconds',
            'Processing time'
        )
        self.active_jobs = Gauge(
            f'{module_name}_active_jobs',
            'Active jobs'
        )
    
    def record_request(self):
        self.requests_total.inc()
    
    def record_processing_time(self, seconds: float):
        self.processing_time.observe(seconds)
    
    def set_active_jobs(self, count: int):
        self.active_jobs.set(count)

def setup_metrics(module_name: str):
    return ModuleMetrics(module_name)
```

---

## ✅ Prednosti Modularne Arhitekture

1. **Nezavisnost** - Svaki modul radi samostalno
2. **Skalabilnost** - Lako dodavanje novih modula
3. **Održavanje** - Izmene u jednom modulu ne utiču na druge
4. **Testiranje** - Svaki modul se testira nezavisno
5. **Deployment** - Moduli se deploy-uju nezavisno
6. **Monitoring** - Svaki modul ima svoje metrike
7. **Debugging** - Lakše pronalaženje grešaka
8. **Reusability** - Moduli se mogu koristiti u drugim projektima

---

## 📝 Zaključak

Ova modularna arhitektura omogućava:
- ✅ **20 nezavisnih modula** sa jasnim API-jem
- ✅ **Centralni orchestrator** za koordinaciju
- ✅ **Sopstvene baze** za svaki modul
- ✅ **Logging i metrics** per modul
- ✅ **Skalabilnost** - Svaki modul može biti skaliran nezavisno
- ✅ **Maintainability** - Lakše održavanje i razvoj

---

## 🔄 Arhitekturne Izmene (V3.0 - Jun 2026)

### Razlozi za Reorganizaciju

**Problem sa prethodnom arhitekturom:**
- M10 (Embedding Generator) je skladištio vektore u SQLite umesto direktno u Qdrant
- Tri odvojena modula (M14, M15, M16) za knowledge enrichment bila su neefikasna
- Nedostajao je centralizovan search service

**Nova optimizovana arhitektura:**

#### 1. Konsolidacija Knowledge Enrichment (M10)
**Staro:**
- M14: Ontology Matcher
- M15: Reference Resolver  
- M16: Definition Extractor

**Novo:**
- **M10: Knowledge Enrichment** (Port 8110) - Jedinstveni modul sa tri funkcije:
  - Ontology Matcher (hibridna ontologija iz ZAIKON projekta)
  - Reference Resolver (rezolucija pravnih referenci)
  - Definition Extractor (ekstrakcija definicija)

**Prednosti:**
- Jedna baza podataka za sve knowledge enrichment operacije
- Efikasnija komunikacija između komponenti
- Lakše održavanje i razvoj
- Smanjenje network overhead-a

#### 2. Promena Uloge Vector Store (M10 → M11)
**Staro:**
- M10: Embedding Generator (generisao i skladištio u SQLite)

**Novo:**
- **M11: Vector Store** (Port 8111) - Fokus na Qdrant storage:
  - Generisanje embeddings (sentence-transformers)
  - **Qdrant storage** (production vector database)
  - SQLite samo za audit trail

**Prednosti:**
- Direktno skladištenje u Qdrant (brža pretraga)
- SQLite samo za audit i metadata
- Optimizovana arhitektura za vector search

#### 3. Novi Search Service (M12)
**Novo:**
- **M12: Search Service** (Port 8112) - Hibridna pretraga:
  - Vector similarity search (Qdrant)
  - Keyword search (BM25)
  - Hybrid ranking (kombinacija)
  - Filtriranje po metapodacima

**Prednosti:**
- Centralizovan search endpoint
- Hibridna pretraga (vector + keyword)
- Optimizovano za production use

### Hibridna Storage Strategija

```
┌─────────────────────────────────────────────────────────────┐
│                    HYBRID STORAGE                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SQLite (Audit Trail)          Qdrant (Production)          │
│  ├─ Processing history         ├─ Vector embeddings         │
│  ├─ Metadata                   ├─ Fast similarity search    │
│  ├─ Error logs                 ├─ Scalable storage          │
│  └─ Timestamps                 └─ Production queries        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### ZAIKON Lessons Learned - Implementirano

1. **Hibridna Ontologija** (M10)
   - Database-backed ontology (SQLite)
   - Auto-learning iz NER ekstrakcija
   - Confidence scoring i frequency tracking
   - Tri tabele: `ontology_terms`, `ontology_relationships`, `ontology_domains`

2. **Modularna Arhitektura**
   - Nezavisni servisi sa sopstvenim API-jem
   - Lakše testiranje i deployment
   - Mogućnost nezavisnog skaliranja

3. **Audit Trail**
   - SQLite za istoriju procesiranja
   - Qdrant za production vector search
   - Best of both worlds

### Novi Data Flow

```
M1 → M2 → M3 → M4 → M6 → M7 → M8 → M9 → M10 → M11 → M12
                                    ↓      ↓      ↓
                              Knowledge  Vector  Search
                              Enrichment  Store  Service
                              (Port 8110) (8111) (8112)
```

### Port Allocation (Ažurirano)

| Modul | Port | Status |
|-------|------|--------|
| M1: File Reader | 8101 | ✅ Implementiran |
| M2: Text Normalizer | 8102 | ✅ Implementiran |
| M3: Latinizer | 8103 | ✅ Implementiran |
| M4: Legal Parser | 8104 | ✅ Implementiran |
| M6: Assertion Extractor | 8106 | ✅ Implementiran |
| M7: Entity Recognizer | 8107 | ✅ Implementiran |
| M8: Condition Extractor | 8108 | ✅ Implementiran |
| M9: Assertion Classifier | 8109 | ✅ Implementiran |
| **M10: Knowledge Enrichment** | **8110** | 🔄 **U razvoju** |
| **M11: Vector Store** | **8111** | 🔄 **Renameovan** |
| **M12: Search Service** | **8112** | ⏳ **Planirano** |
| M17-M20: Conflict Detection | 8117-8120 | ⏳ Planirano |

### Sledeći Koraci

1. ✅ Rename `embedding_generator` → `vector_store` (M10 → M11)
2. ✅ Update `config.yaml` sa novom strukturom
3. ✅ Update `MODULAR_ARCHITECTURE.md`
4. 🔄 Implementacija M10: Knowledge Enrichment
   - Ontology Matcher (ZAIKON hybrid approach)
   - Reference Resolver
   - Definition Extractor
5. ⏳ Update M11: Vector Store za Qdrant integration
6. ⏳ Implementacija M12: Search Service
7. ⏳ End-to-end testiranje pipeline-a

---
- ✅ **Samostalno pozivanje** ili od strane orkestratora
- ✅ **Docker deployment** sa docker-compose
- ✅ **Lako skaliranje** i održavanje

**Status**: Spremno za implementaciju!
