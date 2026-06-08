# Architecture Redesign for Scale
**Target**: Process 8,000 documents in 2-3 hours (2-3s per document)  
**Current**: 77 minutes for 25 documents (~3 minutes per document)  
**Required Speedup**: **60x improvement needed**

---

## Root Cause Analysis: Why So Slow?

### 1. HTTP Overhead (MAJOR BOTTLENECK)
```
Current Architecture: 10 HTTP calls per document
- M1 → M2 → M3 → M4 → M6 → M7 → M8 → M9 → M10
- Each call: TCP handshake + JSON serialization + network latency
- Estimated overhead: 200-500ms per call = 2-5s per document
```

**Problem**: HTTP servers are designed for distributed systems, not single-machine pipelines.

### 2. Sequential Processing (NO PARALLELISM)
```
Current: Process 1 document at a time
- 25 documents × 3 min = 75 minutes
- CPU cores idle: ~90% of the time
- GPU idle: ~95% of the time
```

**Problem**: Not utilizing available hardware parallelism.

### 3. Module Startup Overhead
```
Each HTTP server:
- Flask/FastAPI overhead
- Model loading (CLASSLA, embeddings)
- Database connections
- Memory footprint: ~500MB-1GB per module
```

**Problem**: 10 servers × 1GB = 10GB RAM just for infrastructure.

### 4. Database Locking
```
SQLite with multiple processes:
- Write locks block readers
- Sequential writes only
- Contention increases with parallelism
```

**Problem**: SQLite not designed for high-concurrency writes.

---

## Proposed Architecture: Monolithic Pipeline Processor

### Design Philosophy
**ELIMINATE HTTP OVERHEAD** - Direct Python function calls  
**MAXIMIZE PARALLELISM** - Process multiple documents simultaneously  
**MINIMIZE MEMORY** - Single process, shared models  
**OPTIMIZE I/O** - Batch database operations

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────┐
│  CLI Entry Point: process_documents.py                  │
│  - Accepts directory path or file list                  │
│  - Configurable parallelism (workers)                   │
│  - Progress tracking and checkpointing                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Document Queue Manager                                 │
│  - Load all document paths                              │
│  - Distribute to worker pool                            │
│  - Collect results                                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Worker Pool (multiprocessing.Pool)                     │
│  - N workers (configurable, default: CPU cores - 1)     │
│  - Each worker: independent pipeline instance           │
│  - Shared: GPU models (via CUDA streams)                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Pipeline Instance (per worker)                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 1. File Reader      → in-memory text              │  │
│  │ 2. Normalizer       → normalized text             │  │
│  │ 3. Latinizer        → latinized text              │  │
│  │ 4. Parser           → legal units                 │  │
│  │ 5. Assertion Ext.   → assertions (batch)          │  │
│  │ 6. Entity Recog.    → entities (GPU batch)        │  │
│  │ 7. Condition Ext.   → conditions (batch)          │  │
│  │ 8. Classifier       → classifications             │  │
│  │ 9. Enrichment       → enriched data (GPU batch)   │  │
│  └───────────────────────────────────────────────────┘  │
│  All steps: Direct function calls (no HTTP)             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Batch Database Writer                                  │
│  - Accumulate results from all workers                  │
│  - Write in large batches (100-1000 records)            │
│  - Single writer thread (no locking contention)         │
│  - Optional: PostgreSQL for better concurrency          │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Strategy

### Phase 1: Create Monolithic Pipeline (Week 1)

#### 1.1 Core Pipeline Class
```python
# pipeline/processor.py
class DocumentPipeline:
    """Single-process pipeline with all modules integrated."""
    
    def __init__(self, gpu_id: int = 0):
        """Initialize all modules once (shared across documents)."""
        self.gpu_id = gpu_id
        
        # Load models once
        self.file_reader = FileReaderService()
        self.normalizer = NormalizerService()
        self.latinizer = LatinizerService()
        self.parser = ParserService()
        self.assertion_extractor = AssertionExtractorService()
        self.entity_recognizer = EntityRecognizerService(gpu_id=gpu_id)
        self.condition_extractor = ConditionExtractorService()
        self.classifier = ClassifierService()
        self.enrichment = EnrichmentService(gpu_id=gpu_id)
        
        # Cache for repeated operations
        self.cache = LRUCache(maxsize=1000)
    
    def process_document(self, file_path: str) -> Dict:
        """Process single document through entire pipeline."""
        try:
            # Step 1: Read file
            text = self.file_reader.read(file_path)
            
            # Step 2-3: Normalize and latinize
            normalized = self.normalizer.normalize(text)
            latinized = self.latinizer.latinize(normalized)
            
            # Step 4: Parse legal structure
            legal_units = self.parser.parse(latinized)
            
            if not legal_units:
                return {"status": "empty", "file": file_path}
            
            # Step 5-9: Extract and enrich (batch operations)
            assertions = self.assertion_extractor.extract_batch(legal_units)
            
            if not assertions:
                return {"status": "no_assertions", "file": file_path}
            
            entities = self.entity_recognizer.recognize_batch(assertions)
            conditions = self.condition_extractor.extract_batch(assertions)
            classifications = self.classifier.classify_batch(assertions)
            enriched = self.enrichment.enrich_batch(assertions, entities, conditions)
            
            return {
                "status": "success",
                "file": file_path,
                "assertions": len(assertions),
                "entities": len(entities),
                "conditions": len(conditions),
                "enriched": len(enriched),
                "data": enriched
            }
            
        except Exception as e:
            return {"status": "error", "file": file_path, "error": str(e)}
```

