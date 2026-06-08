# Document Export JSON Schema

## Overview

The `export_document_to_json.py` script exports complete pipeline results for a single document from the unified database into a structured JSON file suitable for vector database import.

---

## Usage

### Basic Usage
```bash
# Export document with default output name
python export_document_to_json.py "radni_odnosi_0001_000001.pdf"
# Output: radni_odnosi_0001_000001_export.json

# Export with custom output name
python export_document_to_json.py "radni_odnosi_0001_000001.pdf" --output doc1.json

# Export from different database
python export_document_to_json.py "document.pdf" --db custom.db

# Export compact JSON (no pretty printing)
python export_document_to_json.py "document.pdf" --compact
```

### Command Line Options
```
positional arguments:
  document_name         Document name or path (e.g., 'radni_odnosi_0001_000001.pdf')

optional arguments:
  --output, -o          Output JSON file path (default: <document_name>_export.json)
  --db                  Database file path (default: unified_legal_pipeline.db)
  --compact             Output compact JSON (no pretty printing)
```

---

## JSON Structure

### Top-Level Schema

```json
{
  "metadata": {
    "job_id": "string (UUID)",
    "file_path": "string",
    "file_name": "string",
    "file_size_bytes": "integer",
    "page_count": "integer",
    "processing_time_ms": "float",
    "processed_at": "string (ISO 8601 timestamp)",
    "export_timestamp": "string (ISO 8601 timestamp)",
    "exporter_version": "string"
  },
  "legal_structure": {
    "units": [
      {
        "legal_unit_id": "string (UUID)",
        "type": "string (article|paragraph|section|chapter)",
        "number": "string",
        "title": "string",
        "content": "string",
        "hierarchy_level": "integer",
        "parent_id": "string (UUID) | null"
      }
    ],
    "total_units": "integer"
  },
  "assertions": {
    "items": [
      {
        "assertion_id": "string (UUID)",
        "legal_unit_id": "string (UUID)",
        "text": "string",
        "confidence": "float (0.0-1.0)",
        "sentence_index": "integer",
        "start_char": "integer",
        "end_char": "integer",
        "extracted_at": "string (ISO 8601 timestamp)",
        "entities": [
          {
            "text": "string",
            "type": "string (PERSON|ORG|LOC|DATE|MONEY|etc.)",
            "start_pos": "integer",
            "end_pos": "integer",
            "confidence": "float (0.0-1.0)",
            "recognized_at": "string (ISO 8601 timestamp)"
          }
        ],
        "conditions": [
          {
            "text": "string",
            "type": "string (temporal|conditional|exception|etc.)",
            "trigger_words": "string",
            "confidence": "float (0.0-1.0)",
            "extracted_at": "string (ISO 8601 timestamp)"
          }
        ],
        "classification": {
          "primary_category": "string",
          "confidence": "float (0.0-1.0)",
          "all_categories": [
            {
              "category": "string",
              "confidence": "float (0.0-1.0)"
            }
          ],
          "classified_at": "string (ISO 8601 timestamp)"
        },
        "enrichment": {
          "enriched_data": {
            "related_laws": ["string"],
            "precedents": ["string"],
            "interpretations": ["string"],
            "cross_references": ["string"]
          },
          "knowledge_sources": ["string"],
          "confidence": "float (0.0-1.0)",
          "enriched_at": "string (ISO 8601 timestamp)"
        }
      }
    ],
    "total_assertions": "integer",
    "total_entities": "integer",
    "total_conditions": "integer",
    "classified_count": "integer",
    "enriched_count": "integer"
  },
  "statistics": {
    "legal_units": "integer",
    "assertions": "integer",
    "entities": "integer",
    "conditions": "integer",
    "classifications": "integer",
    "enrichments": "integer"
  }
}
```

---

## Example Output

### Small Document Example

