# Knowledge Enrichment Module (M10)

**Port**: 8110  
**Version**: 1.0.0  
**Status**: ✅ Implemented

## Overview

The Knowledge Enrichment Module enriches legal assertions with three types of knowledge:

1. **Ontology Matching** - Matches entities to canonical ontology terms with auto-learning
2. **Reference Resolution** - Identifies and resolves legal citations
3. **Definition Extraction** - Extracts term definitions from legal text

This module implements a **hybrid ontology approach** based on lessons learned from the ZAIKON project, combining database-backed ontology with automatic learning from NER extractions.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Knowledge Enrichment Module (M10)              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │ Ontology Matcher │  │ Reference        │  │Definition │ │
│  │                  │  │ Resolver         │  │Extractor  │ │
│  │ - DB lookup      │  │                  │  │           │ │
│  │ - Auto-learning  │  │ - Pattern match  │  │- Pattern  │ │
│  │ - Confidence     │  │ - Parse citation │  │  match    │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         SQLite Database (Hybrid Ontology)            │  │
│  │  - ontology_terms                                    │  │
│  │  - ontology_relationships                            │  │
│  │  - ontology_domains                                  │  │
│  │  - legal_references                                  │  │
│  │  - term_definitions                                  │  │
│  │  - enriched_assertions (audit trail)                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. Hybrid Ontology Matching

- **Database-backed**: Ontology terms stored in SQLite for fast lookup
- **Auto-learning**: Automatically learns new terms from NER extractions
- **Dual NER engines**: Uses entities from M7 (CLASSLA) + optional Stanza for additional coverage
- **Confidence scoring**: Tracks confidence and frequency of terms
- **Domain categorization**: Terms organized by legal domain

### 2. Legal Reference Resolution

Identifies and parses Serbian legal citations:
- "Član 5. Zakona o..."
- "Stav 2. člana 5."
- "Tačka 3) stava 2."
- "Službeni glasnik RS, br. 123/2020"

### 3. Definition Extraction

Extracts term definitions using patterns:
- "X znači Y"
- "Pod X se podrazumeva Y"
- "X je Y"
- "X predstavlja Y"
- "U smislu ovog zakona, X je Y"

## NER Integration

### Dual-Engine Approach

Module 10 uses a **dual NER engine approach** for comprehensive entity extraction:

1. **Primary: M7 (CLASSLA)** - Entities extracted by Module 7 are passed to M10
2. **Secondary: CLASSLA in M10 (Optional)** - M10 can optionally run additional CLASSLA NER for enhanced coverage

This approach leverages CLASSLA's proven effectiveness for Serbian legal text, as demonstrated in the ZAIKON project.

### How It Works

```python
# In OntologyMatcher.match_terms()
all_entities = list(entities)  # Entities from M7 (CLASSLA)

if use_classla:
    classla_entities = self._extract_additional_entities_with_classla(text)
    # Add only unique entities (avoid duplicates)
    for classla_entity in classla_entities:
        if classla_entity['text'].lower() not in existing_texts:
            all_entities.append(classla_entity)
```

### Benefits

- **Dual CLASSLA Processing**: M7 and M10 both use CLASSLA but may detect different entities
- **Improved Recall**: Running NER twice with different contexts = better entity coverage
- **Graceful Degradation**: If M10's CLASSLA fails to load, continues with M7 entities only
- **No Duplication**: Duplicate entities are filtered out
- **Serbian-Optimized**: CLASSLA is specifically designed for Serbian language

### Configuration

CLASSLA NER in M10 is **optional** and controlled via the `use_classla` parameter in the enrichment request:

```json
{
  "assertion_id": 123,
  "assertion_text": "...",
  "entities": [...],
  "use_classla": true  // Optional, default: true
}
```


## API Endpoints

### Main Enrichment

