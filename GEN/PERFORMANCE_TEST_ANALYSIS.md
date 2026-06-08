# Performance Test Analysis and Fixes

## Test Results Summary

**Test Run**: 25 documents processed before memory exhaustion
**Success Rate**: ~50% (high error rate)
**Primary Issues**:
1. Memory exhaustion causing system freeze
2. High error rate (~50% of documents failing)
3. M6 (Assertion Extractor) failures with status 500, 422, 404

## Root Cause Analysis

### 1. Memory Leak Issues

**Problem**: CLASSLA NER pipelines in M7 and M10 are loaded per request and never released
- Each document loads CLASSLA models into GPU/CPU memory
- Models are cached globally but GPU memory accumulates
- No memory cleanup between documents
- 25 documents × ~2GB per CLASSLA instance = 50GB+ memory usage

**Evidence**:
- System froze at document 25
- GPU memory not released between requests
- Global `_classla_pipeline` variable holds references indefinitely

### 2. Large Document Batch Processing Failures

**Problem**: Documents with 311+ legal units cause M6 batch endpoint to fail
- M6 batch processing has no size limits
- Large batches cause timeout or memory issues
- Status 500 errors indicate server-side crashes

**Evidence from logs**:
```json
{
  "document": "radni_odnosi_0001_000001.pdf",
  "success": false,
  "error": "M6 failed with status 500"
}
```

### 3. API Endpoint Inconsistencies

**Problem**: Multiple error codes (404, 422, 500) suggest API instability
- 404: Endpoint not found (routing issues)
- 422: Validation errors (data format issues)
- 500: Server crashes (memory/timeout issues)

**Evidence**: Different error codes across test runs for same documents

### 4. No Resource Cleanup Between Documents

**Problem**: Test script processes documents sequentially without cleanup
- No cache clearing between documents
- No GPU memory release
- Database connections accumulate
- HTTP sessions not properly closed

## Proposed Fixes

### Fix 1: Implement Proper Memory Management

**Changes to M7 and M10 Services**:

```python
# Add memory cleanup after batch processing
def cleanup_gpu_memory():
    """Release GPU memory after processing"""
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    except:
        pass

# Add to batch endpoints
@app.post("/api/recognize/batch")
async def recognize_batch(request: BatchRequest):
    try:
        result = service.recognize_batch(request.assertions)
        cleanup_gpu_memory()  # Clean up after batch
        return result
    finally:
        cleanup_gpu_memory()  # Ensure cleanup even on error
```

**Changes to CLASSLA Pipeline Loading**:

```python
# Limit CLASSLA pipeline instances
import threading
_pipeline_lock = threading.Lock()
_pipeline_usage_count = 0
MAX_PIPELINE_REUSES = 100  # Reload after N uses

def _get_classla_pipeline():
    global _classla_pipeline, _pipeline_usage_count
    
    with _pipeline_lock:
        # Reload pipeline periodically to prevent memory leaks
        if _pipeline_usage_count >= MAX_PIPELINE_REUSES:
            if _classla_pipeline:
                del _classla_pipeline
                cleanup_gpu_memory()
            _classla_pipeline = None
            _pipeline_usage_count = 0
        
        if _classla_pipeline is None:
            # Initialize pipeline...
            _pipeline_usage_count = 0
        
        _pipeline_usage_count += 1
        return _classla_pipeline
```

### Fix 2: Implement Batch Size Limits and Chunking

**Changes to M6 Batch Endpoint**:

```python
# Add batch size limits
MAX_BATCH_SIZE = 50  # Process max 50 units at once
CHUNK_SIZE = 25      # Split large batches into chunks

@app.post("/api/extract/batch")
async def extract_batch(request: BatchRequest):
    legal_units = request.legal_units
    
    # Check batch size
    if len(legal_units) > MAX_BATCH_SIZE:
        # Process in chunks
        results = []
        for i in range(0, len(legal_units), CHUNK_SIZE):
            chunk = legal_units[i:i + CHUNK_SIZE]
            chunk_results = service.extract_batch(chunk, request.min_confidence)
            results.extend(chunk_results)
        
        return BatchResponse(
            results=results,
            metadata={"total_processed": len(results)}
        )
    else:
        # Process normally
        return service.extract_batch(legal_units, request.min_confidence)
```

### Fix 3: Add Resource Cleanup to Test Script

**Changes to test_performance_load.py**:

