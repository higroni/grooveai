# Module 10: Vector Store

**Port**: 8110
**Model**: BAAI/bge-m3
**Embedding Dimension**: 1024

## Overview

The Vector Store module converts text into dense vector representations (embeddings) using the BAAI/bge-m3 multilingual model. Supports **hybrid embedding strategy** with assertion-level and document-level embeddings, enriched with metadata for semantic search and vector DB storage.

## Features

- **Hybrid Embedding Strategy**:
  - Assertion-level embeddings (primary) with rich metadata
  - Document-level embeddings (secondary) for discovery
  - Generic chunk embeddings for flexibility
- **Rich Metadata Support**: Stores assertion type, entities, conditions, article numbers
- **Multilingual Support**: Handles Serbian Cyrillic and Latin text
- **High-Quality Embeddings**: Uses state-of-the-art BAAI/bge-m3 model
- **Batch Processing**: Efficient batch embedding generation
- **GPU Acceleration**: Automatic CUDA detection and usage
- **Database Persistence**: All embeddings stored in SQLite with metadata
- **REST API**: Easy integration with other modules
- **Pipeline Integration**: Receives classified assertions from Module 9

## Installation

```bash
# Install dependencies
pip install -r modules/vector_store/requirements.txt

# The model will be downloaded automatically on first run (~2GB)
```

## Running the Module

```bash
# Start the module
python -m modules.vector_store.main

# Module will start on http://localhost:8110
```

## API Endpoints

### 1. Generate Assertion Embeddings (Primary Use Case)

**POST** `/api/generate/assertions`

Generate embeddings for classified assertions with rich metadata. This is the **primary endpoint** for pipeline integration.

**Request:**
```json
{
  "assertions": [
    {
      "assertion_id": "assert_001",
      "text": "Poslodavac je duzan da zaposlenom isplacuje platu.",
      "assertion_type": "obligation",
      "confidence": 0.95,
      "entities": [{"type": "LEGAL_REF", "text": "Clan 104"}],
      "conditions": [{"type": "condition", "text": "ako je zaposlen"}],
      "article_number": "Clan 104",
      "source_document": "zakon_o_radu.pdf"
    }
  ]
}
```

**Response:**
```json
{
  "job_id": "emb_assertions_x1y2z3",
  "output": {
    "embeddings": [[0.123, -0.456, ...]],
    "model_name": "BAAI/bge-m3",
    "embedding_dimension": 1024,
    "text_count": 1,
    "assertion_count": 1,
    "total_processing_time_ms": 45.23,
    "metadata_list": [
      {
        "assertion_id": "assert_001",
        "assertion_type": "obligation",
        "confidence": 0.95,
        "article_number": "Clan 104",
        "source_document": "zakon_o_radu.pdf",
        "entities": [...],
        "conditions": [...],
        "entity_count": 1,
        "condition_count": 1
      }
    ]
  }
}
```

### 2. Generate Single Embedding with Metadata

**POST** `/api/generate`

Generate embedding for a single text with optional metadata.

**Request:**
```json
{
  "text": "Zakon o radu regulise prava i obaveze zaposlenih.",
  "metadata": {
    "source": "zakon_o_radu.pdf",
    "article": "Clan 1"
  },
  "embedding_type": "document"
}
```

**Response:**
```json
{
  "job_id": "emb_a1b2c3d4",
  "output": {
    "embeddings": [0.123, -0.456, 0.789, ...],
    "model_name": "BAAI/bge-m3",
    "embedding_dimension": 1024,
    "text_length": 50,
    "processing_time_ms": 45.23,
    "metadata": {
      "source": "zakon_o_radu.pdf",
      "article": "Clan 1"
    }
  }
}
```

### 3. Generate Batch Embeddings with Metadata

**POST** `/api/generate/batch`

Generate embeddings for multiple texts with optional metadata list.

**Request:**
```json
{
  "texts": [
    "Clan 1: Opste odredbe",
    "Clan 2: Definicije pojmova",
    "Clan 3: Primena zakona"
  ],
  "batch_size": 32,
  "metadata_list": [
    {"article": "Clan 1"},
    {"article": "Clan 2"},
    {"article": "Clan 3"}
  ],
  "embedding_type": "document"
}
```

**Response:**
```json
{
  "job_id": "emb_batch_x1y2z3",
  "output": {
    "embeddings": [[...], [...], [...]],
    "model_name": "BAAI/bge-m3",
    "embedding_dimension": 1024,
    "text_count": 3,
    "total_processing_time_ms": 120.45,
    "avg_time_per_text_ms": 40.15,
    "metadata_list": [...]
  }
}
```

### 4. Get Job Details

**GET** `/api/jobs/{job_id}`

Retrieve details of a specific embedding job.

**Response:**
```json
{
  "job_id": "emb_a1b2c3d4",
  "input_text": "Zakon o radu...",
  "embeddings": [0.123, -0.456, ...],
  "model_name": "BAAI/bge-m3",
  "embedding_dimension": 1024,
  "text_length": 50,
  "processing_time_ms": 45.23,
  "created_at": "2026-06-06T14:00:00"
}
```

### 5. List All Jobs

**GET** `/api/jobs?limit=10&offset=0`

List all embedding jobs with pagination.

### 6. Delete Job

**DELETE** `/api/jobs/{job_id}`

Delete a specific embedding job.

### 7. Get Model Info

**GET** `/model/info`

