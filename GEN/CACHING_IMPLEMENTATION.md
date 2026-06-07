# Caching Implementation - Phase 3

## Overview

Implemented in-memory caching with LRU eviction and TTL support to optimize performance of computationally expensive operations, particularly CLASSLA NER processing in Module 10 (Knowledge Enrichment).

## Architecture

### Cache Manager (`shared/cache_manager.py`)

Thread-safe, singleton-based cache manager with the following features:

- **LRU Eviction**: Automatically removes least recently used entries when max_size is reached
- **TTL Support**: Entries expire after specified time-to-live duration
- **Thread Safety**: Uses `threading.Lock` for concurrent access protection
- **Statistics Tracking**: Monitors hits, misses, evictions, and hit rate
- **Singleton Pattern**: Global cache instance shared across application

### Key Components

```python
class CacheManager:
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Args:
            max_size: Maximum number of entries (default: 1000)
            default_ttl: Default time-to-live in seconds (default: 3600 = 1 hour)
        """
```

### Cache Operations

1. **get(key)** - Retrieve cached value with TTL checking
2. **set(key, value, ttl)** - Store value with optional TTL
3. **delete(key)** - Remove specific entry
4. **clear()** - Remove all entries
5. **get_stats()** - Get cache statistics
6. **get_or_compute(key, compute_fn, ttl)** - Cache-or-compute pattern

## Integration Points

### Module 10: Knowledge Enrichment

Integrated caching into CLASSLA NER processing:

**File**: `modules/knowledge_enrichment/service.py`

```python
class OntologyMatcher:
    def __init__(self, db: KnowledgeEnrichmentDatabase):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.cache = get_cache_manager(max_size=1000, default_ttl=3600)  # 1 hour TTL
    
    def _extract_additional_entities_with_classla(self, text: str) -> List[Dict[str, Any]]:
        """Extract additional entities using CLASSLA NER with caching"""
        # Generate cache key from text hash
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        cache_key = f"classla_entities:{text_hash}"
        
        # Try to get from cache
        cached_entities = self.cache.get(cache_key)
        if cached_entities is not None:
            self.logger.debug(f"Cache hit for CLASSLA entities (text hash: {text_hash[:8]})")
            return cached_entities
        
        # Process with CLASSLA (expensive operation)
        # ... CLASSLA processing ...
        
        # Cache the results
        self.cache.set(cache_key, additional_entities, ttl=3600)  # Cache for 1 hour
        
        return additional_entities
```

### Cache Key Generation

Uses MD5 hashing of input text for consistent cache keys:

```python
text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
cache_key = f"classla_entities:{text_hash}"
```

## API Endpoints

Added cache management endpoints to Module 10:

### GET /cache/stats

Returns cache statistics:

```json
{
  "status": "success",
  "cache_stats": {
    "size": 9,
    "max_size": 1000,
    "hits": 9,
    "misses": 9,
    "evictions": 0,
    "hit_rate": 50.0,
    "total_requests": 18
  }
}
```

### POST /cache/clear

Clears all cache entries:

```json
{
  "status": "success",
  "message": "Cache cleared successfully",
  "entries_cleared": 9
}
```

## Performance Results

### Test Scenario
- Document: `radni_odnosi_0008_000008.pdf`
- Assertions: 9
- Test runs: 2 (first without cache, second with cache)

### First Run (Cache Miss)
```
M10 processing time: 2917ms
Throughput: 3.08 assertions/sec
Cache stats:
  - hits: 0
  - misses: 9
  - hit_rate: 0%
```

### Second Run (Cache Hit)
```
M10 processing time: 17ms
Throughput: 525.21 assertions/sec
Cache stats:
  - hits: 9
  - misses: 9
  - hit_rate: 50%
```

### Performance Improvement

**171x faster!** (2917ms → 17ms)

- **First run**: 2917ms (CLASSLA NER processing)
- **Second run**: 17ms (cache retrieval)
- **Speedup**: 171x
- **Time saved**: 2900ms per batch

## Configuration

### Cache Settings

Default configuration in `OntologyMatcher.__init__()`:

```python
self.cache = get_cache_manager(
    max_size=1000,      # Maximum 1000 entries
    default_ttl=3600    # 1 hour TTL
)
```

