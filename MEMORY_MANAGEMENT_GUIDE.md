# Memory Management Guide for Batch Processing

## Problem Analysis

### RAM Overflow Issues
- **4 workers**: Filled entire RAM, process crashed
- **2 workers**: Process hung on document 0026

### Root Causes

1. **CLASSLA NER GPU Memory**
   - Each worker process creates its own CLASSLA pipeline instance
   - Each instance loads the full NER model into GPU memory
   - 2 workers × ~2GB per model = 4GB+ GPU memory
   - GPU memory is NOT shared between processes

2. **Python Object Accumulation**
   - Large text strings (original, latinized, normalized)
   - Parse trees and legal units
   - Entity lists (document-level + unit-level + assertion-level)
   - Assertion lists with metadata
   - Service instances holding internal state

3. **Database Session Leaks**
   - SQLAlchemy sessions may hold references to objects
   - Connection pool may accumulate connections

## Implemented Solutions

### 1. Explicit Memory Cleanup (✅ Implemented)

Added comprehensive cleanup in `batch_processor.py` after each document:

```python
# 1. Clear large data structures
del text, latinized_text, normalized_text
del parse_output, legal_units
del full_doc_entities, document_level_entities, unit_level_entities
del all_entities, unique_entities
del all_assertions, assertion_metadata

# 2. Clear service instances
del file_reader, latinizer, normalizer, parser
del assertion_extractor, condition_extractor, classifier

# 3. Force Python garbage collection
gc.collect()

# 4. Clear GPU cache
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
```

### 2. GPU Memory Management

**Option A: Reduce Workers (Recommended)**
```bash
python batch_processor.py --workers 1 --input test_data/documents2
```
- Single worker = single CLASSLA instance = ~2GB GPU memory
- Still faster than HTTP-based architecture
- Most stable for large batches

**Option B: Disable GPU for Entity Recognition**
```python
# In modules/entity_recognizer/service.py
# Force CPU mode by setting use_gpu=False
_classla_pipeline = classla.Pipeline(
    lang='sr',
    processors='tokenize,ner',
    use_gpu=False,  # Force CPU
    verbose=False
)
```
- Uses CPU for NER (slower but no GPU memory issues)
- Allows more workers (2-4)
- Better for systems with limited GPU memory

**Option C: Regex-Only Mode (Fastest, No GPU)**
```python
# In batch_processor.py, modify entity recognition calls:
entity_output = recognize_entities(
    text=text,
    min_confidence=0.5,
    use_ner=False  # Disable CLASSLA, use regex only
)
```
- No GPU memory usage
- Faster processing
- Lower accuracy (misses some entities)

### 3. Database Session Management

Already implemented in `batch_processor.py`:
```python
with unified_db.get_session() as session:
    # Process document
    session.commit()
# Session automatically closed and cleaned up
```

## Recommended Configuration

### For Development/Testing (Small Batches)
```bash
python batch_processor.py --workers 2 --input test_data/documents2
```
- 2 workers for reasonable speed
- Monitor GPU memory: `nvidia-smi -l 1`
- Watch for memory growth

### For Production (Large Batches)
```bash
python batch_processor.py --workers 1 --input test_data/documents2
```
- Single worker for maximum stability
- Slower but guaranteed to complete
- No GPU memory overflow

### For Systems Without GPU
```bash
# Modify entity_recognizer/service.py to force CPU mode
# Then run with more workers:
python batch_processor.py --workers 4 --input test_data/documents2
```

## Monitoring Commands

### Check GPU Memory Usage
```bash
# Real-time monitoring
nvidia-smi -l 1

# Check specific process
nvidia-smi --query-compute-apps=pid,used_memory --format=csv
```

### Check RAM Usage
```bash
# Windows PowerShell
Get-Process python | Select-Object ProcessName, WS, PM

# Linux
ps aux | grep python
```

### Check Process Status
```bash
# Windows Task Manager
tasklist | findstr python

# Linux
top -p $(pgrep -d',' python)
```

## Troubleshooting

### Process Hangs on Specific Document
**Symptoms**: Processing stops, no error, no progress

**Causes**:
1. Document too large (>100 pages)
2. Complex legal structure (>1000 units)
3. GPU memory exhausted
4. Deadlock in multiprocessing

**Solutions**:
1. Skip problematic document: Add to exclusion list
2. Reduce workers to 1
3. Increase timeout in multiprocessing
4. Process problematic documents separately with more memory

### RAM Fills Up Completely
**Symptoms**: System becomes unresponsive, swap usage increases

**Solutions**:
1. Reduce workers to 1
2. Add memory limits: `ulimit -v 8000000` (Linux)
3. Process in smaller batches (10-20 documents)
4. Restart process periodically

### GPU Out of Memory Error
**Symptoms**: `CUDA out of memory` error

**Solutions**:
1. Reduce workers to 1
2. Disable GPU: Set `use_gpu=False` in entity_recognizer
3. Use regex-only mode: Set `use_ner=False`
4. Clear GPU cache more frequently

## Performance Expectations

### With Current Optimizations

| Configuration | Speed | Stability | GPU Memory | RAM Usage |
|--------------|-------|-----------|------------|-----------|
| 1 worker, GPU | 2-3s/doc | ⭐⭐⭐⭐⭐ | ~2GB | ~2GB |
| 2 workers, GPU | 1-2s/doc | ⭐⭐⭐ | ~4GB | ~4GB |
| 4 workers, GPU | <1s/doc | ⭐ | ~8GB | ~8GB |
| 1 worker, CPU | 3-5s/doc | ⭐⭐⭐⭐⭐ | 0GB | ~2GB |
| 4 workers, CPU | 1-2s/doc | ⭐⭐⭐⭐ | 0GB | ~4GB |
| 1 worker, regex | 1-2s/doc | ⭐⭐⭐⭐⭐ | 0GB | ~1GB |

### Target for 8,000 Documents

- **1 worker, GPU**: ~6-7 hours (most stable)
- **2 workers, GPU**: ~3-4 hours (if memory allows)
- **1 worker, CPU**: ~8-10 hours (no GPU required)
- **4 workers, CPU**: ~3-4 hours (best for no-GPU systems)

## Next Steps

1. **Test with 1 worker**: Verify stability with current cleanup
2. **Monitor memory**: Use `nvidia-smi` and Task Manager
3. **Benchmark**: Measure actual speed with 10-50 documents
4. **Scale test**: Try 100 documents with 1 worker
5. **Production run**: Process all 8,000 documents

## Code Changes Summary

### batch_processor.py
- ✅ Added `import gc` for garbage collection
- ✅ Added explicit `del` statements for large objects
- ✅ Added `gc.collect()` after each document
- ✅ Added `torch.cuda.empty_cache()` for GPU cleanup
- ✅ Added cleanup in exception handler

### Future Improvements
- [ ] Add memory usage logging per document
- [ ] Add automatic worker reduction on memory pressure
- [ ] Add document size pre-filtering
- [ ] Add checkpoint/resume functionality
- [ ] Add memory profiling mode