```json
{
  "metadata": {
    "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "file_path": "D:/POSAO/OllamaProjects/GROOVE.AI/DOCUMENTS/DEV/perftest/radni_odnosi_0008_000008.pdf",
    "file_name": "radni_odnosi_0008_000008.pdf",
    "file_size_bytes": 245678,
    "page_count": 3,
    "processing_time_ms": 2070.45,
    "processed_at": "2026-06-08T01:07:41.719455",
    "export_timestamp": "2026-06-08T07:15:00.123456Z",
    "exporter_version": "1.0.0"
  },
  "legal_structure": {
    "units": [
      {
        "legal_unit_id": "d691a249-33e5-5c66-9cab-736944ecb046",
        "type": "article",
        "number": "1",
        "title": "Osnovna odredba",
        "content": "Ovim zakonom uređuju se radni odnosi zaposlenih...",
        "hierarchy_level": 1,
        "parent_id": null
      },
      {
        "legal_unit_id": "e792b350-44f6-6d77-0dbc-847055fdc157",
        "type": "article",
        "number": "2",
        "title": "Definicije",
        "content": "U smislu ovog zakona, pojedini izrazi imaju sledeće značenje...",
        "hierarchy_level": 1,
        "parent_id": null
      }
    ],
    "total_units": 2
  },
  "assertions": {
    "items": [
      {
        "assertion_id": "a5a71590-4a49-4321-8abe-80754d3c653c",
        "legal_unit_id": "d691a249-33e5-5c66-9cab-736944ecb046",
        "text": "Zaposleni ima pravo na godišnji odmor u trajanju od najmanje 20 radnih dana.",
        "confidence": 0.95,
        "sentence_index": 0,
        "start_char": 0,
        "end_char": 78,
        "extracted_at": "2026-06-08T01:07:43.719455",
        "entities": [
          {
            "text": "Zaposleni",
            "type": "PERSON",
            "start_pos": 0,
            "end_pos": 9,
            "confidence": 0.92,
            "recognized_at": "2026-06-08T01:07:45.123456"
          },
          {
            "text": "20 radnih dana",
            "type": "DURATION",
            "start_pos": 64,
            "end_pos": 78,
            "confidence": 0.98,
            "recognized_at": "2026-06-08T01:07:45.123456"
          }
        ],
        "conditions": [
          {
            "text": "u trajanju od najmanje 20 radnih dana",
            "type": "quantitative",
            "trigger_words": "najmanje",
            "confidence": 0.89,
            "extracted_at": "2026-06-08T01:07:47.234567"
          }
        ],
        "classification": {
          "primary_category": "labor_rights",
          "confidence": 0.94,
          "all_categories": [
            {
              "category": "labor_rights",
              "confidence": 0.94
            },
            {
              "category": "vacation_leave",
              "confidence": 0.87
            }
          ],
          "classified_at": "2026-06-08T01:07:49.345678"
        },
        "enrichment": {
          "enriched_data": {
            "related_laws": [
              "Zakon o radu, član 68",
              "Kolektivni ugovor, član 15"
            ],
            "precedents": [
              "Presuda Vrhovnog suda Rev. 1234/2020"
            ],
            "interpretations": [
              "Godišnji odmor se računa u kalendarskim danima, ne radnim danima"
            ],
            "cross_references": [
              "Član 3, stav 2 ovog zakona"
            ]
          },
          "knowledge_sources": [
            "legal_database",
            "case_law",
            "doctrine"
          ],
          "confidence": 0.91,
          "enriched_at": "2026-06-08T01:07:51.456789"
        }
      }
    ],
    "total_assertions": 9,
    "total_entities": 4,
    "total_conditions": 5,
    "classified_count": 9,
    "enriched_count": 9
  },
  "statistics": {
    "legal_units": 2,
    "assertions": 9,
    "entities": 4,
    "conditions": 5,
    "classifications": 9,
    "enrichments": 9
  }
}
```

---

## Field Descriptions

### Metadata Section

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | UUID | Unique identifier for the processing job |
| `file_path` | string | Full path to the source document |
| `file_name` | string | Name of the source document |
| `file_size_bytes` | integer | Size of the source file in bytes |
| `page_count` | integer | Number of pages in the document |
| `processing_time_ms` | float | Total processing time in milliseconds |
| `processed_at` | ISO 8601 | Timestamp when document was processed |
| `export_timestamp` | ISO 8601 | Timestamp when export was created |
| `exporter_version` | string | Version of the export script |

### Legal Structure Section

| Field | Type | Description |
|-------|------|-------------|
| `legal_unit_id` | UUID | Unique identifier for the legal unit |
| `type` | string | Type of legal unit (article, paragraph, section, chapter) |
| `number` | string | Number/identifier of the unit (e.g., "1", "2a", "III") |
| `title` | string | Title or heading of the unit |
| `content` | string | Full text content of the unit |
| `hierarchy_level` | integer | Nesting level (1 = top level, 2 = nested, etc.) |
| `parent_id` | UUID/null | ID of parent unit (null for top-level units) |

### Assertions Section

| Field | Type | Description |
|-------|------|-------------|
| `assertion_id` | UUID | Unique identifier for the assertion |
| `legal_unit_id` | UUID | ID of the legal unit containing this assertion |
| `text` | string | Full text of the assertion |
| `confidence` | float | Confidence score (0.0-1.0) |
| `sentence_index` | integer | Index of sentence within legal unit |
| `start_char` | integer | Starting character position |
| `end_char` | integer | Ending character position |
| `extracted_at` | ISO 8601 | Timestamp when assertion was extracted |

