# GROOVE.AI - Revised Architecture (Production-Ready)

**Version**: 2.0  
**Last Updated**: 2026-06-07  
**Status**: Production Architecture with Knowledge Enrichment

---

## Executive Summary

Ova arhitektura incorporira sve lessons learned iz prethodnog pokušaja i optimizuje pipeline za maksimalnu efikasnost i kvalitet podataka.

**Ključne Izmene:**
1. ✅ **Knowledge Enrichment Phase** - Ontology/References/Definitions PRE Vector Store
2. ✅ **Hybrid Storage** - SQLite (audit) + Qdrant (production search)
3. ✅ **Unified Vector Store** - Embeddings + Keywords u jednom modulu
4. ✅ **Separate Search Service** - Dedicated modul za hybrid search

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GROOVE.AI SYSTEM ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: DOCUMENT INGESTION & PREPROCESSING                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  M1: File Reader (8101)                                                     │
│  ├─ Input: PDF/DOCX/TXT files                                              │
│  ├─ Output: Raw text + metadata                                            │
│  └─ Storage: SQLite (file_reader.db)                                       │
│                          ↓                                                   │
│  M2: Text Normalizer (8102)                                                │
│  ├─ Input: Raw text                                                        │
│  ├─ Output: Normalized text (whitespace, encoding)                         │
│  └─ Storage: SQLite (text_normalizer.db)                                   │
│                          ↓                                                   │
│  M3: Latinizer (8103)                                                      │
│  ├─ Input: Cyrillic text                                                   │
│  ├─ Output: Latin text                                                     │
│  └─ Storage: SQLite (latinizer.db)                                         │
│                          ↓                                                   │
│  M4: Legal Parser (8105)                                                   │
│  ├─ Input: Latin text                                                      │
│  ├─ Output: Structured legal units (articles, paragraphs, items)          │
│  └─ Storage: SQLite (legal_parser.db)                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: ASSERTION EXTRACTION & ANALYSIS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  M6: Assertion Extractor (8106)                                            │
│  ├─ Input: Legal units                                                     │
│  ├─ Output: Normative assertions                                           │
│  └─ Storage: SQLite (assertion_extractor.db)                               │
│                          ↓                                                   │
│  M7: Entity Recognizer (8107)                                              │
│  ├─ Input: Assertions                                                      │
│  ├─ Output: Assertions + entities (PERSON, ORG, MONEY, DATE, etc.)        │
│  └─ Storage: SQLite (entity_recognizer.db)                                 │
│                          ↓                                                   │
│  M8: Condition Extractor (8108)                                            │
│  ├─ Input: Assertions + entities                                           │
│  ├─ Output: Assertions + conditions, exceptions, temporal clauses          │
│  └─ Storage: SQLite (condition_extractor.db)                               │
│                          ↓                                                   │
│  M9: Assertion Classifier (8109)                                           │
│  ├─ Input: Assertions + entities + conditions                              │
│  ├─ Output: Classified assertions (obligation, right, prohibition, etc.)   │
│  └─ Storage: SQLite (assertion_classifier.db)                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: KNOWLEDGE ENRICHMENT                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  M10: Knowledge Enrichment (8110) - UNIFIED MODULE                         │
│  ├─ Input: Classified assertions from M9                                   │
│  ├─ Functions:                                                              │
│  │   1. Ontology Matcher - Maps to domain ontology (ZAIKON hybrid)        │
│  │   2. Reference Resolver - Resolves legal references                     │
│  │   3. Definition Extractor - Extracts legal term definitions             │
│  ├─ Output: ENRICHED assertions with full metadata                         │
│  └─ Storage: SQLite (knowledge_enrichment.db)                              │
│      ├─ ontology_terms (canonical, labels, confidence, frequency)          │
│      ├─ ontology_relationships (broader_than, narrower_than)               │
│      ├─ ontology_domains (term domains)                                    │
│      ├─ references (resolved legal references)                              │
│      └─ definitions (extracted legal terms)                                 │
│                                                                              │
│  Ontology Matching (Hybrid ZAIKON Approach):                               │
│  ├─ Database-backed ontology (SQLite)                                      │
│  ├─ Auto-learning from NER extractions                                     │
│  ├─ Confidence scoring                                                      │
│  └─ Frequency tracking                                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: INDEXING & STORAGE                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  M11: Vector Store (8111) - UNIFIED MODULE                                 │
│  ├─ Input: ENRICHED assertions (with ontology, references, definitions)    │
│  ├─ Functions:                                                              │
│  │   1. Generate semantic embeddings (BAAI/bge-m3, 1024-dim)              │
│  │   2. Generate keyword index (BM25)                                      │
│  │   3. Store vectors in Qdrant (production search)                        │
│  │   4. Store JSON in SQLite (audit trail + development control)          │
│  ├─ Output: Searchable vector database                                     │
│  └─ Storage:                                                                │
│      ├─ Qdrant: data/qdrant_storage/                                       │
│      │   ├─ Collection: corpus_assertions                                  │
│      │   ├─ Collection: draft_assertions                                   │
│      │   └─ Payload: {text, vector, keywords, ontology, refs, defs, ...}  │
│      └─ SQLite: data/databases/vector_store.db (audit only)                │
│                                                                              │
│  Qdrant Payload Structure:                                                  │
│  {                                                                           │
│    "id": "assertion_123",                                                   │
│    "vector": [0.123, -0.456, ...],  // 1024-dim semantic embedding         │
│    "payload": {                                                             │
│      // Core data                                                           │
│      "text": "Ugovor se zaključuje pismeno.",                              │
│      "assertion_type": "obligation",                                        │
│      "source_document": "zakon_o_obligacionim_odnosima.pdf",               │
│      "source_article": "Član 25",                                          │
│                                                                              │
│      // Entities (from M7)                                                  │
│      "entities": {                                                          │
│        "PERSON": ["Prodavac", "Kupac"],                                    │
│        "MONEY": ["1000 EUR"],                                              │
│        "DATE": ["01.01.2024"]                                              │
│      },                                                                     │
│                                                                              │
│      // Conditions (from M8)                                                │
│      "conditions": ["ako je cena veća od 1000 EUR"],                       │
│      "exceptions": ["osim u slučaju..."],                                  │
│      "temporal_clauses": ["u roku od 30 dana"],                            │
│                                                                              │
│      // Ontology (from M13)                                                 │
│      "ontology_concepts": [                                                 │
│        {"concept": "contract_formation", "confidence": 0.95},              │
│        {"concept": "written_form_requirement", "confidence": 0.88}         │
│      ],                                                                     │
│                                                                              │
│      // References (from M14)                                               │
│      "references": [                                                        │
│        {                                                                    │
│          "text": "Član 25",                                                │
│          "resolved_to": "Zakon o obligacionim odnosima, Član 25",         │
│          "document_id": "zoo_2023"                                         │
│        }                                                                    │
│      ],                                                                     │
│                                                                              │
│      // Definitions (from M15)                                              │
│      "definitions": [                                                       │
│        {                                                                    │
│          "term": "ugovor",                                                 │
│          "definition": "Saglasnost volja dve ili više strana...",         │
│          "source": "Član 10 ZOO"                                           │
│        }                                                                    │
│      ],                                                                     │
│                                                                              │
│      // Keywords (for hybrid search)                                        │
│      "keywords": ["ugovor", "zaključuje", "pismeno"],                      │
│      "keyword_scores": {                                                    │
│        "ugovor": 0.8,                                                      │
│        "zaključuje": 0.6,                                                  │
│        "pismeno": 0.7                                                      │
│      }                                                                      │
│    }                                                                         │
│  }                                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: SEARCH & RETRIEVAL                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  M12: Search Service (8112) - SEPARATE MODULE                              │
│  ├─ Input: User query                                                      │
│  ├─ Functions:                                                              │
│  │   1. Query processing & expansion                                       │
│  │   2. Semantic search (vector similarity in Qdrant)                      │
│  │   3. Keyword search (BM25 in Qdrant payload)                           │
│  │   4. Hybrid fusion (weighted combination)                               │
│  │   5. Filtering (by ontology, entities, conditions, etc.)               │
│  │   6. Reranking (BAAI/bge-reranker-v2-m3)                               │
│  ├─ Output: Ranked search results                                          │
│  └─ Storage: SQLite (search_service.db) - query logs only                  │
│                                                                              │
│  Search Weights (configurable):                                             │
│  ├─ Semantic (vector): 0.45                                                │
│  ├─ Keyword (BM25): 0.35                                                   │
│  └─ Graph (ontology): 0.20                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 6: CONFLICT DETECTION (Future)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  M16: Candidate Finder (8116)                                              │
│  M17: Conflict Detector (8117)                                             │
│  M18: Severity Calculator (8118)                                           │
│  M19: Recommendation Generator (8119)                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

