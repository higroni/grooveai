# Module 4: Embedding Generator

**Port**: 8104
**Model**: BAAI/bge-m3
**Embedding Dimension**: 1024

## Overview

The Embedding Generator module converts text into dense vector representations (embeddings) using the BAAI/bge-m3 multilingual model. These embeddings are used for semantic search, similarity comparison, and other NLP tasks.

## Features

- **Multilingual Support**: Handles Serbian Cyrillic and Latin text
- **High-Quality Embeddings**: Uses state-of-the-art BAAI/bge-m3 model
- **Batch Processing**: Efficient batch embedding generation
- **GPU Acceleration**: Automatic CUDA detection and usage
- **Database Persistence**: All embeddings stored in SQLite
- **REST API**: Easy integration with other modules

## Installation

```bash
# Install dependencies
pip install -r modules/embedding_generator/requirements.txt

# The model will be downloaded automatically on first run (~2GB)
```

## Running the Module

```bash
# Start the module
python -m modules.embedding_generator.main

# Module will start on http://localhost:8104
```

## API Endpoints

### 1. Generate Single Embedding

**POST** `/api/generate`

Generate embedding for a single text.

**Request:**
```json
{
  "text": "Zakon o radu regulise prava i obaveze zaposlenih."
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
    "processing_time_ms": 45.23
  }
}
```

### 2. Generate Batch Embeddings

**POST** `/api/generate/batch`

Generate embeddings for multiple texts efficiently.

**Request:**
```json
{
  "texts": [
    "Clan 1: Opste odredbe",
    "Clan 2: Definicije pojmova",
    "Clan 3: Primena zakona"
  ],
  "batch_size": 32
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
    "avg_time_per_text_ms": 40.15
  }
}
```

### 3. Get Job Details

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

### 4. List All Jobs

**GET** `/api/jobs?limit=10&offset=0`

List all embedding jobs with pagination.

### 5. Delete Job

**DELETE** `/api/jobs/{job_id}`

Delete a specific embedding job.

### 6. Get Model Info

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

### 7. Health Check

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
    embedding_generator:
      host: "0.0.0.0"
      port: 8103

database:
  modules:
    embedding_generator: "sqlite:///data/databases/embedding_generator.db"
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
    input_text TEXT NOT NULL,
    text_length INTEGER NOT NULL,
    model_name VARCHAR(200) NOT NULL,
    embedding_dimension INTEGER NOT NULL,
    embeddings TEXT NOT NULL,  -- JSON array
    processing_time_ms FLOAT NOT NULL,
    created_at DATETIME NOT NULL
);
```

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
pytest modules/embedding_generator/tests -v

# Run with coverage
pytest modules/embedding_generator/tests --cov=modules.embedding_generator --cov-report=html
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