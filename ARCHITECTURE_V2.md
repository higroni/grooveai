# ZAIKON V2 - Nova Arhitektura (Lessons Learned)

**Verzija**: 2.0  
**Datum**: 2026-06-06  
**Status**: Arhitekturni Plan za Reimplementaciju

---

## 📋 Izvršni Rezime

Ovaj dokument definiše novu arhitekturu ZAIKON sistema zasnovanu na:
- **Lessons Learned** iz prethodne implementacije (50+ sati uštede)
- **Domain-Driven Design (DDD)** principima
- **Production-Ready** verzionisanju i parametrizaciji (V3 model)
- **Modularnoj arhitekturi** sa jasnim granicama

---

## 🎯 Ključne Lekcije iz Prethodne Implementacije

### Kritične Greške koje NE SMEMO Ponoviti

#### 1. StoreAssertionsStep u Pogrešnom Lancu (4h izgubljeno)
**Problem**: Step za čuvanje asercija bio u glavnom lancu umesto u per-file lancu.
**Rešenje**: Uvek stavljati storage step-ove u per-file processing chain.

#### 2. JSON umesto SQLite (6h izgubljeno)
**Problem**: Korišćenje JSON fajlova za perzistenciju umesto SQLite.
**Rešenje**: SQLite za sve strukturirane podatke, JSON samo za artifacts.

#### 3. Nedostatak Cyrillic Podrške (2h izgubljeno)
**Problem**: Parser nije podržavao ćirilicu.
**Rešenje**: UTF-8 encoding svuda, regex pattern-i za latinicu I ćirilicu.

#### 4. Preveliki Batch Size (2h izgubljeno)
**Problem**: Batch size od 1000 za embeddings preopterećivao GPU.
**Rešenje**: Batch size 32-64 za embeddings, 100 za keyword indexing.

#### 5. Nedostatak Debug Output-a (10h izgubljeno)
**Problem**: Teško debugovanje bez detaljnih logova.
**Rešenje**: Opširan logging sa fazama, timing-om, validacijom.

#### 6. Ponavljanje Dugotrajnih Faza (10h izgubljeno)
**Problem**: Svaki test pokretao import i embedding generation od početka.
**Rešenje**: Caching mehanizam, "skip if exists" logika.

### Top 5 Optimizacija

1. **Hybrid Search** (45% vector + 35% keyword + 20% graph) - najbolji balans
2. **Batch Processing** - 10x brže od pojedinačnog procesiranja
3. **Parallel Execution** - 2x brže pretraživanje
4. **Caching** - 45x brže za ponovljene upite
5. **Database Indexing** - 100x brže upite

---

## 🏗️ Nova Arhitektura - DDD Pristup

### Bounded Contexts (6 konteksta)

```
┌─────────────────────────────────────────────────────────────────┐
│                    ZAIKON V2 - DDD ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐     ┌──────────────────────┐
│  Document Management │────▶│  Corpus Management   │
│                      │     │                      │
│ - Text Extraction    │     │ - Corpus CRUD        │
│ - Legal Parsing      │     │ - Import Pipeline    │
│ - Structure Analysis │     │ - Run Tracking       │
└──────────────────────┘     └──────────┬───────────┘
                                        │
                                        ▼
┌──────────────────────┐     ┌──────────────────────┐
│ Knowledge            │────▶│  Conflict Detection  │
│ Representation       │     │                      │
│                      │     │ - Rule Engine        │
│ - Ontology Sets      │     │ - Finding Generation │
│ - Embeddings         │     │ - Severity Scoring   │
│ - Semantic Search    │     └──────────────────────┘
└──────────────────────┘                │
         │                              │
         ▼                              ▼
┌──────────────────────┐     ┌──────────────────────┐
│  Configuration       │     │   Draft Review       │
│                      │     │                      │
│ - ParamSets          │     │ - Draft Analysis     │
│ - Versioning         │     │ - Conflict Report    │
│ - Export/Import      │     │ - Resolution         │
└──────────────────────┘     └──────────────────────┘
```

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                      │
│  FastAPI Routers, REST Endpoints, WebSocket             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                       │
│  Use Cases, Application Services, DTOs                   │
│  - ImportCorpusUseCase                                   │
│  - SearchCorpusUseCase                                   │
│  - AnalyzeDraftUseCase                                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                          │
│  Aggregates, Entities, Value Objects, Domain Services    │
│  - Document, Corpus, OntologySet, Finding                │
│  - ConflictDetectionService, LegalParserService          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                     │
│  Repositories, External Services, Persistence            │
│  - SQLite, Qdrant, Ollama, File System                  │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Domain Model V3 (Production-Ready)