### Entities (within assertions)

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Text of the recognized entity |
| `type` | string | Entity type (PERSON, ORG, LOC, DATE, MONEY, etc.) |
| `start_pos` | integer | Starting position within assertion text |
| `end_pos` | integer | Ending position within assertion text |
| `confidence` | float | Recognition confidence (0.0-1.0) |
| `recognized_at` | ISO 8601 | Timestamp when entity was recognized |

### Conditions (within assertions)

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Text of the condition |
| `type` | string | Condition type (temporal, conditional, exception, etc.) |
| `trigger_words` | string | Words that triggered condition detection |
| `confidence` | float | Extraction confidence (0.0-1.0) |
| `extracted_at` | ISO 8601 | Timestamp when condition was extracted |

### Classification (within assertions)

| Field | Type | Description |
|-------|------|-------------|
| `primary_category` | string | Main classification category |
| `confidence` | float | Classification confidence (0.0-1.0) |
| `all_categories` | array | All detected categories with confidences |
| `classified_at` | ISO 8601 | Timestamp when classification was performed |

### Enrichment (within assertions)

| Field | Type | Description |
|-------|------|-------------|
| `enriched_data` | object | Structured enrichment data |
| `knowledge_sources` | array | Sources used for enrichment |
| `confidence` | float | Enrichment confidence (0.0-1.0) |
| `enriched_at` | ISO 8601 | Timestamp when enrichment was performed |

---

## Vector Database Import

### Recommended Chunking Strategy

For vector database import, consider these chunking strategies:

#### Strategy 1: Assertion-Level Chunks
```python
# Each assertion becomes a separate vector
for assertion in document["assertions"]["items"]:
    chunk = {
        "id": assertion["assertion_id"],
        "text": assertion["text"],
        "metadata": {
            "document": document["metadata"]["file_name"],
            "legal_unit": assertion["legal_unit_id"],
            "entities": [e["text"] for e in assertion["entities"]],
            "conditions": [c["type"] for c in assertion["conditions"]],
            "category": assertion["classification"]["primary_category"],
            "confidence": assertion["confidence"]
        }
    }
    # Insert into vector database
```

#### Strategy 2: Legal Unit-Level Chunks
```python
# Each legal unit becomes a vector with all its assertions
for unit in document["legal_structure"]["units"]:
    # Find all assertions for this unit
    unit_assertions = [
        a for a in document["assertions"]["items"]
        if a["legal_unit_id"] == unit["legal_unit_id"]
    ]
    
    chunk = {
        "id": unit["legal_unit_id"],
        "text": unit["content"],
        "metadata": {
            "document": document["metadata"]["file_name"],
            "unit_type": unit["type"],
            "unit_number": unit["number"],
            "title": unit["title"],
            "assertions_count": len(unit_assertions),
            "entities": list(set(
                e["text"] 
                for a in unit_assertions 
                for e in a["entities"]
            ))
        }
    }
    # Insert into vector database
```

#### Strategy 3: Hierarchical Chunks
```python
# Create multiple granularity levels
chunks = []

# Level 1: Document-level
chunks.append({
    "id": f"{document['metadata']['job_id']}_doc",
    "text": " ".join(u["content"] for u in document["legal_structure"]["units"]),
    "metadata": {
        "level": "document",
        "file_name": document["metadata"]["file_name"],
        "total_assertions": document["statistics"]["assertions"]
    }
})

# Level 2: Legal unit-level
for unit in document["legal_structure"]["units"]:
    chunks.append({
        "id": f"{unit['legal_unit_id']}_unit",
        "text": unit["content"],
        "metadata": {
            "level": "legal_unit",
            "parent_doc": document["metadata"]["job_id"],
            "unit_type": unit["type"]
        }
    })

# Level 3: Assertion-level
for assertion in document["assertions"]["items"]:
    chunks.append({
        "id": f"{assertion['assertion_id']}_assertion",
        "text": assertion["text"],
        "metadata": {
            "level": "assertion",
            "parent_unit": assertion["legal_unit_id"],
            "category": assertion["classification"]["primary_category"]
        }
    })
```

---

## Integration Examples

