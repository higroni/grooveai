# Hybrid Architecture: Batch Processing + Interactive API

## Design Philosophy

**Two Modes, One Codebase**

1. **Batch Mode** (Production): Monolithic pipeline for processing 8,000 documents
2. **Interactive Mode** (Development/Debug): HTTP API for step-by-step inspection

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Shared Core Library                      │
│  - All processing logic (M1-M10)                            │
│  - Models and services                                      │
│  - Database operations                                      │
│  - Caching and monitoring                                   │
└─────────────────────────────────────────────────────────────┘
                    ↓                    ↓
        ┌───────────────────┐  ┌───────────────────┐
        │   Batch Processor │  │   HTTP API Server │
        │   (Production)    │  │   (Development)   │
        └───────────────────┘  └───────────────────┘
```

---

## Implementation Strategy

### 1. Shared Core Library

All processing logic extracted into reusable library:

```
pipeline/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── file_reader.py       # M1 logic
│   ├── normalizer.py        # M2 logic
│   ├── latinizer.py         # M3 logic
│   ├── parser.py            # M4 logic
│   ├── assertion_extractor.py  # M6 logic
│   ├── entity_recognizer.py    # M7 logic
│   ├── condition_extractor.py  # M8 logic
│   ├── classifier.py           # M9 logic
│   └── enrichment.py           # M10 logic
├── models/
│   ├── __init__.py
│   └── schemas.py           # Pydantic models
├── database/
│   ├── __init__.py
│   └── operations.py        # DB operations
└── utils/
    ├── __init__.py
    ├── cache.py
    └── monitoring.py
```

### 2. Batch Processor (Production)

Fast, parallel processing for large datasets:

```python
# batch_processor.py
from pipeline.core import DocumentPipeline
import multiprocessing as mp

class BatchProcessor:
    """High-performance batch processing."""
    
    def __init__(self, workers: int = 12):
        self.workers = workers
        self.pipeline = None  # Lazy load in worker
    
    def process_directory(self, input_dir: str, output_db: str):
        """Process all documents in directory."""
        files = list(Path(input_dir).glob("**/*.pdf"))
        
        with mp.Pool(processes=self.workers) as pool:
            results = pool.map(self._process_single, files)
        
        # Batch write to database
        self._write_results(results, output_db)
    
    def _process_single(self, file_path: str) -> dict:
        """Process single document (runs in worker)."""
        if self.pipeline is None:
            self.pipeline = DocumentPipeline()
        
        return self.pipeline.process(file_path)

# CLI entry point
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    
    processor = BatchProcessor(workers=args.workers)
    processor.process_directory(args.input_dir, "output.db")
```

### 3. HTTP API Server (Development/Debug)

Interactive API for step-by-step inspection:

```python
# api_server.py
from fastapi import FastAPI, UploadFile
from pipeline.core import (
    FileReaderService, NormalizerService, LatinizerService,
    ParserService, AssertionExtractorService, EntityRecognizerService,
    ConditionExtractorService, ClassifierService, EnrichmentService
)

app = FastAPI(title="Legal Document Pipeline API")

# Initialize services once at startup
@app.on_event("startup")
async def startup():
    app.state.file_reader = FileReaderService()
    app.state.normalizer = NormalizerService()
    app.state.latinizer = LatinizerService()
    app.state.parser = ParserService()
    app.state.assertion_extractor = AssertionExtractorService()
    app.state.entity_recognizer = EntityRecognizerService()
    app.state.condition_extractor = ConditionExtractorService()
    app.state.classifier = ClassifierService()
    app.state.enrichment = EnrichmentService()

# Individual module endpoints for debugging
@app.post("/api/v1/read")
async def read_file(file: UploadFile):
    """M1: Read and extract text from file."""
    content = await file.read()
    result = app.state.file_reader.process(content)
    return {"module": "M1_file_reader", "output": result}

@app.post("/api/v1/normalize")
async def normalize(text: str):
    """M2: Normalize text."""
    result = app.state.normalizer.process(text)
    return {"module": "M2_normalizer", "output": result}

@app.post("/api/v1/latinize")
async def latinize(text: str):
    """M3: Convert to Latin script."""
    result = app.state.latinizer.process(text)
    return {"module": "M3_latinizer", "output": result}

@app.post("/api/v1/parse")
async def parse(text: str):
    """M4: Parse legal structure."""
    result = app.state.parser.process(text)
    return {"module": "M4_parser", "output": result}

@app.post("/api/v1/extract-assertions")
async def extract_assertions(legal_units: list):
    """M6: Extract assertions."""
    result = app.state.assertion_extractor.process_batch(legal_units)
    return {"module": "M6_assertions", "output": result}

@app.post("/api/v1/recognize-entities")
async def recognize_entities(assertions: list):
    """M7: Recognize entities."""
    result = app.state.entity_recognizer.process_batch(assertions)
    return {"module": "M7_entities", "output": result}