### Ključni Entiteti

#### 1. Domain (Pravna Oblast)
```python
class Domain:
    id: UUID
    name: str  # "Radno pravo", "Šumarstvo"
    description: str
    created_at: datetime
```

#### 2. OntologySet (Verzionisana Ontologija)
```python
class OntologySet:
    id: UUID
    domain_id: UUID
    version: str  # "1.0", "2.0"
    name: str
    language: str  # "sr", "en"
    created_at: datetime
    terms: List[OntologyTerm]  # 1:N
```

#### 3. ConflictRuleSet (Verzionisana Pravila)
```python
class ConflictRuleSet:
    id: UUID
    domain_id: UUID
    version: str  # "1.0", "2.0"
    name: str
    description: str
    created_at: datetime
    rules: List[ConflictRule]  # 1:N
```

#### 4. ParamSet (Parametri za Reproducibilnost)
```python
class ParamSet:
    id: UUID
    name: str
    llm_model: str  # "llama3.2:latest"
    llm_temperature: float  # 0.7
    ontology_set_id: UUID
    conflict_rule_set_id: UUID
    embedding_model: str  # "BAAI/bge-m3"
    vector_weight: float  # 0.45
    keyword_weight: float  # 0.35
    graph_weight: float  # 0.20
    created_at: datetime
```

#### 5. Corpus (Kolekcija Dokumenata)
```python
class Corpus:
    id: UUID
    name: str
    domain_id: UUID
    language: str
    status: str  # "active", "archived"
    created_at: datetime
    runs: List[CorpusRun]  # 1:N
```

#### 6. CorpusRun (Tracking Izvršavanja)
```python
class CorpusRun:
    id: UUID
    corpus_id: UUID
    param_set_id: UUID
    ontology_set_id: UUID
    conflict_rule_set_id: UUID
    status: str  # "running", "completed", "failed"
    started_at: datetime
    ended_at: Optional[datetime]
    stats: Dict  # documents, legal_units, assertions
```

#### 7. Document (Pravni Dokument)
```python
class Document:
    id: UUID
    corpus_id: UUID
    corpus_run_id: UUID  # Tracking
    language: str
    filename: str
    title: str
    document_type: str  # "zakon", "uredba"
    is_draft: bool  # Unified: corpus + draft
    canonical_json: Dict
    created_at: datetime
    legal_units: List[LegalUnit]  # 1:N
```

#### 8. LegalUnit (Pravna Jedinica)
```python
class LegalUnit:
    id: UUID
    document_id: UUID
    corpus_run_id: UUID  # Tracking
    language: str
    unit_type: str  # "clan", "stav", "tacka"
    number: int
    title: str
    content: str
    parent_id: Optional[UUID]
    assertions: List[Assertion]  # 1:N
```

#### 9. Assertion (Normativna Tvrdnja)
```python
class Assertion:
    id: UUID
    legal_unit_id: UUID
    corpus_run_id: UUID  # Tracking
    language: str
    assertion_type: str  # "obaveza", "zabrana", "pravo"
    content: str
    entities: Dict  # action, object, domain, modality
    conditions: List[str]
    exceptions: List[str]
    embedding: Optional[Embedding]  # 1:1
```

#### 10. Embedding (Vektorska Reprezentacija)
```python
class Embedding:
    id: UUID
    assertion_id: UUID
    corpus_run_id: UUID  # Tracking
    language: str
    vector: List[float]  # 1024 dimensions
    model: str  # "BAAI/bge-m3"
    created_at: datetime
```