**POST /enrich**
```json
{
  "assertion_id": 123,
  "assertion_text": "Pravno lice je organizacija...",
  "entities": [
    {"text": "pravno lice", "type": "LEGAL_TERM"}
  ]
}
```

Response:
```json
{
  "success": true,
  "enriched_assertion": {
    "assertion_id": 123,
    "matched_terms": [...],
    "legal_references": [...],
    "term_definitions": [...]
  },
  "processing_time_ms": 45.2
}
```

### Batch Enrichment

**POST /enrich/batch**
```json
{
  "assertions": [
    {"assertion_id": 1, "assertion_text": "..."},
    {"assertion_id": 2, "assertion_text": "..."}
  ]
}
```

### Standalone Operations

**POST /ontology/match** - Match ontology only  
**POST /references/resolve** - Resolve references only  
**POST /definitions/extract** - Extract definitions only

### Statistics

**GET /stats**
```json
{
  "total_terms": 1250,
  "total_relationships": 450,
  "total_references": 3200,
  "total_definitions": 890,
  "total_enriched": 5000,
  "avg_processing_time_ms": 42.5
}
```

## Database Schema

### ontology_terms
- `id` - Primary key
- `canonical_form` - Canonical term (unique)
- `label` - Display label
- `domain` - Legal domain
- `confidence` - Confidence score (0-1)
- `frequency` - Usage frequency
- `source` - Source (manual, ner, auto)

### ontology_relationships
- `id` - Primary key
- `term1_id` - First term
- `term2_id` - Second term
- `relationship_type` - Type (broader_than, narrower_than, etc.)
- `confidence` - Confidence score

### legal_references
- `id` - Primary key
- `assertion_id` - Assertion ID
- `raw_reference` - Raw citation text
- `document_type` - Type (zakon, uredba, etc.)
- `article_number` - Article number
- `paragraph_number` - Paragraph number
- `item_number` - Item number

### term_definitions
- `id` - Primary key
- `assertion_id` - Assertion ID
- `term` - Term being defined
- `definition` - Definition text
- `definition_pattern` - Pattern used
- `confidence` - Confidence score

## Usage

### Start Module
```bash
python -m modules.knowledge_enrichment.main
```

### Test Enrichment
```bash
curl -X POST http://localhost:8110/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "assertion_id": 1,
    "assertion_text": "Pravno lice je organizacija koja ima pravnu sposobnost.",
    "entities": [{"text": "pravno lice", "type": "LEGAL_TERM"}]
  }'
```

## Configuration

Module configuration in `config.yaml`:

```yaml
network:
  knowledge_enrichment:
    host: "0.0.0.0"
    port: 8110
    url: "http://localhost:8110"

database:
  knowledge_enrichment: "data/databases/knowledge_enrichment.db"

logging:
  knowledge_enrichment: "data/logs/knowledge_enrichment.log"
  level: "INFO"
```

## Integration with Pipeline

Module 10 receives classified assertions from Module 9 (Assertion Classifier) and enriches them before passing to Module 11 (Vector Store):

```
M9 (Classifier) → M10 (Knowledge Enrichment) → M11 (Vector Store)
```

## ZAIKON Lessons Learned

This module implements key insights from the ZAIKON project:

1. **Hybrid Ontology**: Database-backed with auto-learning is more maintainable than static files
2. **Confidence Tracking**: Track confidence and frequency for quality assessment
3. **Modular Design**: Independent service with clear API boundaries
4. **Audit Trail**: Keep full history of enrichment operations

## Performance

- Average enrichment time: ~40-50ms per assertion
- Ontology lookup: <5ms
- Reference resolution: ~10-15ms
- Definition extraction: ~10-15ms
- Auto-learning overhead: ~5-10ms

## Future Enhancements

- [ ] External ontology integration (EuroVoc, etc.)
- [ ] Machine learning for better pattern matching
- [ ] Relationship inference
- [ ] Cross-reference validation
- [ ] Definition quality scoring