#### 1.2 CLI Entry Point
```python
# process_documents.py
import argparse
import multiprocessing as mp
from pathlib import Path
from typing import List
import time

def process_worker(args):
    """Worker function for multiprocessing."""
    file_path, gpu_id = args
    pipeline = DocumentPipeline(gpu_id=gpu_id)
    return pipeline.process_document(file_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="Directory with PDF files")
    parser.add_argument("--workers", type=int, default=mp.cpu_count() - 1)
    parser.add_argument("--gpu-workers", type=int, default=1, 
                       help="Number of GPU workers (if multiple GPUs)")
    parser.add_argument("--batch-size", type=int, default=100,
                       help="Database batch write size")
    parser.add_argument("--checkpoint", type=str, default="checkpoint.json")
    args = parser.parse_args()
    
    # Find all PDF files
    files = list(Path(args.input_dir).glob("**/*.pdf"))
    print(f"Found {len(files)} files to process")
    
    # Assign GPU IDs to workers
    worker_args = [(f, i % args.gpu_workers) for i, f in enumerate(files)]
    
    # Process in parallel
    start_time = time.time()
    with mp.Pool(processes=args.workers) as pool:
        results = pool.map(process_worker, worker_args)
    
    elapsed = time.time() - start_time
    
    # Write results to database in batch
    write_results_batch(results, batch_size=args.batch_size)
    
    # Print summary
    successful = sum(1 for r in results if r["status"] == "success")
    print(f"\nProcessed {len(files)} files in {elapsed:.2f}s")
    print(f"Success: {successful}/{len(files)} ({successful/len(files)*100:.1f}%)")
    print(f"Average: {elapsed/len(files):.2f}s per file")

if __name__ == "__main__":
    main()
```

### Phase 2: Optimize Critical Paths (Week 2)

#### 2.1 GPU Batch Processing
```python
class OptimizedEntityRecognizer:
    """Process multiple documents' assertions in single GPU batch."""
    
    def __init__(self, gpu_id: int = 0):
        self.gpu_id = gpu_id
        self.model = self._load_model()
        self.batch_size = 128  # Process 128 assertions at once
    
    def recognize_batch(self, assertions: List[Dict]) -> List[Dict]:
        """Process assertions in optimal GPU batches."""
        results = []
        
        # Group into GPU-optimal batches
        for i in range(0, len(assertions), self.batch_size):
            batch = assertions[i:i + self.batch_size]
            texts = [a["text"] for a in batch]
            
            # Single GPU call for entire batch
            entities = self.model.process_batch(texts)
            results.extend(entities)
        
        return results
```

#### 2.2 Database Optimization
```python
class BatchDatabaseWriter:
    """Accumulate and write results in large batches."""
    
    def __init__(self, db_path: str, batch_size: int = 1000):
        self.db_path = db_path
        self.batch_size = batch_size
        self.buffer = []
        self.lock = threading.Lock()
    
    def add_result(self, result: Dict):
        """Add result to buffer, flush if full."""
        with self.lock:
            self.buffer.append(result)
            if len(self.buffer) >= self.batch_size:
                self._flush()
    
    def _flush(self):
        """Write entire buffer to database in single transaction."""
        if not self.buffer:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Single transaction for all inserts
            cursor.execute("BEGIN TRANSACTION")
            
            for result in self.buffer:
                # Insert assertions
                cursor.executemany(
                    "INSERT INTO assertions VALUES (?, ?, ?, ?)",
                    result["assertions"]
                )
                # Insert entities
                cursor.executemany(
                    "INSERT INTO entities VALUES (?, ?, ?, ?)",
                    result["entities"]
                )
                # ... other tables
            
            cursor.execute("COMMIT")
            self.buffer.clear()
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            raise e
        finally:
            conn.close()
```

### Phase 3: Advanced Optimizations (Week 3)

#### 3.1 Model Caching and Sharing
```python
# Use shared memory for models across workers
from multiprocessing import shared_memory

class SharedModelManager:
    """Share loaded models across all workers."""
    
    @staticmethod
    def load_shared_model(model_name: str):
        """Load model into shared memory once."""
        # Load model
        model = load_model(model_name)
        
        # Serialize to bytes
        model_bytes = pickle.dumps(model)
        
        # Create shared memory
        shm = shared_memory.SharedMemory(
            create=True, 
            size=len(model_bytes),
            name=f"model_{model_name}"
        )
        
        # Copy to shared memory
        shm.buf[:len(model_bytes)] = model_bytes
        
        return shm.name
    
    @staticmethod
    def get_shared_model(shm_name: str):
        """Access model from shared memory."""
        shm = shared_memory.SharedMemory(name=shm_name)
        model_bytes = bytes(shm.buf)
        return pickle.loads(model_bytes)
```