#### 11. Finding (Detektovani Konflikt)
```python
class Finding:
    id: UUID
    draft_review_id: UUID
    assertion1_id: UUID  # Draft ili Corpus
    assertion2_id: UUID  # Draft ili Corpus
    conflict_rule_id: UUID
    severity: str  # "critical", "high", "medium", "low"
    score: float
    explanation: str
    recommendation: str
    created_at: datetime
    resolution: Optional[Resolution]  # 1:1
```

#### 12. Resolution (Rešenje Konflikta)
```python
class Resolution:
    id: UUID
    finding_id: UUID
    status: str  # "accepted", "rejected", "deferred"
    decision: str
    comment: str
    resolved_by: str
    resolved_at: datetime
```

---

## 🔧 Tehnološki Stack

### Backend
- **Python**: 3.12+
- **Framework**: FastAPI 0.104+
- **Database**: SQLite (centralizovano na `data/zaikon.db`)
- **Vector Store**: Qdrant (embedded mode, `data/qdrant_storage/`)
- **Embeddings**: BAAI/bge-m3 (1024 dim, 3.2GB VRAM)
- **Reranker**: BAAI/bge-reranker-v2-m3 (2.1GB VRAM)
- **NLP**: Stanza 1.9.2 (Serbian NER)
- **LLM**: Ollama (optional, Mistral 7B / Llama 3.1 8B)
- **Document Processing**: PyMuPDF 1.24.13, python-docx 1.1.2
- **Deep Learning**: PyTorch 2.5.1

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **State Management**: React Query + Zustand
- **UI Components**: Radix UI + Tailwind CSS
- **API Client**: Axios

### DevOps
- **Testing**: pytest, pytest-asyncio
- **Linting**: ruff, mypy
- **Formatting**: black
- **CI/CD**: GitHub Actions
- **Containerization**: Docker + Docker Compose

---

## 📁 Folder Struktura (DDD)