---

## Module Dependencies

```
M1 (File Reader)
  ↓
M2 (Text Normalizer)
  ↓
M3 (Latinizer)
  ↓
M4 (Legal Parser)
  ↓
M6 (Assertion Extractor)
  ↓
M7 (Entity Recognizer)
  ↓
M8 (Condition Extractor)
  ↓
M9 (Assertion Classifier)
  ↓
M10 (Knowledge Enrichment) ← Unified: Ontology + References + Definitions
  ↓
M11 (Vector Store) ← Stores ENRICHED data
  ↓
M12 (Search Service) ← Searches enriched data
```

---

## Port Allocation

| Module | Port | Purpose |
|--------|------|---------|
| M1: File Reader | 8101 | Document ingestion |
| M2: Text Normalizer | 8102 | Text preprocessing |
| M3: Latinizer | 8103 | Script conversion |
| M4: Legal Parser | 8105 | Structure extraction |
| M6: Assertion Extractor | 8106 | Assertion extraction |
| M7: Entity Recognizer | 8107 | Entity recognition |
| M8: Condition Extractor | 8108 | Condition extraction |
| M9: Assertion Classifier | 8109 | Assertion classification |
| M10: Knowledge Enrichment | 8110 | Ontology + References + Definitions |
| M11: Vector Store | 8111 | Embedding + indexing + storage |
| M12: Search Service | 8112 | Hybrid search |
| M13: Candidate Finder | 8113 | Conflict candidates |
| M14: Conflict Detector | 8114 | Conflict detection |
| M15: Severity Calculator | 8115 | Severity scoring |
| M16: Recommendation Generator | 8116 | Recommendations |

