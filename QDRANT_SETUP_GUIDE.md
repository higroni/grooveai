# Qdrant Setup Guide

Quick guide for setting up Qdrant vector database and loading legal documents.

## Prerequisites

- Docker Desktop installed and running
- Python 3.9+ with pip
- Processed JSON exports in `test_data/json_output/`

## Step 1: Install Dependencies

```bash
pip install -r modules/qdrant_loader/requirements.txt
```

This installs:
- `qdrant-client` - Qdrant Python client
- `sentence-transformers` - For generating embeddings
- `pydantic` - Data validation
- `torch` - PyTorch for transformers

**Note**: First run will download the embedding model (~400MB).

## Step 2: Start Qdrant

### Option A: Using Docker Compose (Recommended)

```bash
# Start Qdrant
docker-compose -f docker-compose.qdrant.yml up -d

# Check status
docker-compose -f docker-compose.qdrant.yml ps

# View logs
docker-compose -f docker-compose.qdrant.yml logs -f
```

### Option B: Using Batch Script (Windows)

```bash
setup_qdrant.bat
```

### Option C: Manual Docker Command

```bash
docker run -p 6333:6333 -p 6334:6334 -v ./qdrant_storage:/qdrant/storage qdrant/qdrant
```

## Step 3: Verify Qdrant is Running

Open browser and navigate to:
- **Dashboard**: http://localhost:6333/dashboard
- **Health Check**: http://localhost:6333/health

Or use curl:
```bash
curl http://localhost:6333/health
```

## Step 4: Load Data into Qdrant

### Load All Documents

```bash
python load_data_to_qdrant.py
```

### Load with Options

```bash
# Recreate collections (deletes existing data)
python load_data_to_qdrant.py --recreate

# Load only first 10 documents (for testing)
python load_data_to_qdrant.py --limit 10

# Custom JSON directory
python load_data_to_qdrant.py --json-dir path/to/json/files

# Custom Qdrant URL (for cloud)
python load_data_to_qdrant.py --qdrant-url https://your-cluster.qdrant.io
```

### Expected Output

```
========================================
GROOVE.AI - Load Data to Qdrant
========================================
Found 234 JSON files

Configuration:
  Qdrant URL: http://localhost:6333
  Recreate collections: False
  Batch size: 100
  Embedding model: paraphrase-multilingual-mpnet-base-v2
  Vector size: 768

Connected to Qdrant at http://localhost:6333

Initializing Qdrant Loader Service...
Loading embedding model: paraphrase-multilingual-mpnet-base-v2

Setting up collections...
Creating collection: legal_units
Creating collection: normative_content
Creating collection: document_metadata

========================================
Loading Documents
========================================
Loading document from: radni_odnosi_0001_000001_export.json
Loaded 45 legal units
Loaded 23 normative assertions
...

========================================
LOADING COMPLETE
========================================

Statistics:
  Documents processed: 234
  Legal units loaded: 10,523
  Normative content loaded: 5,847
  Metadata loaded: 234
  Duration: 245.67s
  Errors: 0

Averages per Document:
  Legal units: 45.0
  Normative content: 25.0
  Processing time: 1.05s

========================================
Collection Information
========================================

legal_units:
  Points: 10,523
  Vectors: 10,523
  Indexed: 10,523
  Status: green

normative_content:
  Points: 5,847
  Vectors: 5,847
  Indexed: 5,847
  Status: green

document_metadata:
  Points: 234
  Vectors: 234
  Indexed: 234
  Status: green

========================================
SUCCESS - Data loaded into Qdrant
========================================

Qdrant Dashboard: http://localhost:6333/dashboard
Next step: Run conflict detection tests
```

## Step 5: Verify Data in Qdrant

### Using Dashboard

1. Open http://localhost:6333/dashboard
2. Click on "Collections"
3. You should see three collections:
   - `legal_units`
   - `normative_content`
   - `document_metadata`
4. Click on any collection to see points and vectors

### Using Python

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

# List collections
collections = client.get_collections()
print(collections)

# Get collection info
info = client.get_collection("legal_units")
print(f"Points: {info.points_count}")
print(f"Vectors: {info.vectors_count}")

# Search example
results = client.search(
    collection_name="legal_units",
    query_text="radni odnos",
    limit=5
)
for result in results:
    print(f"Score: {result.score}")
    print(f"Content: {result.payload['content'][:100]}...")
```

## Collections Structure

### 1. legal_units
- **Purpose**: Individual legal units (articles, paragraphs, items)
- **Vector**: Embedding of latinized content
- **Payload**: Full unit data (hierarchy, content, metadata)
- **Use Case**: Find similar legal units, search by content

### 2. normative_content
- **Purpose**: Extracted normative assertions
- **Vector**: Embedding of latinized normative text
- **Payload**: Normative type, text, conditions, source info
- **Use Case**: Find conflicting obligations/prohibitions/rights

### 3. document_metadata
- **Purpose**: Document-level information
- **Vector**: Embedding of document title
- **Payload**: Statistics, hierarchy info, processing metadata
- **Use Case**: Find related documents, filter by document type

## Troubleshooting

### Qdrant Not Starting

```bash
# Check if port is already in use
netstat -ano | findstr :6333

# Stop existing Qdrant
docker-compose -f docker-compose.qdrant.yml down

# Remove old containers
docker rm -f groove-ai-qdrant

# Start fresh
docker-compose -f docker-compose.qdrant.yml up -d
```

### Connection Refused

- Ensure Docker Desktop is running
- Wait 10-15 seconds after starting Qdrant
- Check firewall settings

### Out of Memory

- Reduce batch size: `--batch-size 50`
- Load fewer documents: `--limit 50`
- Increase Docker memory limit in Docker Desktop settings

### Slow Loading

- First run downloads embedding model (~400MB)
- Subsequent runs are faster
- Use GPU for faster embedding generation
- Increase batch size: `--batch-size 200`

## Stopping Qdrant

```bash
# Stop but keep data
docker-compose -f docker-compose.qdrant.yml stop

# Stop and remove containers (keeps data in volume)
docker-compose -f docker-compose.qdrant.yml down

# Stop and remove everything including data
docker-compose -f docker-compose.qdrant.yml down -v
```

## Next Steps

After loading data:
1. Test semantic search queries
2. Build conflict detection module
3. Create UI for conflict detection
4. Fine-tune search parameters

## Resources

- Qdrant Documentation: https://qdrant.tech/documentation/
- Sentence Transformers: https://www.sbert.net/
- Qdrant Python Client: https://github.com/qdrant/qdrant-client