```
ZAIKON/
├── backend/
│   ├── zaikon/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app
│   │   │
│   │   ├── core/                      # Shared infrastructure
│   │   │   ├── config.py              # Settings
│   │   │   ├── database.py            # SQLite connection
│   │   │   ├── logging.py             # Logging setup
│   │   │   └── exceptions.py          # Custom exceptions
│   │   │
│   │   ├── domain/                    # Domain Layer
│   │   │   ├── document_management/   # BC: Document Management
│   │   │   │   ├── entities/
│   │   │   │   │   ├── document.py
│   │   │   │   │   ├── legal_unit.py
│   │   │   │   │   └── assertion.py
│   │   │   │   ├── value_objects/
│   │   │   │   │   ├── document_metadata.py
│   │   │   │   │   ├── legal_unit_reference.py
│   │   │   │   │   └── assertion_content.py
│   │   │   │   ├── services/
│   │   │   │   │   ├── legal_parser_service.py
│   │   │   │   │   ├── text_extraction_service.py
│   │   │   │   │   └── structure_analysis_service.py
│   │   │   │   └── events/
│   │   │   │       ├── document_imported.py
│   │   │   │       └── assertions_extracted.py
│   │   │   │
│   │   │   ├── corpus_management/    # BC: Corpus Management
│   │   │   │   ├── entities/
│   │   │   │   │   ├── corpus.py
│   │   │   │   │   └── corpus_run.py
│   │   │   │   ├── value_objects/
│   │   │   │   │   ├── corpus_metadata.py
│   │   │   │   │   └── run_parameters.py
│   │   │   │   ├── services/
│   │   │   │   │   ├── corpus_import_service.py
│   │   │   │   │   └── corpus_indexing_service.py
│   │   │   │   └── events/
│   │   │   │       ├── corpus_created.py
│   │   │   │       └── corpus_run_completed.py
│   │   │   │
│   │   │   ├── knowledge_representation/  # BC: Knowledge
│   │   │   │   ├── entities/
│   │   │   │   │   ├── ontology_set.py
│   │   │   │   │   ├── ontology_term.py
│   │   │   │   │   └── embedding.py
│   │   │   │   ├── value_objects/
│   │   │   │   │   ├── ontology_metadata.py
│   │   │   │   │   └── vector_representation.py
│   │   │   │   ├── services/
│   │   │   │   │   ├── embedding_generation_service.py
│   │   │   │   │   ├── semantic_search_service.py
│   │   │   │   │   └── ontology_matching_service.py
│   │   │   │   └── events/
│   │   │   │       └── embeddings_generated.py
│   │   │   │
│   │   │   ├── conflict_detection/   # BC: Conflict Detection
│   │   │   │   ├── entities/
│   │   │   │   │   ├── conflict_rule_set.py
│   │   │   │   │   ├── conflict_rule.py
│   │   │   │   │   ├── finding.py
│   │   │   │   │   └── resolution.py
│   │   │   │   ├── value_objects/
│   │   │   │   │   ├── rule_definition.py
│   │   │   │   │   └── conflict_score.py
│   │   │   │   ├── services/
│   │   │   │   │   ├── conflict_detection_service.py
│   │   │   │   │   └── severity_calculation_service.py
│   │   │   │   └── events/
│   │   │   │       └── conflict_detected.py
│   │   │   │
│   │   │   ├── draft_review/         # BC: Draft Review
│   │   │   │   ├── entities/
│   │   │   │   │   └── draft_review.py
│   │   │   │   ├── services/
│   │   │   │   │   └── draft_analysis_service.py
│   │   │   │   └── events/
│   │   │   │       └── draft_analyzed.py
│   │   │   │
│   │   │   └── configuration/        # BC: Configuration
│   │   │       ├── entities/
│   │   │       │   ├── domain.py
│   │   │       │   └── param_set.py
│   │   │       └── services/
│   │   │           └── export_import_service.py
│   │   │
│   │   ├── application/               # Application Layer
│   │   │   ├── use_cases/
│   │   │   │   ├── import_corpus_use_case.py
│   │   │   │   ├── search_corpus_use_case.py
│   │   │   │   └── analyze_draft_use_case.py
│   │   │   ├── dtos/
│   │   │   │   ├── corpus_dto.py
│   │   │   │   ├── document_dto.py
│   │   │   │   └── finding_dto.py
│   │   │   └── services/
│   │   │       └── application_service.py
│   │   │
│   │   ├── infrastructure/            # Infrastructure Layer
│   │   │   ├── repositories/
│   │   │   │   ├── corpus_repository.py
│   │   │   │   ├── document_repository.py
│   │   │   │   ├── assertion_repository.py
│   │   │   │   ├── finding_repository.py
│   │   │   │   └── ontology_repository.py
│   │   │   ├── external_services/
│   │   │   │   ├── qdrant_service.py
│   │   │   │   ├── ollama_service.py
│   │   │   │   └── stanza_service.py
│   │   │   └── persistence/
│   │   │       ├── sqlite_connection.py
│   │   │       └── migrations/
│   │   │
│   │   └── presentation/              # Presentation Layer
│   │       ├── api/
│   │       │   ├── routers/
│   │       │   │   ├── corpus_router.py
│   │       │   │   ├── draft_router.py
│   │       │   │   ├── conflict_router.py
│   │       │   │   └── config_router.py
│   │       │   ├── dependencies.py
│   │       │   └── middleware.py
│   │       └── websocket/
│   │           └── progress_handler.py
│   │
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   │
│   ├── scripts/
│   │   ├── init_db.py
│   │   ├── import_test_corpus.py
│   │   └── benchmark.py
│   │
│   ├── pyproject.toml
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── corpus/
│   │   │   ├── draft/
│   │   │   ├── findings/
│   │   │   └── common/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── data/                              # Data directory
│   ├── zaikon.db                      # SQLite database
│   ├── qdrant_storage/                # Qdrant vector store
│   └── logs/                          # Application logs
│
├── DOCUMENTS/                         # Test documents
│   ├── corpus/
│   └── drafts/
│
├── GEN/                               # Documentation
│   ├── README.md
│   ├── LESSONS_LEARNED.md
│   ├── DDD_ARCHITECTURE.md
│   └── ...
│
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## 🚀 Implementacioni Plan (7 Nedelja)

### Nedelja 1: Core Infrastructure & Domain Layer
**Cilj**: Postaviti osnovu projekta i domain entitete

**Dan 1-2: Project Setup**
- [ ] Kreirati folder strukturu
- [ ] Setup Python projekat (pyproject.toml)
- [ ] Setup Frontend projekat (package.json)
- [ ] Konfiguracija (Settings, Environment)
- [ ] Logging setup sa verbosity nivoima
- [ ] Database schema (SQLite)

**Dan 3-4: Domain Entities**
- [ ] Document Management entities (Document, LegalUnit, Assertion)
- [ ] Corpus Management entities (Corpus, CorpusRun)
- [ ] Knowledge Representation entities (OntologySet, OntologyTerm, Embedding)
- [ ] Conflict Detection entities (ConflictRuleSet, ConflictRule, Finding, Resolution)
- [ ] Configuration entities (Domain, ParamSet)

**Dan 5-7: Value Objects & Domain Events**
- [ ] Value Objects za sve entitete
- [ ] Domain Events definicije
- [ ] Unit testovi za domain layer

---

### Nedelja 2: Infrastructure Layer
**Cilj**: Implementirati repositories i eksterne servise

**Dan 1-3: Repositories**
- [ ] CorpusRepository (CRUD + queries)
- [ ] DocumentRepository (CRUD + queries)
- [ ] AssertionRepository (CRUD + queries)
- [ ] FindingRepository (CRUD + queries)
- [ ] OntologyRepository (CRUD + queries)
- [ ] Unit testovi za repositories

**Dan 4-5: External Services**
- [ ] QdrantService (vector store operations)
- [ ] OllamaService (LLM integration)
- [ ] StanzaService (NER)
- [ ] Integration testovi

**Dan 6-7: Persistence**
- [ ] SQLite connection pool
- [ ] Database migrations
- [ ] Transaction management
- [ ] Error handling

---

### Nedelja 3: Domain Services
**Cilj**: Implementirati biznis logiku

**Dan 1-2: Document Management Services**
- [ ] LegalParserService (parsing pravnih dokumenata)
  - Podrška za latinicu I ćirilicu
  - Regex pattern-i za članove, stavove, tačke
- [ ] TextExtractionService (PDF, DOCX, TXT)
  - UTF-8 encoding
  - Error handling
- [ ] StructureAnalysisService (analiza strukture)

**Dan 3-4: Knowledge Representation Services**
- [ ] EmbeddingGenerationService
  - BAAI/bge-m3 integration
  - Batch processing (32-64)
  - Progress tracking
- [ ] SemanticSearchService
  - Hybrid search (45% vector + 35% keyword + 20% graph)
  - Reranking
- [ ] OntologyMatchingService

**Dan 5-7: Conflict Detection Services**
- [ ] ConflictDetectionService
  - Slot-based matching
  - Candidate scoring (threshold 0.25)
  - 127 conflict types
- [ ] SeverityCalculationService
- [ ] Unit testovi za sve servise

---

### Nedelja 4: Application Layer (Use Cases)
**Cilj**: Implementirati use case-ove

**Dan 1-3: ImportCorpusUseCase**
- [ ] File-by-file import pipeline
- [ ] Per-file processing chain:
  - ExtractTextStep
  - NormalizeTextStep
  - ParseLegalStructureStep
  - ExtractNormativeAssertionsStep
  - **StoreAssertionsStep** (u per-file chain!)
  - BuildIndexesStep
- [ ] Progress tracking
- [ ] Error handling
- [ ] Caching mehanizam ("skip if exists")

**Dan 4-5: SearchCorpusUseCase**
- [ ] Hybrid search implementation
- [ ] Reranking
- [ ] Result formatting
- [ ] Caching (45x speedup)

**Dan 6-7: AnalyzeDraftUseCase**
- [ ] Draft parsing
- [ ] Assertion extraction
- [ ] Conflict detection
- [ ] Finding generation
- [ ] Report generation

---

### Nedelja 5: Presentation Layer (API)
**Cilj**: Implementirati REST API

**Dan 1-2: Corpus Router**
- [ ] POST /api/v1/corpora (create corpus)
- [ ] GET /api/v1/corpora (list corpora)
- [ ] GET /api/v1/corpora/{id} (get corpus)
- [ ] POST /api/v1/corpora/{id}/import (import documents)
- [ ] GET /api/v1/corpora/{id}/progress (import progress)
- [ ] DELETE /api/v1/corpora/{id} (delete corpus)

**Dan 3-4: Draft Router**
- [ ] POST /api/v1/draft-reviews (create draft review)
- [ ] GET /api/v1/draft-reviews (list reviews)
- [ ] GET /api/v1/draft-reviews/{id} (get review)
- [ ] POST /api/v1/draft-reviews/{id}/analyze (analyze draft)
- [ ] GET /api/v1/draft-reviews/{id}/findings (get findings)

**Dan 5: Conflict Router**
- [ ] GET /api/v1/conflicts/types (list conflict types)
- [ ] GET /api/v1/conflicts/rules (list rules)
- [ ] POST /api/v1/conflicts/rules (create rule)

**Dan 6-7: Configuration Router & WebSocket**
- [ ] GET /api/v1/config/domains (list domains)
- [ ] GET /api/v1/config/ontologies (list ontology sets)
- [ ] GET /api/v1/config/param-sets (list param sets)
- [ ] WebSocket /ws/progress (real-time progress)

---

### Nedelja 6: Frontend
**Cilj**: Implementirati React aplikaciju

**Dan 1-2: Core Setup & Components**
- [ ] Vite + React + TypeScript setup
- [ ] Tailwind CSS + Radix UI
- [ ] API client (Axios)
- [ ] State management (React Query + Zustand)
- [ ] Common components (Button, Input, Card, etc.)

**Dan 3-4: Corpus Management UI**
- [ ] Corpus list view
- [ ] Create corpus form
- [ ] Import documents interface
- [ ] Progress indicator (real-time via WebSocket)
- [ ] Corpus details view

**Dan 5-6: Draft Review UI**
- [ ] Draft editor
- [ ] Corpus selection
- [ ] Analyze button
- [ ] Findings list
- [ ] Finding details modal

**Dan 7: Configuration UI**
- [ ] Domain management
- [ ] Ontology set management
- [ ] Param set management
- [ ] Conflict rule management

---

### Nedelja 7: Testing, Optimization & Deployment
**Cilj**: Testiranje, optimizacija, deployment

**Dan 1-2: Testing**
- [ ] Unit tests (90%+ coverage)
- [ ] Integration tests
- [ ] E2E tests (Playwright)
- [ ] Performance tests
- [ ] Load tests

**Dan 3-4: Optimization**
- [ ] Database indexing
- [ ] Query optimization
- [ ] Caching strategy
- [ ] Batch processing tuning
- [ ] Memory profiling

**Dan 5-6: Documentation**
- [ ] API documentation (OpenAPI)
- [ ] User guide
- [ ] Developer guide
- [ ] Deployment guide

**Dan 7: Deployment**
- [ ] Docker setup
- [ ] Docker Compose
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Production deployment

---

## 🔍 Ključne Implementacione Smernice

### 1. Uvek Koristiti Centralizovanu Bazu
```python
from zaikon.core.config import settings

