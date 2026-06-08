# Qdrant Loader Module

This module handles loading legal document data from JSON exports into Qdrant vector database for semantic search and conflict detection.

## Overview

The Qdrant Loader creates and manages three specialized collections:

1. **legal_units** - Individual legal units (articles, paragraphs, items, etc.)
2. **normative_content** - Normative assertions extracted from legal units
3. **document_metadata** - Document-level metadata and statistics

Each collection stores both structured data (as payload) and semantic embeddings (as vectors) for efficient similarity search.

## Architecture

### Collections Design

#### 1. Legal Units Collection
Stores individual legal units with full hierarchy and content:
- **Vector**: Embedding of latinized content
- **Payload**: Unit metadata, hierarchy, content, document info

#### 2. Normative Content Collection
Stores extracted normative assertions (obligations, prohibitions, rights):
- **Vector**: Embedding of latinized normative text
- **Payload**: Normative type, text, conditions, source unit info

#### 3. Document Metadata Collection
Stores document-level information and statistics:
- **Vector**: Embedding of document title
- **Payload**: Document info, statistics, hierarchy stats

### Embedding Model

Uses `paraphrase-multilingual-mpnet-base-v2` from sentence-transformers:
- Supports 50+ languages including Serbian
- 768-dimensional vectors
- Optimized for semantic similarity
- Good balance between quality and speed

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Setup

```python
from pathlib import Path
from modules.qdrant_loader import QdrantLoaderService, LoaderConfig

# Configure loader
config = LoaderConfig(
    qdrant_url="http://localhost:6333",
    recreate_collections=True  # Set to False to append to existing
)

# Initialize service
loader = QdrantLoaderService(config)

# Setup collections (creates if not exist)
loader.setup_collections()
```

### Load Single Document

```python
# Load one JSON export
json_path = Path("test_data/json_output/radni_odnosi_0001_000001_export.json")
loader.load_document_from_json(json_path)
```

### Batch Load

```python
# Load all JSON files from directory
json_dir = Path("test_data/json_output")
stats = loader.load_batch(json_dir)

print(f"Documents processed: {stats.documents_processed}")
print(f"Legal units loaded: {stats.legal_units_loaded}")
print(f"Normative content loaded: {stats.normative_content_loaded}")
print(f"Duration: {stats.duration_seconds:.2f}s")
```

### Check Collection Status

```python
# Get info about all collections
info = loader.get_all_collections_info()

for collection_name, collection_info in info.items():
    print(f"\n{collection_name}:")
    print(f"  Points: {collection_info['points_count']}")
    print(f"  Vectors: {collection_info['vectors_count']}")
    print(f"  Status: {collection_info['status']}")
```

## Configuration Options

### LoaderConfig Parameters

- `qdrant_url` (str): Qdrant server URL (default: "http://localhost:6333")
- `qdrant_api_key` (str, optional): API key for Qdrant Cloud
- `legal_units_collection` (str): Collection name for legal units (default: "legal_units")
- `normative_collection` (str): Collection name for normative content (default: "normative_content")
- `metadata_collection` (str): Collection name for metadata (default: "document_metadata")
- `vector_size` (int): Embedding vector size (default: 768)
- `distance_metric` (str): Distance metric - "Cosine" or "Euclid" (default: "Cosine")
- `embedding_model` (str): Sentence transformer model (default: "paraphrase-multilingual-mpnet-base-v2")
- `batch_size` (int): Batch size for uploads (default: 100)
- `recreate_collections` (bool): Whether to recreate collections (default: False)

## Data Flow

```
JSON Export Files
    ↓
QdrantLoaderService
    ↓
Parse JSON → Extract Units/Normative/Metadata
    ↓
Generate Embeddings (sentence-transformers)
    ↓
Create PointStruct (vector + payload)
    ↓
Upload to Qdrant (batched)
    ↓
Three Collections Ready for Search
```

## Performance

- **Embedding Generation**: ~50-100 units/second (CPU)
- **Upload Speed**: ~1000 points/second (batched)
- **Memory Usage**: ~2GB for model + ~100MB per 1000 documents
- **Recommended**: Use GPU for faster embedding generation

## Qdrant Setup

### Local (Docker)

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Cloud

Sign up at https://cloud.qdrant.io and use API key:

```python
config = LoaderConfig(
    qdrant_url="https://your-cluster.qdrant.io",
    qdrant_api_key="your-api-key"
)
```

## Error Handling

The loader includes comprehensive error handling:
- Failed documents are logged but don't stop batch processing
- Statistics track errors with detailed messages
- Partial failures are supported (some units may load even if others fail)

## Testing

See `test_qdrant_loader.py` for examples:

```bash
python test_qdrant_loader.py
```

## Next Steps

After loading data into Qdrant:
1. Use for semantic search in conflict detection
2. Query similar legal units
3. Find related normative content
4. Build conflict detection system on top

## Dependencies

- `qdrant-client`: Qdrant Python client
- `sentence-transformers`: Embedding generation
- `pydantic`: Data validation
- `torch`: PyTorch for transformers

## Notes

- First run downloads the embedding model (~400MB)
- Embeddings are generated from **latinized** text for consistency
- Collections use Cosine distance for semantic similarity
- Indexing starts automatically after 10,000 points