### Adjustable Parameters

1. **max_size**: Maximum number of cached entries
   - Default: 1000
   - Adjust based on available memory
   - LRU eviction when limit reached

2. **default_ttl**: Time-to-live in seconds
   - Default: 3600 (1 hour)
   - Adjust based on data freshness requirements
   - Set to None for no expiration

3. **Cache key TTL**: Per-entry TTL override
   ```python
   self.cache.set(cache_key, value, ttl=7200)  # 2 hours
   ```

## Monitoring

### Cache Statistics

Monitor cache performance via `/cache/stats` endpoint:

- **size**: Current number of entries
- **max_size**: Maximum capacity
- **hits**: Number of cache hits
- **misses**: Number of cache misses
- **evictions**: Number of LRU evictions
- **hit_rate**: Percentage of requests served from cache
- **total_requests**: Total cache requests

### Logging

Cache operations are logged at DEBUG level:

```
DEBUG: Cache hit for CLASSLA entities (text hash: a1b2c3d4)
DEBUG: Cache miss for CLASSLA entities (text hash: e5f6g7h8)
```

## Best Practices

### When to Use Caching

✅ **Good candidates:**
- Expensive computations (CLASSLA NER, ML inference)
- Frequently accessed data
- Immutable or slowly changing data
- Deterministic operations (same input → same output)

❌ **Avoid caching:**
- Rapidly changing data
- User-specific data (unless keyed properly)
- Large objects (memory constraints)
- Non-deterministic operations

### Cache Key Design

1. **Use content hashing** for text-based keys
   ```python
   text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
   ```

2. **Include version/namespace** in keys
   ```python
   cache_key = f"classla_entities:v1:{text_hash}"
   ```

3. **Keep keys short** but descriptive
   ```python
   cache_key = f"ner:{text_hash[:16]}"
   ```

### Memory Management

1. **Set appropriate max_size** based on available memory
2. **Monitor cache size** via statistics
3. **Use TTL** to prevent stale data
4. **Clear cache** when needed via API endpoint

## Future Enhancements

### Potential Improvements

1. **Distributed Caching**: Redis/Memcached for multi-instance deployments
2. **Cache Warming**: Pre-populate cache with common queries
3. **Tiered Caching**: L1 (memory) + L2 (disk/Redis)
4. **Cache Invalidation**: Smart invalidation based on data changes
5. **Compression**: Compress large cached values
6. **Metrics Export**: Prometheus metrics for monitoring
7. **Cache Persistence**: Save/restore cache on restart

### Additional Caching Opportunities

Consider caching for:

1. **M9 (Assertion Classifier)**: Classification patterns
2. **M7 (Entity Recognizer)**: Duplicate text processing
3. **M4 (Legal Parser)**: Parsed legal structures
4. **Ontology Lookups**: Frequently accessed terms

## Testing

### Validation Steps

1. **First run**: Verify cache misses and CLASSLA processing
2. **Second run**: Verify cache hits and performance improvement
3. **Cache stats**: Check hit rate and statistics
4. **Cache clear**: Test manual cache clearing
5. **TTL expiration**: Verify entries expire after TTL

### Test Commands

```bash
# Run pipeline test
python test_batch_pipeline_complete.py "DOCUMENTS\DEV\onedoc\radni_odnosi_0008_000008.pdf"

# Check cache stats
curl http://localhost:8110/cache/stats

# Clear cache
curl -X POST http://localhost:8110/cache/clear

# Run again to verify cache rebuild
python test_batch_pipeline_complete.py "DOCUMENTS\DEV\onedoc\radni_odnosi_0008_000008.pdf"
```

## Conclusion

Caching implementation successfully achieved:

- ✅ **171x performance improvement** for M10 CLASSLA NER processing
- ✅ **Thread-safe** in-memory cache with LRU eviction
- ✅ **TTL support** for automatic expiration
- ✅ **Statistics tracking** for monitoring
- ✅ **API endpoints** for cache management
- ✅ **50% hit rate** in test scenario (9 hits / 18 requests)

The caching layer provides significant performance gains for expensive operations while maintaining data freshness through TTL and providing visibility through statistics and management endpoints.