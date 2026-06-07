# GROOVE.AI Performance Optimization Plan

## Current Performance Analysis

### Timing Breakdown (154.6s total for 1 file):
```
M1_File_Reader              4.2s   (  2.7%)  ✓ Acceptable
M2_Text_Normalizer          2.1s   (  1.3%)  ✓ Acceptable  
M3_Latinizer                2.1s   (  1.4%)  ✓ Acceptable
M4_Legal_Parser             0.0s   (  0.0%)  ✓ Fast (not measured separately)
M6_Assertion_Extractor     12.3s   (  8.0%)  ⚠️ Needs optimization
M7_Entity_Recognizer       51.2s   ( 33.1%)  🔴 CRITICAL BOTTLENECK
M8_Condition_Extractor      0.0s   (  0.0%)  ✓ Fast (not measured separately)
M9_Assertion_Classifier    38.9s   ( 25.2%)  🔴 MAJOR BOTTLENECK
M10_Knowledge_Enrichment   43.8s   ( 28.3%)  🔴 MAJOR BOTTLENECK
```

### Key Issues:
1. **Sequential Processing**: Each assertion processed one-by-one (19 assertions × ~7s each)
2. **Network Overhead**: HTTP calls between modules add latency
3. **CLASSLA Initialization**: Heavy NER model loaded per request
4. **No Batch Processing**: Modules don't support batch operations
5. **Redundant Work**: Multiple modules parse same text

---

## Optimization Strategy

### Phase 1: Quick Wins (Target: 60s → 15s)

#### 1.1 Merge Fast Preprocessing Modules
**Merge M1+M2+M3+M4 into single "Document Processor" module**

**Rationale:**
- These modules are fast (8.4s combined)
- Sequential text transformations
- No benefit from separation
- Eliminates 3 HTTP round-trips

**Implementation:**
```python
# New: modules/document_processor/
# Combines: file_reader + text_normalizer + latinizer + legal_parser
# Single API call: /process_document
# Returns: {text, normalized, latinized, articles}
```

**Expected Gain:** 8.4s → 6s (save 2.4s from HTTP overhead)

---

#### 1.2 Implement Batch Processing for M6-M10
**Add `/batch` endpoints to all enrichment modules**

**Current:** 19 assertions × 19 HTTP calls per module = 361 total HTTP calls
**Target:** 19 assertions × 1 batch call per module = 5 total HTTP calls

**Implementation:**
```python
# M6: POST /extract/batch
{
  "articles": [article1, article2, ...],
  "batch_size": 50  # Process 50 articles at once
}

# M7: POST /recognize/batch  
{
  "assertions": [assertion1, assertion2, ...],
  "batch_size": 100
}

# M8: POST /extract/batch
{
  "assertions": [assertion1, assertion2, ...],
  "batch_size": 100
}

# M9: POST /classify/batch
{
  "assertions": [assertion1, assertion2, ...],
  "batch_size": 100
}

# M10: POST /enrich/batch (already exists!)
{
  "assertions": [assertion1, assertion2, ...],
  "batch_size": 50
}
```

**Expected Gain:** 
- M6: 12.3s → 8s (save 4.3s)
- M7: 51.2s → 15s (save 36.2s) 🎯
- M9: 38.9s → 12s (save 26.9s) 🎯
- M10: 43.8s → 15s (save 28.8s) 🎯

**Total Phase 1 Savings: ~98s (154s → 56s)**

---

### Phase 2: Architectural Improvements (Target: 56s → 10s)

#### 2.1 Parallel Processing with asyncio
**Process assertions in parallel batches**

**Current:** Sequential processing
**Target:** Process 5-10 assertions simultaneously

**Implementation:**
```python
import asyncio
import aiohttp

async def process_batch_parallel(assertions, batch_size=10):
    """Process assertions in parallel batches"""
    tasks = []
    for i in range(0, len(assertions), batch_size):
        batch = assertions[i:i+batch_size]
        tasks.append(process_single_batch(batch))
    
    results = await asyncio.gather(*tasks)
    return results
```

**Expected Gain:** 56s → 25s (save 31s)

---

#### 2.2 Merge M7+M8+M9 into "Assertion Analyzer"
**Single module for entity recognition, condition extraction, and classification**

**Rationale:**
- All three analyze same assertion text
- Can share NER results
- Single CLASSLA initialization
- Eliminates 2 HTTP round-trips per assertion

**Implementation:**
```python
# New: modules/assertion_analyzer/
# POST /analyze/batch
{
  "assertions": [...],
  "include_entities": true,
  "include_conditions": true,
  "include_classification": true
}

# Returns:
{
  "results": [
    {
      "assertion_id": "...",
      "entities": [...],
      "conditions": [...],
      "classification": {...}
    }
  ]
}
```

**Expected Gain:** 25s → 15s (save 10s)

---

#### 2.3 Optimize CLASSLA Loading
**Load CLASSLA once at module startup, not per request**

**Current:** CLASSLA loaded on first request, then cached
**Target:** Pre-load during module initialization

**Implementation:**
```python
# In main.py
def startup_event():
    """Pre-load heavy models"""
    logger.info("Pre-loading CLASSLA NER model...")
    _get_classla_pipeline()  # Force initialization
    logger.info("CLASSLA ready!")
```

**Expected Gain:** 15s → 12s (save 3s from cold starts)

---

#### 2.4 Database Connection Pooling
**Reuse database connections instead of creating new ones**

**Implementation:**
```python
# Use SQLAlchemy connection pooling
engine = create_engine(
    db_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

**Expected Gain:** 12s → 10s (save 2s)

---

### Phase 3: Advanced Optimizations (Target: 10s → 5s)

#### 3.1 Caching Layer with Redis
**Cache frequently accessed data**

**What to cache:**
- Ontology terms (M10)
- Classification patterns (M9)
- Entity recognition results for duplicate text
- Legal references (M10)

**Implementation:**
```python
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_entities(text_hash):
    """Get cached entity recognition results"""
    cached = cache.get(f"entities:{text_hash}")
    if cached:
        return json.loads(cached)
    return None