```python
import gc
import requests

# Add session management
session = requests.Session()

def cleanup_resources():
    """Clean up resources between documents"""
    # Clear caches via API
    for module_name, url in MODULES.items():
        if module_name in ["M6", "M7", "M8", "M9", "M10"]:
            try:
                requests.post(f"{url}/cache/clear", timeout=5)
            except:
                pass
    
    # Force garbage collection
    gc.collect()
    
    # Clear GPU memory if available
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except:
        pass

def process_document(pdf_path, doc_num, total_docs):
    """Process document with cleanup"""
    try:
        result = _process_document_impl(pdf_path, doc_num, total_docs)
        return result
    finally:
        # Always cleanup after each document
        cleanup_resources()
        
        # Extra cleanup every 10 documents
        if doc_num % 10 == 0:
            print(f"\n🧹 Deep cleanup after {doc_num} documents...")
            time.sleep(2)  # Allow cleanup to complete
```

### Fix 4: Add Progress Checkpointing

**Changes to test_performance_load.py**:

```python
def save_checkpoint(results, checkpoint_file):
    """Save progress checkpoint"""
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def load_checkpoint(checkpoint_file):
    """Load progress checkpoint"""
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def run_test():
    """Run test with checkpointing"""
    checkpoint_file = RESULTS_DIR / "checkpoint.json"
    
    # Try to resume from checkpoint
    checkpoint = load_checkpoint(checkpoint_file)
    if checkpoint:
        print(f"\n📂 Resuming from checkpoint: {len(checkpoint['results'])} documents completed")
        results = checkpoint['results']
        start_idx = len(results)
    else:
        results = []
        start_idx = 0
    
    # Process documents
    for idx, pdf_path in enumerate(pdf_files[start_idx:], start=start_idx):
        result = process_document(pdf_path, idx + 1, len(pdf_files))
        results.append(result)
        
        # Save checkpoint every 5 documents
        if (idx + 1) % 5 == 0:
            save_checkpoint({"results": results}, checkpoint_file)
            print(f"💾 Checkpoint saved ({idx + 1} documents)")
```

### Fix 5: Add Request Timeout and Retry Logic

**Changes to test_performance_load.py**:

```python
def make_request_with_retry(url, json_data, max_retries=3, timeout=300):
    """Make HTTP request with retry logic"""
    for attempt in range(max_retries):
        try:
            response = session.post(url, json=json_data, timeout=timeout)
            return response
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"\n⏱️ Timeout, retrying in {wait_time}s... (attempt {attempt + 2}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                print(f"\n🔌 Connection error, retrying... (attempt {attempt + 2}/{max_retries})")
                time.sleep(2)
            else:
                raise
    
    raise Exception("Max retries exceeded")
```

### Fix 6: Add Memory Monitoring

**New utility function**:

```python
import psutil

def log_memory_usage(stage: str):
    """Log current memory usage"""
    process = psutil.Process()
    mem_info = process.memory_info()
    mem_mb = mem_info.rss / (1024 * 1024)
    
    # GPU memory if available
    gpu_mem = "N/A"
    try:
        import torch
        if torch.cuda.is_available():
            gpu_mem = f"{torch.cuda.memory_allocated() / (1024**2):.0f}MB"
    except:
        pass
    
    print(f"  💾 Memory [{stage}]: RAM={mem_mb:.0f}MB, GPU={gpu_mem}")
```

## Implementation Priority

### Phase 1: Critical Fixes (Immediate)
1. ✅ Add GPU memory cleanup to M7 and M10
2. ✅ Implement batch size limits in M6
3. ✅ Add resource cleanup between documents in test script
4. ✅ Add checkpointing for test resumption

### Phase 2: Stability Improvements (Next)
5. ✅ Add retry logic with exponential backoff
6. ✅ Add memory monitoring
7. ✅ Implement CLASSLA pipeline reloading

### Phase 3: Optimization (Later)
8. ⏳ Add parallel processing with worker pools
9. ⏳ Implement distributed processing
10. ⏳ Add real-time monitoring dashboard

## Expected Improvements

After implementing these fixes:

1. **Memory Usage**: Reduced from 50GB+ to <10GB for 235 documents
2. **Success Rate**: Improved from 50% to 95%+
3. **Stability**: No system freezes, graceful handling of large documents
4. **Resumability**: Can resume from checkpoint after interruption
5. **Throughput**: Maintain ~20-30s per document with cleanup overhead

## Testing Strategy

1. Test with 2 documents (onedoc) - verify fixes work
2. Test with 10 documents - verify memory cleanup
3. Test with 50 documents - verify checkpointing
4. Test with full 235 documents - verify stability
5. Monitor memory usage throughout

## Monitoring Metrics

Track these metrics during testing:
- RAM usage per document
- GPU memory usage per document
- Success/failure rate
- Average processing time per document
- Error types and frequencies
- Cache hit rates