@app.post("/api/v1/extract-conditions")
async def extract_conditions(assertions: list):
    """M8: Extract conditions."""
    result = app.state.condition_extractor.process_batch(assertions)
    return {"module": "M8_conditions", "output": result}

@app.post("/api/v1/classify")
async def classify(assertions: list):
    """M9: Classify assertions."""
    result = app.state.classifier.process_batch(assertions)
    return {"module": "M9_classifier", "output": result}

@app.post("/api/v1/enrich")
async def enrich(assertions: list, entities: list, conditions: list):
    """M10: Enrich with knowledge."""
    result = app.state.enrichment.process_batch(assertions, entities, conditions)
    return {"module": "M10_enrichment", "output": result}

# Full pipeline endpoint for convenience
@app.post("/api/v1/pipeline/full")
async def full_pipeline(file: UploadFile):
    """Process document through entire pipeline."""
    # Read file
    content = await file.read()
    text = app.state.file_reader.process(content)
    
    # Preprocess
    normalized = app.state.normalizer.process(text)
    latinized = app.state.latinizer.process(normalized)
    
    # Parse
    legal_units = app.state.parser.process(latinized)
    
    # Extract and enrich
    assertions = app.state.assertion_extractor.process_batch(legal_units)
    entities = app.state.entity_recognizer.process_batch(assertions)
    conditions = app.state.condition_extractor.process_batch(assertions)
    classifications = app.state.classifier.process_batch(assertions)
    enriched = app.state.enrichment.process_batch(assertions, entities, conditions)
    
    return {
        "pipeline": "full",
        "steps": {
            "M1_file_reader": {"status": "success"},
            "M2_normalizer": {"status": "success"},
            "M3_latinizer": {"status": "success"},
            "M4_parser": {"legal_units": len(legal_units)},
            "M6_assertions": {"count": len(assertions)},
            "M7_entities": {"count": len(entities)},
            "M8_conditions": {"count": len(conditions)},
            "M9_classifier": {"count": len(classifications)},
            "M10_enrichment": {"count": len(enriched)}
        },
        "output": enriched
    }

