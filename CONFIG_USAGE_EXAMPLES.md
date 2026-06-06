# GROOVE.AI - Configuration Usage Examples

Ovaj dokument pokazuje kako svi moduli koriste centralizovani config sistem.

---

## 📋 Struktura

```
GROOVE.AI/
├── config.yaml                    # Master config file
├── shared/
│   └── config_loader.py          # Shared library
├── orchestrator/
│   └── main.py                   # Uses config
├── modules/
│   ├── file_reader/
│   │   └── main.py               # Uses config
│   ├── text_normalizer/
│   │   └── main.py               # Uses config
│   └── ...
```

---

## 🔧 Kako Koristiti Config Loader

### 1. Import u Modulu

```python
# U bilo kom modulu
from shared.config_loader import config

# Sada možeš koristiti config
project_name = config.get_project_name()
port = config.get_module_port("file_reader")
db_url = config.get_database_url("file_reader")
```

---

## 📦 Primer: File Reader Module

**modules/file_reader/main.py**:

```python
from fastapi import FastAPI
from shared.config_loader import config
import logging

# Get configuration
MODULE_NAME = "file_reader"
HOST = config.get_module_host(MODULE_NAME)
PORT = config.get_module_port(MODULE_NAME)
DB_URL = config.get_database_url(MODULE_NAME)
LOG_FILE = config.get_log_file(MODULE_NAME)

# Setup logging
logging.basicConfig(
    level=config.get_log_level(),
    format=config.get_log_format(),
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(MODULE_NAME)

# Create FastAPI app
app = FastAPI(
    title=f"{config.get_project_name()} - File Reader",
    version=config.get_version()
)

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "module": MODULE_NAME,
        "version": config.get_version()
    }

@app.post("/api/read")
def read_file(file_path: str):
    logger.info(f"Reading file: {file_path}")
    # ... processing logic
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {MODULE_NAME} on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
```

---

## 🎯 Primer: Orchestrator

**orchestrator/main.py**:

```python
from fastapi import FastAPI
from shared.config_loader import config
import httpx
import logging

# Get configuration
HOST = config.get_orchestrator_host()
PORT = config.get_orchestrator_port()
LOG_FILE = config.get_log_file("orchestrator")

# Setup logging
logging.basicConfig(
    level=config.get_log_level(),
    format=config.get_log_format(),
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("orchestrator")

# Create FastAPI app
app = FastAPI(
    title=f"{config.get_project_name()} - Orchestrator",
    version=config.get_version()
)

@app.post("/api/orchestrator/workflows/import-corpus")
async def import_corpus(corpus_id: str, file_paths: list):
    """Import corpus workflow."""
    
    # Get workflow steps from config
    steps = config.get_workflow_steps("import_corpus")
    
    logger.info(f"Starting import corpus workflow with {len(steps)} steps")
    
    results = []
    
    for step_name in steps:
        # Get module URL from config
        module_url = config.get_module_url(step_name)
        
        logger.info(f"Executing step: {step_name} at {module_url}")
        
        # Call module
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{module_url}/api/process",
                json={"data": "..."},
                timeout=config.get("performance.timeouts.http_request", 30)
            )
            results.append(response.json())
    
    return {
        "workflow_id": "uuid-123",
        "status": "completed",
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Orchestrator on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
```

---

## 🗄️ Primer: Database Connection

**modules/file_reader/database.py**:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.config_loader import config

MODULE_NAME = "file_reader"

# Get database URL from config
DATABASE_URL = config.get_database_url(MODULE_NAME)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=config.get("database.echo", False),
    pool_size=config.get("database.pool_size", 5),
    max_overflow=config.get("database.max_overflow", 10)
)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 📊 Primer: AI Model Configuration

**modules/embedding_generator/service.py**:

```python
from sentence_transformers import SentenceTransformer
from shared.config_loader import config
import torch

class EmbeddingService:
    def __init__(self):
        # Get model config
        self.model_name = config.get_embedding_model()
        self.device = config.get_embedding_device()
        self.batch_size = config.get_embedding_batch_size()
        self.dimensions = config.get_embedding_dimensions()
        
        # Load model
        self.model = SentenceTransformer(self.model_name)
        self.model.to(self.device)
        
        print(f"✓ Loaded {self.model_name} on {self.device}")
    
    def generate_embeddings(self, texts: list) -> list:
        """Generate embeddings for texts."""
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            device=self.device,
            normalize_embeddings=config.get("ai_models.embedding.normalize", True)
        )
        return embeddings.tolist()
```

---

## 🔍 Primer: Hybrid Search

**modules/hybrid_search/service.py**:

```python
from shared.config_loader import config

class HybridSearchService:
    def __init__(self):
        # Get search weights from config
        self.weights = config.get_search_weights()
        self.min_similarity = config.get_min_similarity()
        
        print(f"✓ Hybrid Search initialized with weights: {self.weights}")
    
    def search(self, query: str, corpus_id: str):
        """Perform hybrid search."""
        
        # Vector search
        vector_results = self._vector_search(query)
        
        # Keyword search
        keyword_results = self._keyword_search(query)
        
        # Graph search
        graph_results = self._graph_search(query)
        
        # Combine with weights
        combined = self._combine_results(
            vector_results,
            keyword_results,
            graph_results,
            self.weights
        )
        
        # Filter by min similarity
        filtered = [r for r in combined if r['score'] >= self.min_similarity]
        
        return filtered
```

---

## 📝 Primer: Logging

**modules/legal_parser/service.py**:

```python
import logging
from shared.config_loader import config

# Setup logger
logger = logging.getLogger("legal_parser")

# Configure from config
logging.basicConfig(
    level=config.get_log_level(),
    format=config.get_log_format(),
    datefmt=config.get_log_date_format(),
    handlers=[
        logging.FileHandler(config.get_log_file("legal_parser")),
        logging.StreamHandler()
    ]
)

class LegalParserService:
    def parse(self, text: str):
        """Parse legal document."""
        logger.info(f"Parsing document ({len(text)} chars)")
        
        # ... parsing logic
        
        logger.info(f"Parsing completed")
        return result
```

---

## 🚀 Primer: Workflow Configuration

**orchestrator/workflows/import_corpus.py**:

```python
from shared.config_loader import config
import httpx

async def execute_import_corpus_workflow(corpus_id: str, file_paths: list):
    """Execute import corpus workflow."""
    
    # Check if workflow is enabled
    if not config.is_workflow_enabled("import_corpus"):
        raise ValueError("Import corpus workflow is disabled")
    
    # Get workflow steps
    steps = config.get_workflow_steps("import_corpus")
    
    results = []
    
    for step_name in steps:
        # Get module URL
        module_url = config.get_module_url(step_name)
        
        # Get timeout
        timeout = config.get("performance.timeouts.http_request", 30)
        
        # Call module
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{module_url}/api/process",
                json={"corpus_id": corpus_id, "file_paths": file_paths}
            )
            results.append(response.json())
    
    return results
```

---

## 🎛️ Primer: Feature Flags

**modules/recommendation_generator/service.py**:

```python
from shared.config_loader import config

class RecommendationService:
    def __init__(self):
        # Check if LLM is enabled
        self.use_llm = config.is_feature_enabled("enable_llm")
        
        if self.use_llm:
            self.llm_url = config.get_llm_base_url()
            self.llm_model = config.get_llm_model()
            print(f"✓ LLM enabled: {self.llm_model}")
        else:
            print("⚠ LLM disabled, using rule-based recommendations")
    
    def generate_recommendation(self, conflict):
        """Generate recommendation."""
        if self.use_llm:
            return self._generate_with_llm(conflict)
        else:
            return self._generate_rule_based(conflict)
```

---

## 🔄 Primer: Dynamic Configuration Reload

```python
from shared.config_loader import config

# Initial load
print(f"Port: {config.get_module_port('file_reader')}")  # 8101

# Change config.yaml manually
# ...

# Reload configuration
config.reload()

print(f"Port: {config.get_module_port('file_reader')}")  # New value
```

---

## 📊 Primer: Performance Configuration

**modules/embedding_generator/service.py**:

```python
from shared.config_loader import config

class EmbeddingService:
    def __init__(self):
        # Get performance settings
        self.batch_size = config.get_batch_size("embeddings")
        self.max_workers = config.get_max_workers()
        self.cache_enabled = config.is_cache_enabled()
        self.cache_ttl = config.get_cache_ttl()
        
        print(f"✓ Performance config:")
        print(f"  - Batch size: {self.batch_size}")
        print(f"  - Max workers: {self.max_workers}")
        print(f"  - Cache: {'enabled' if self.cache_enabled else 'disabled'}")
```

---

## 🧪 Primer: Testing sa Mock Config

**tests/test_file_reader.py**:

```python
import pytest
from shared.config_loader import ConfigLoader

@pytest.fixture
def mock_config(monkeypatch):
    """Mock configuration for testing."""
    config = ConfigLoader()
    
    # Override specific values
    monkeypatch.setattr(config, "get_module_port", lambda x: 9999)
    monkeypatch.setattr(config, "get_database_url", lambda x: "sqlite:///:memory:")
    
    return config

def test_file_reader(mock_config):
    """Test file reader with mock config."""
    port = mock_config.get_module_port("file_reader")
    assert port == 9999
```

---

## ✅ Prednosti Ovog Pristupa

1. **Centralizovano** - Svi parametri na jednom mestu
2. **Type-safe** - Getteri sa tipovima
3. **Default values** - Fallback vrednosti
4. **Dot notation** - Lak pristup nested vrednostima
5. **Singleton** - Jedna instanca za sve module
6. **Reload** - Mogućnost reload-a bez restarta
7. **Testabilno** - Lako mockovanje za testove
8. **Dokumentovano** - Jasni getteri sa opisima

---

## 🔧 Dodavanje Novih Parametara

### 1. Dodaj u config.yaml

```yaml
# config.yaml
new_feature:
  enabled: true
  parameter1: "value1"
  parameter2: 42
```

### 2. Dodaj getter u config_loader.py

```python
# shared/config_loader.py
def is_new_feature_enabled(self) -> bool:
    """Check if new feature is enabled."""
    return self.get("new_feature.enabled", False)

def get_new_feature_param1(self) -> str:
    """Get new feature parameter 1."""
    return self.get("new_feature.parameter1", "default")
```

### 3. Koristi u modulu

```python
# modules/some_module/service.py
from shared.config_loader import config

if config.is_new_feature_enabled():
    param1 = config.get_new_feature_param1()
    # Use new feature
```

---

## 📝 Best Practices

1. **Uvek koristi config loader** - Ne hardkoduj vrednosti
2. **Koristi getters** - Ne pristupaj direktno dict-u
3. **Dodaj default values** - Za fallback
4. **Dokumentuj nove parametre** - U config.yaml
5. **Testiraj sa mock config** - Za unit testove
6. **Reload samo kad treba** - Ne u svakom request-u
7. **Validiraj vrednosti** - Pre korišćenja

---

**Status**: Spremno za korišćenje u svim modulima!