---

## Storage Strategy

### SQLite (Audit Trail + Development)
- **Purpose**: Job history, debugging, reprocessing
- **Location**: `data/databases/*.db`
- **Content**: 
  - Processing metadata
  - Job status and timing
  - JSON representation of embeddings (for debugging)
  - Error logs

### Qdrant (Production Search)
- **Purpose**: Fast semantic + keyword search
- **Location**: `data/qdrant_storage/`
- **Content**:
  - Vector embeddings (1024-dim)
  - Rich payload with all enriched metadata
  - Keyword scores for hybrid search
  - Optimized for similarity search (HNSW algorithm)

---

## Key Improvements Over Previous Version

### 1. Knowledge Enrichment Phase
✅ **Before**: Assertions stored immediately after classification  
✅ **After**: Assertions enriched with ontology, references, definitions BEFORE storage

### 2. Unified Vector Store
✅ **Before**: Separate modules for embeddings, keywords, vector storage  
✅ **After**: Single module handles all indexing and storage

### 3. Hybrid Storage
✅ **Before**: Only SQLite or only Qdrant  
✅ **After**: SQLite for audit, Qdrant for production search

### 4. Rich Metadata
✅ **Before**: Basic assertion data  
✅ **After**: Comprehensive metadata (entities, conditions, ontology, references, definitions, keywords)

### 5. Separate Search Service
✅ **Before**: Search logic mixed with storage  
✅ **After**: Dedicated search module with hybrid fusion and reranking

---

## Lessons Learned Applied

### From LESSONS_LEARNED.md:

1. ✅ **Artifact Validation**: Each module validates required artifacts
2. ✅ **Context Awareness**: Modules understand their execution context
3. ✅ **Data Verification**: Modules verify data is actually stored
4. ✅ **Flexible Validation**: Optional artifacts don't block execution
5. ✅ **Clear Dependencies**: Explicit module dependency chain

---

## Next Steps

1. ✅ Implement M13: Ontology Matcher
2. ✅ Implement M14: Reference Resolver
3. ✅ Implement M15: Definition Extractor
4. ✅ Refactor M10: Vector Store (Qdrant + Keywords)
5. ✅ Implement M11: Search Service
6. ✅ Test full pipeline (M1→M2→M3→M4→M6→M7→M8→M9→M13→M14→M15→M10→M11)
7. ✅ Performance optimization
8. ✅ Production deployment

---

## Success Criteria

- ✅ All assertions enriched with ontology, references, definitions
- ✅ Vectors stored in Qdrant with rich metadata
- ✅ Hybrid search (semantic + keyword) working
- ✅ Search results include all enriched metadata
- ✅ Audit trail in SQLite for debugging
- ✅ Pipeline processes 100+ documents without errors
- ✅ Search latency < 500ms for typical queries

---

**Made with Bob** 🤖