```

**Expected Gain:** 10s → 7s (save 3s)

---

#### 3.2 GPU Acceleration for CLASSLA
**Use GPU for NER if available**

**Implementation:**
```python
_classla_pipeline = classla.Pipeline(
    lang='sr',
    processors='tokenize,ner',
    use_gpu=True,  # Enable GPU
    verbose=False
)
```

**Expected Gain:** 7s → 5s (save 2s) - if GPU available

---

#### 3.3 Incremental Processing
**Process only changed assertions**

**Implementation:**
- Store hash of each assertion
- Skip processing if hash unchanged
- Useful for document updates

**Expected Gain:** Variable (depends on document changes)

---

## Implementation Roadmap

### Week 1: Quick Wins (Phase 1)
**Day 1-2:** Merge M1+M2+M3+M4 into Document Processor
- Create new module structure
- Combine logic
- Test thoroughly
- **Expected: 154s → 150s**

**Day 3-4:** Implement batch endpoints for M6
- Add `/extract/batch` endpoint
- Update database layer for bulk inserts
- Test with 50-100 articles
- **Expected: 150s → 146s**

**Day 5-7:** Implement batch endpoints for M7, M9, M10
- Add `/recognize/batch` to M7
- Add `/classify/batch` to M9  
- Test M10's existing `/enrich/batch`
- **Expected: 146s → 56s** 🎯

### Week 2: Architectural Improvements (Phase 2)
**Day 1-3:** Implement parallel processing
- Add asyncio support
- Create parallel batch processor
- Test with different batch sizes
- **Expected: 56s → 25s** 🎯

**Day 4-5:** Merge M7+M8+M9 into Assertion Analyzer
- Create new combined module
- Implement shared NER
- Test thoroughly
- **Expected: 25s → 15s** 🎯

**Day 6-7:** Optimize CLASSLA and DB connections
- Pre-load models at startup
- Implement connection pooling
- **Expected: 15s → 10s** 🎯

### Week 3: Advanced Optimizations (Phase 3)
**Day 1-3:** Implement Redis caching
- Set up Redis
- Add caching layer
- Test cache hit rates
- **Expected: 10s → 7s**

**Day 4-5:** GPU acceleration (if available)
- Configure CLASSLA for GPU
- Benchmark improvements
- **Expected: 7s → 5s**

**Day 6-7:** Testing and documentation
- End-to-end testing
- Performance benchmarking
- Update documentation

---

## Expected Final Performance

### Target Performance (After All Optimizations):
```
Document Processor (M1-4)      3s   ( 60%)  - Merged, optimized
Assertion Analyzer (M7-9)      1s   ( 20%)  - Merged, parallel, GPU
Knowledge Enrichment (M10)     1s   ( 20%)  - Batch, cached, parallel
----------------------------------------
TOTAL                          5s   (100%)  - 30x faster! 🚀
```

### Scalability:
- **1 document (311 articles):** 5s
- **10 documents:** 15s (parallel document processing)
- **100 documents:** 60s (batch + parallel)

---

## Alternative: Monolithic Approach

### Option B: Single "Legal Document Processor" Module
**Merge ALL modules into one**

**Pros:**
- No HTTP overhead
- Shared memory/models
- Simplest deployment
- Fastest possible (2-3s per document)

**Cons:**
- Less modular
- Harder to maintain
- Can't scale individual components
- All-or-nothing updates

**Recommendation:** Start with Phase 1-2, consider monolithic only if needed

---

## Monitoring & Metrics

### Key Metrics to Track:
1. **Processing Time per Document**
   - Target: < 5s for 300 articles
   - Alert if > 10s

2. **Throughput**
   - Target: > 12 documents/minute
   - Alert if < 6 documents/minute

3. **Memory Usage**
   - Target: < 2GB per module
   - Alert if > 4GB

4. **Cache Hit Rate** (Phase 3)
   - Target: > 60%
   - Alert if < 40%

5. **Error Rate**
   - Target: < 1%
   - Alert if > 5%

---

## Risk Mitigation

### Risks:
1. **Batch processing complexity** → Start with small batches (10-20)
2. **Memory issues with large batches** → Implement streaming
3. **CLASSLA GPU compatibility** → Test thoroughly, fallback to CPU
4. **Cache invalidation bugs** → Use TTL, version keys

### Rollback Plan:
- Keep current modular architecture
- Feature flags for new optimizations
- A/B testing for performance validation

---

## Success Criteria

### Phase 1 Success:
- ✅ Processing time < 60s per document
- ✅ All tests passing
- ✅ No accuracy degradation

### Phase 2 Success:
- ✅ Processing time < 15s per document
- ✅ Parallel processing working
- ✅ Memory usage stable

### Phase 3 Success:
- ✅ Processing time < 5s per document
- ✅ Cache hit rate > 60%
- ✅ System stable under load

---

## Conclusion

**Current:** 154s per document (unacceptable)
**After Phase 1:** 56s per document (acceptable)
**After Phase 2:** 10s per document (good)
**After Phase 3:** 5s per document (excellent) 🎯

**Recommended Approach:**
1. Start with Phase 1 (batch processing) - biggest impact, lowest risk
2. Move to Phase 2 (parallel + merge) - significant gains
3. Consider Phase 3 (caching + GPU) - if needed

**Timeline:** 3 weeks for full implementation
**Effort:** Medium (mostly refactoring existing code)
**Risk:** Low (incremental changes, easy rollback)