# ✅ ISPRAVNO
db_path = settings.database_path  # "data/zaikon.db"

# ❌ POGREŠNO
db_path = "zaikon.db"  # Relativna putanja
```

### 2. StoreAssertionsStep u Per-File Chain
```python
# ✅ ISPRAVNO - U per-file processing chain
def _process_single_file(self, file_info):
    steps = [
        ExtractTextStep(),
        ParseLegalStructureStep(),
        ExtractNormativeAssertionsStep(),
        StoreAssertionsStep(),  # ← OVDE!
    ]
```

### 3. UTF-8 Encoding Svuda
```python
# ✅ ISPRAVNO
with open(file, "r", encoding="utf-8") as f:
    text = f.read()
```

### 4. Opširan Logging
```python
logger.info("="*80)
logger.info(f"PROCESSING: {doc_id}")
logger.info(f"  Input: {len(text)} chars")
logger.info(f"  Output: {len(assertions)} assertions")
logger.info(f"  Time: {elapsed:.3f}s")
logger.info("="*80)
```

### 5. Validacija Međurezultata
```python
if len(assertions) == 0:
    logger.warning("⚠ No assertions extracted!")
    logger.warning(f"  Document: {doc_id}")
    logger.warning(f"  Text sample: {text[:200]}")
```

### 6. Caching Mehanizam
```python
def import_corpus(corpus_id: str, force: bool = False):
    if not force and corpus_exists(corpus_id):
        logger.info(f"Corpus {corpus_id} already exists, skipping")
        return load_corpus(corpus_id)
    
    # Import logic...