Get information about the loaded model.

**Response:**
```json
{
  "model_name": "BAAI/bge-m3",
  "embedding_dimension": 1024,
  "device": "cuda",
  "batch_size": 32,
  "max_seq_length": 8192
}
```

### 8. Health Check

**GET** `/health`

Check if the module is healthy and model is loaded.

## Usage Examples

### Python

```python
import requests

# Generate single embedding
response = requests.post(
    "http://localhost:8103/api/generate",
    json={"text": "Zakon o radu regulise prava i obaveze zaposlenih."}
)
result = response.json()
embeddings = result["output"]["embeddings"]
print(f"Generated {len(embeddings)}-dimensional embedding")

# Generate batch embeddings
texts = [
    "Clan 1: Opste odredbe",
    "Clan 2: Definicije pojmova",
    "Clan 3: Primena zakona"
]
response = requests.post(
    "http://localhost:8103/api/generate/batch",
    json={"texts": texts, "batch_size": 32}
)
result = response.json()
print(f"Generated {result['output']['text_count']} embeddings")
```

### cURL

```bash
# Generate embedding
curl -X POST http://localhost:8103/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Zakon o radu regulise prava i obaveze zaposlenih."}'

# Get job details
curl http://localhost:8103/api/jobs/emb_a1b2c3d4

# Get model info
curl http://localhost:8103/model/info
```

## Configuration

Module reads configuration from `config.yaml`:

```yaml
ai_models:
  embedding:
    model_name: "BAAI/bge-m3"
    dimensions: 1024
    device: "cuda"  # or "cpu"
    batch_size: 32

network:
  modules:
    vector_store:
      host: "0.0.0.0"
      port: 8103

database:
  modules:
    vector_store: "sqlite:///data/databases/vector_store.db"
```

## Model Information

### BAAI/bge-m3

- **Type**: Multilingual embedding model
- **Dimension**: 1024
- **Languages**: 100+ languages including Serbian
- **Max Sequence Length**: 8192 tokens
- **Size**: ~2GB
- **Performance**: ~40-50ms per text on GPU, ~200-300ms on CPU

### Device Selection

The module automatically detects and uses CUDA if available:
- **GPU (CUDA)**: ~40-50ms per embedding
- **CPU**: ~200-300ms per embedding

## Database Schema

```sql
CREATE TABLE embedding_jobs (
    id INTEGER PRIMARY KEY,
    job_id VARCHAR(100) UNIQUE NOT NULL,
    embedding_type VARCHAR(20) NOT NULL,  -- 'assertion', 'document', 'chunk'
    input_text TEXT NOT NULL,
    text_length INTEGER NOT NULL,
    model_name VARCHAR(200) NOT NULL,
    embedding_dimension INTEGER NOT NULL,
    embeddings TEXT NOT NULL,  -- JSON array
    processing_time_ms FLOAT NOT NULL,
    embedding_metadata TEXT,  -- JSON metadata
    assertion_type VARCHAR(50),  -- For quick filtering
    assertion_id VARCHAR(100),
    source_document VARCHAR(500),
    source_article VARCHAR(100),
    created_at DATETIME NOT NULL
);
```

**Indexes:**
- `job_id` (unique)
- `embedding_type`
- `assertion_type`
- `source_article`
- `assertion_id`

## Performance

- **Single Text**: 40-50ms (GPU) / 200-300ms (CPU)
- **Batch (32 texts)**: ~1.5s (GPU) / ~8s (CPU)
- **Memory**: ~4GB GPU VRAM / ~8GB RAM (CPU)

## Integration with Other Modules

### With Module 1 (File Reader) and Module 2 (Text Normalizer)

```python
import requests

# Step 1: Read PDF
response1 = requests.post(
    "http://localhost:8101/api/read",
    json={"file_path": "document.pdf", "file_type": "pdf"}
)
text = response1.json()["output"]["text"]

# Step 2: Normalize text
response2 = requests.post(
    "http://localhost:8102/api/normalize",
    json={"text": text}
)
normalized_text = response2.json()["output"]["normalized_text"]

# Step 3: Generate embeddings
response3 = requests.post(
    "http://localhost:8103/api/generate",
    json={"text": normalized_text}
)
embeddings = response3.json()["output"]["embeddings"]

print(f"Generated {len(embeddings)}-dimensional embedding from PDF")
```

## Testing

```bash
# Run tests
pytest modules/vector_store/tests -v

# Run with coverage
pytest modules/vector_store/tests --cov=modules.vector_store --cov-report=html
```

## Troubleshooting

### Model Download Issues

If model download fails:
```bash
# Manually download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
```

### CUDA Out of Memory

Reduce batch size in config.yaml:
```yaml
ai_models:
  embedding:
    batch_size: 16  # Reduce from 32
```

### Slow Performance

- Check if CUDA is being used: `GET /model/info`
- Ensure GPU drivers are installed
- Consider using CPU if GPU is unavailable

## Dependencies

- `sentence-transformers>=2.2.2` - Embedding model
- `torch>=2.0.0` - PyTorch for model inference
- `fastapi>=0.104.0` - Web framework
- `sqlalchemy>=2.0.0` - Database ORM

## Future Enhancements

- [ ] Support for additional embedding models
- [ ] Embedding caching for duplicate texts
- [ ] Quantization for faster inference
- [ ] Streaming API for large batches
- [ ] Embedding similarity search endpoint