### Pinecone
```python
import pinecone
from sentence_transformers import SentenceTransformer

# Initialize
pinecone.init(api_key="your-api-key")
index = pinecone.Index("legal-documents")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load exported document
with open("document_export.json") as f:
    doc = json.load(f)

# Create vectors for each assertion
vectors = []
for assertion in doc["assertions"]["items"]:
    # Generate embedding
    embedding = model.encode(assertion["text"])
    
    # Prepare metadata
    metadata = {
        "document": doc["metadata"]["file_name"],
        "text": assertion["text"],
        "entities": [e["text"] for e in assertion["entities"]],
        "category": assertion["classification"]["primary_category"],
        "confidence": assertion["confidence"]
    }
    
    vectors.append((assertion["assertion_id"], embedding.tolist(), metadata))

# Upsert to Pinecone
index.upsert(vectors=vectors)
```

### Weaviate
```python
import weaviate

# Initialize client
client = weaviate.Client("http://localhost:8080")

# Load exported document
with open("document_export.json") as f:
    doc = json.load(f)

# Create schema
schema = {
    "class": "LegalAssertion",
    "properties": [
        {"name": "text", "dataType": ["text"]},
        {"name": "document", "dataType": ["string"]},
        {"name": "category", "dataType": ["string"]},
        {"name": "confidence", "dataType": ["number"]},
        {"name": "entities", "dataType": ["string[]"]}
    ]
}
client.schema.create_class(schema)

# Import assertions
for assertion in doc["assertions"]["items"]:
    data_object = {
        "text": assertion["text"],
        "document": doc["metadata"]["file_name"],
        "category": assertion["classification"]["primary_category"],
        "confidence": assertion["confidence"],
        "entities": [e["text"] for e in assertion["entities"]]
    }
    
    client.data_object.create(
        data_object=data_object,
        class_name="LegalAssertion",
        uuid=assertion["assertion_id"]
    )
```

### Qdrant
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Initialize
client = QdrantClient("localhost", port=6333)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create collection
client.create_collection(
    collection_name="legal_assertions",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Load exported document
with open("document_export.json") as f:
    doc = json.load(f)

# Prepare points
points = []
for assertion in doc["assertions"]["items"]:
    embedding = model.encode(assertion["text"])
    
    point = PointStruct(
        id=assertion["assertion_id"],
        vector=embedding.tolist(),
        payload={
            "text": assertion["text"],
            "document": doc["metadata"]["file_name"],
            "category": assertion["classification"]["primary_category"],
            "entities": [e["text"] for e in assertion["entities"]],
            "confidence": assertion["confidence"]
        }
    )
    points.append(point)

# Upload to Qdrant
client.upsert(collection_name="legal_assertions", points=points)
```

---

## Performance Considerations

### File Size
- Small documents (1-10 assertions): ~10-50 KB
- Medium documents (10-100 assertions): ~50-500 KB
- Large documents (100-1000 assertions): ~500 KB - 5 MB
- Very large documents (1000+ assertions): 5+ MB

### Export Time
- Database query: ~100-500ms
- JSON serialization: ~50-200ms
- File write: ~10-50ms
- **Total: ~200-750ms per document**

### Batch Export
For exporting multiple documents, consider creating a batch script:

```python
# batch_export.py
import os
from export_document_to_json import DocumentExporter

exporter = DocumentExporter()
exporter.connect()

documents = [
    "doc1.pdf",
    "doc2.pdf",
    "doc3.pdf"
]

for doc in documents:
    try:
        output = f"exports/{doc.replace('.pdf', '.json')}"
        exporter.export_to_file(doc, output)
        print(f"✅ Exported: {doc}")
    except Exception as e:
        print(f"❌ Failed: {doc} - {e}")

exporter.close()
```

---

## Troubleshooting

### Document Not Found
```
❌ Error: Document not found: document.pdf
```
**Solution**: Check that the document name matches exactly (including extension)

### Database Not Found
```
❌ Error: Database not found: unified_legal_pipeline.db
```
**Solution**: Specify correct database path with `--db` option

### Empty Export
```
✅ Successfully exported document to: output.json
Document Statistics:
  - Legal Units: 0
  - Assertions: 0
```
**Solution**: Document may not have been processed through pipeline yet

### Large File Warning
If export file is >10MB, consider:
1. Exporting only specific sections
2. Using compact JSON format (`--compact`)
3. Compressing output file (gzip)

---

## Future Enhancements

### Planned Features
- [ ] Export multiple documents in single JSON array
- [ ] Filter by date range or category
- [ ] Export to other formats (CSV, Parquet, Avro)
- [ ] Direct vector database upload
- [ ] Incremental export (only new/changed data)
- [ ] Compression support (gzip, bz2)

---

**Version**: 1.0.0  
**Last Updated**: 2026-06-08  
**Script**: [`export_document_to_json.py`](../export_document_to_json.py)