```

### 7. Batch Processing
```python
# Embeddings: batch_size = 32-64
for batch in batched(assertions, batch_size=32):
    embeddings = model.encode(batch)
    
# Keyword indexing: batch_size = 100
for batch in batched(documents, batch_size=100):
    index.add_documents(batch)
```

### 8. Error Handling
```python
try:
    result = process_document(doc_id)
except Exception as e:
    logger.error(f"Failed to process {doc_id}: {e}")
    # Store error in database
    store_error(doc_id, str(e))
    # Continue with next document
    continue
```

---

## 📊 Performance Targets

### Import Performance
- **Single Document**: < 5s (parsing + extraction + storage)
- **100 Documents**: < 10 minutes (with batch processing)
- **Embedding Generation**: < 2s per document (batch_size=32)

### Search Performance
- **Hybrid Search**: < 140ms per query
- **Reranking**: < 50ms for top 100 results
- **Total Search Time**: < 200ms

### Conflict Detection Performance
- **Single Draft**: < 30s (100 assertions vs 10,000 corpus assertions)
- **Candidate Finding**: < 10s
- **Conflict Checking**: < 20s

### Memory Usage
- **Embedding Model**: 3.2GB VRAM (BAAI/bge-m3)
- **Reranker Model**: 2.1GB VRAM (BAAI/bge-reranker-v2-m3)
- **NER Model**: 1.5GB RAM (Stanza Serbian)
- **Total**: ~7GB (fits in RTX 5070 Ti 16GB)

---

## ✅ Checklist Pre-Implementation

### Pre-Coding
- [ ] Pročitati LESSONS_LEARNED.md (OBAVEZNO!)
- [ ] Razumeti DDD_ARCHITECTURE.md
- [ ] Razumeti DOMAIN_MODEL_V3.md
- [ ] Pregledati CONFLICT_TYPES_SPECIFICATION.md

### During Implementation
- [ ] Koristiti centralizovanu bazu (settings.database_path)
- [ ] StoreAssertionsStep u per-file chain
- [ ] UTF-8 encoding svuda
- [ ] Opširan logging sa fazama
- [ ] Validacija međurezultata
- [ ] Caching mehanizam
- [ ] Batch processing
- [ ] Error handling

### Post-Implementation
- [ ] Unit testovi (90%+ coverage)
- [ ] Integration testovi
- [ ] Performance testovi
- [ ] Load testovi
- [ ] Documentation

---

## 🎓 Zaključak

Ova arhitektura je zasnovana na:
1. **Lessons Learned** - Izbegavanje 50+ sati grešaka
2. **DDD Principi** - Jasne granice, agregati, eventi
3. **Production-Ready** - Verzionisanje, parametrizacija, export/import
4. **Performance** - Hybrid search, caching, batch processing
5. **Maintainability** - Modularnost, testabilnost, dokumentacija

**Sledeći korak**: Kreirati detaljni implementacioni plan za svaku nedelju.