#### 3.2 Async I/O for File Reading
```python
import asyncio
import aiofiles

class AsyncFileReader:
    """Read multiple files concurrently."""
    
    async def read_file(self, path: str) -> str:
        """Read single file asynchronously."""
        async with aiofiles.open(path, 'rb') as f:
            content = await f.read()
            return extract_text_from_pdf(content)
    
    async def read_batch(self, paths: List[str]) -> List[str]:
        """Read multiple files concurrently."""
        tasks = [self.read_file(p) for p in paths]
        return await asyncio.gather(*tasks)
```

---

## Performance Projections

### Current Architecture (HTTP-based)
```
Single document:        ~180s (3 minutes)
25 documents:           ~4,500s (75 minutes)
8,000 documents:        ~400 hours (16.7 days)

Bottlenecks:
- HTTP overhead:        ~50s per document
- Sequential processing: No parallelism
- Database locking:     Contention
```

### Proposed Architecture (Monolithic + Parallel)

#### Conservative Estimate (8 workers, 1 GPU)
```
Single document:        ~3s (60x faster)
- No HTTP overhead:     -50s
- Optimized batching:   -100s
- Better GPU usage:     -27s

Parallel throughput:    8 docs/3s = 2.67 docs/s
8,000 documents:        ~3,000s (50 minutes)
```

#### Optimistic Estimate (16 workers, 2 GPUs)
```
Single document:        ~2s (90x faster)
Parallel throughput:    16 docs/2s = 8 docs/s
8,000 documents:        ~1,000s (16.7 minutes)
```

#### Target Achievement
```
Target:                 2-3s per document
Workers needed:         8-12 (with 1 GPU)
Total time (8k docs):   ~45-60 minutes ✅
```

---

## Migration Plan

### Week 1: Core Implementation
- [ ] Create `DocumentPipeline` class with all modules
- [ ] Implement CLI entry point with multiprocessing
- [ ] Test with 100 documents
- [ ] Validate results match HTTP version

### Week 2: Optimization
- [ ] Implement batch database writer
- [ ] Optimize GPU batch sizes
- [ ] Add progress tracking and checkpointing
- [ ] Test with 1,000 documents

### Week 3: Scale Testing
- [ ] Test with full 8,000 document dataset
- [ ] Tune worker count and batch sizes
- [ ] Implement error recovery
- [ ] Performance profiling and bottleneck analysis

### Week 4: Production Deployment
- [ ] Documentation and user guide
- [ ] Monitoring and logging
- [ ] Backup and recovery procedures
- [ ] Final validation

---

## Technology Stack Changes

### Keep
✅ **Python** - Core language  
✅ **PyTorch + CLASSLA** - GPU-accelerated NER  
✅ **SQLite** - For single-writer scenarios  
✅ **Stanza** - Legal text parsing

### Remove
❌ **Flask/FastAPI** - HTTP overhead not needed  
❌ **Multiple processes** - Consolidate to worker pool  
❌ **HTTP clients** - Direct function calls

### Add
✅ **multiprocessing.Pool** - Parallel document processing  
✅ **asyncio** - Async file I/O  
✅ **shared_memory** - Share models across workers  
✅ **PostgreSQL** (optional) - Better concurrency than SQLite

---

## Risk Analysis

### Risks
1. **GPU Memory**: Multiple workers sharing GPU
   - **Mitigation**: CUDA streams, batch size tuning
   
2. **Database Locking**: SQLite write contention
   - **Mitigation**: Batch writes, single writer thread
   
3. **Memory Usage**: Loading models in each worker
   - **Mitigation**: Shared memory for models
   
4. **Error Handling**: One worker crash affects others
   - **Mitigation**: Process isolation, checkpointing

### Rollback Plan
- Keep HTTP architecture as fallback
- Gradual migration: test with small batches first
- Parallel operation: run both architectures during transition

---

## Expected Outcomes

### Performance
- **60-90x speedup** for single documents (3min → 2-3s)
- **8,000 documents in 45-60 minutes** (vs 16 days)
- **95%+ GPU utilization** (vs ~5% currently)
- **80%+ CPU utilization** (vs ~10% currently)

### Resource Usage
- **Memory**: 4-8GB (vs 10GB+ for HTTP servers)
- **Disk I/O**: Batched writes (10x fewer operations)
- **Network**: Zero (no HTTP calls)

### Operational
- **Simpler deployment**: Single Python script
- **Easier debugging**: No distributed tracing needed
- **Better monitoring**: Direct access to all metrics
- **Faster iteration**: No server restarts needed

---

## Conclusion

**Recommendation**: **PROCEED WITH ARCHITECTURE REDESIGN**

The current HTTP-based architecture is fundamentally unsuited for batch processing 8,000 documents. The proposed monolithic pipeline with multiprocessing will deliver:

1. **60-90x speedup** per document
2. **Target of 2-3s per document** achievable
3. **8,000 documents in ~1 hour** (vs 16 days)
4. **Simpler, more maintainable codebase**

**Next Step**: Implement Phase 1 (Core Pipeline) and validate with 100-document test.