# Health and monitoring endpoints
@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """Get performance metrics."""
    return {
        "cache_stats": app.state.cache.get_stats(),
        "model_info": app.state.entity_recognizer.get_model_info()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Web GUI Integration

### Frontend Architecture

```
web-gui/
├── index.html
├── app.js
└── components/
    ├── FileUploader.js
    ├── PipelineViewer.js
    ├── ModuleInspector.js
    └── ResultsViewer.js
```

### Example: Step-by-Step Pipeline Viewer

```javascript
// PipelineViewer.js
class PipelineViewer {
    constructor() {
        this.apiBase = 'http://localhost:8000/api/v1';
        this.currentStep = 0;
        this.results = {};
    }
    
    async processStep(step, input) {
        const endpoints = {
            'read': '/read',
            'normalize': '/normalize',
            'latinize': '/latinize',
            'parse': '/parse',
            'extract-assertions': '/extract-assertions',
            'recognize-entities': '/recognize-entities',
            'extract-conditions': '/extract-conditions',
            'classify': '/classify',
            'enrich': '/enrich'
        };
        
        const response = await fetch(
            `${this.apiBase}${endpoints[step]}`,
            {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(input)
            }
        );
        
        const result = await response.json();
        this.results[step] = result;
        
        // Update UI
        this.displayResult(step, result);
        
        return result.output;
    }
    
    displayResult(step, result) {
        const container = document.getElementById('results');
        const stepDiv = document.createElement('div');
        stepDiv.className = 'pipeline-step';
        stepDiv.innerHTML = `
            <h3>${result.module}</h3>
            <pre>${JSON.stringify(result.output, null, 2)}</pre>
            <button onclick="viewer.nextStep()">Next Step →</button>
        `;
        container.appendChild(stepDiv);
    }
    
    async runFullPipeline(file) {
        // Step 1: Read file
        let output = await this.processStep('read', file);
        
        // Step 2: Normalize
        output = await this.processStep('normalize', output);
        
        // Step 3: Latinize
        output = await this.processStep('latinize', output);
        
        // Step 4: Parse
        output = await this.processStep('parse', output);
        
        // Step 5: Extract assertions
        output = await this.processStep('extract-assertions', output);
        
        // Step 6: Recognize entities
        const entities = await this.processStep('recognize-entities', output);
        
        // Step 7: Extract conditions
        const conditions = await this.processStep('extract-conditions', output);
        
        // Step 8: Classify
        const classifications = await this.processStep('classify', output);
        
        // Step 9: Enrich
        const enriched = await this.processStep('enrich', {
            assertions: output,
            entities: entities,
            conditions: conditions
        });
        
        return enriched;
    }
}

// Usage
const viewer = new PipelineViewer();
document.getElementById('upload').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    await viewer.runFullPipeline(file);
});
```

---

## Deployment Strategy

### Development Environment
```bash
# Start API server for debugging
python api_server.py

# Access at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Production Environment
```bash
# Batch process 8,000 documents
python batch_processor.py /path/to/documents --workers 12

# Output: processed.db (SQLite database with all results)
```

### Hybrid Usage
```bash
# Process in batch mode
python batch_processor.py /data/batch1 --workers 12

# Then start API for inspection
python api_server.py

# GUI can query results from processed.db
```

---

## Benefits of Hybrid Approach

### For Development
✅ **Step-by-step debugging**: Inspect each module's output  
✅ **Interactive testing**: Upload single file, see results immediately  
✅ **API documentation**: Auto-generated Swagger/OpenAPI docs  
✅ **Web GUI**: Visual pipeline inspection

### For Production
✅ **Maximum performance**: 60-90x faster than API mode  
✅ **Parallel processing**: 8-16 documents simultaneously  
✅ **Resource efficiency**: No HTTP overhead  
✅ **Scalability**: Process 8,000 documents in ~1 hour

### Best of Both Worlds
✅ **Same codebase**: No duplication, single source of truth  
✅ **Easy switching**: Choose mode based on use case  
✅ **Gradual migration**: Can run both modes simultaneously  
✅ **Future-proof**: Add new features once, available in both modes

---

## Migration Path

### Phase 1: Extract Core Library (Week 1)
```
1. Create pipeline/core/ directory
2. Move all processing logic from modules/*/service.py
3. Keep API wrappers thin (just HTTP handling)
4. Test: Ensure API still works
```

### Phase 2: Implement Batch Processor (Week 2)
```
1. Create batch_processor.py using core library
2. Add multiprocessing support
3. Test with 100 documents
4. Validate results match API version
```

### Phase 3: Optimize and Scale (Week 3)
```
1. Tune batch sizes and worker count
2. Add progress tracking
3. Test with 1,000 documents
4. Performance profiling
```

### Phase 4: Production Deployment (Week 4)
```
1. Full 8,000 document test
2. Documentation for both modes
3. Web GUI integration
4. Monitoring and logging
```

---

## Code Organization

```
GROOVE.AI/
├── pipeline/                    # Shared core library
│   ├── __init__.py
│   ├── core/                    # Processing logic (M1-M10)
│   ├── models/                  # Data models
│   ├── database/                # DB operations
│   └── utils/                   # Utilities
│
├── batch_processor.py           # Production: Fast batch processing
├── api_server.py                # Development: HTTP API
│
├── modules/                     # Legacy (keep for now)
│   ├── file_reader/
│   ├── text_normalizer/
│   └── ...
│
├── web-gui/                     # Web interface
│   ├── index.html
│   ├── app.js
│   └── components/
│
└── tests/
    ├── test_core.py             # Test core library
    ├── test_batch.py            # Test batch processor
    └── test_api.py              # Test API server
```

---

## Example Usage Scenarios

### Scenario 1: Development - Testing New Feature
```bash
# Start API server
python api_server.py

# Open web GUI
# Upload single document
# Inspect each module's output
# Iterate on code
# No need to restart server (hot reload)
```

### Scenario 2: Production - Process Large Dataset
```bash
# Process 8,000 documents
python batch_processor.py /data/legal_docs --workers 12

# Output: processed.db
# Time: ~45-60 minutes
# Success rate: 95%+
```

### Scenario 3: Hybrid - Debug Production Issue
```bash
# Process batch
python batch_processor.py /data/batch1 --workers 12

# Found issue with document X
# Start API for debugging
python api_server.py

# Upload document X via GUI
# Step through pipeline
# Identify problem
# Fix code
# Re-run batch
```

---

## Performance Comparison

### API Mode (Current)
```
Use Case:       Single document debugging
Performance:    ~180s per document
Parallelism:    None (sequential)
Resource Usage: 10GB+ RAM (10 servers)
Best For:       Development, testing, GUI
```

### Batch Mode (New)
```
Use Case:       Large dataset processing
Performance:    ~2-3s per document
Parallelism:    8-16 workers
Resource Usage: 4-8GB RAM (shared models)
Best For:       Production, bulk processing
```

### Recommendation
- **Development**: Use API mode + Web GUI
- **Production**: Use Batch mode
- **Both available**: Choose based on use case

---

## Conclusion

**Hybrid architecture provides best of both worlds:**

1. ✅ **Keep API for development/debugging** - Web GUI works as planned
2. ✅ **Add batch processor for production** - 60x faster for large datasets
3. ✅ **Single codebase** - No duplication, easy maintenance
4. ✅ **Flexible deployment** - Choose mode based on use case

**Next Steps:**
1. Extract core library from existing modules
2. Implement batch processor
3. Test with 100 documents
4. Validate performance improvements

**Timeline:** 4 weeks to full production deployment