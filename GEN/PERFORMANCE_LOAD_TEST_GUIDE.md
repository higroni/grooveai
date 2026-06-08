# Performance Load Test Guide

## Overview

Comprehensive performance testing framework for GROOVE.AI pipeline with 235 documents from the perftest dataset.

## Test Configuration

### Hardware Requirements
- **CPU**: Multi-core processor (4+ cores recommended)
- **RAM**: 16GB+ recommended
- **GPU**: NVIDIA GPU with CUDA support (optional, for M7/M10 acceleration)
- **Storage**: SSD recommended for faster I/O

### Software Requirements
- All 9 modules (M1-M4, M6-M10) running and healthy
- Python 3.8+
- Required packages: requests, pathlib

### Test Parameters
- **Documents**: 235 PDF files from `DOCUMENTS/DEV/perftest`
- **Parallel Workers**: 4 threads (configurable)
- **Batch Size**: 10 documents per batch
- **Timeout**: 300 seconds (5 minutes) per document
- **Pipeline**: Complete M1→M10 flow

## Test Script

### File: `test_performance_load.py`

**Features:**
- ✅ Parallel document processing (4 workers)
- ✅ Complete M1→M10 pipeline testing
- ✅ Comprehensive metrics collection
- ✅ Real-time progress tracking
- ✅ Detailed error reporting
- ✅ JSON results export
- ✅ Module-level performance breakdown

### Metrics Collected

#### 1. Test Information
- Start/end timestamps
- Total duration (seconds and minutes)

#### 2. Document Statistics
- Total documents processed
- Successful vs failed
- Success rate percentage

#### 3. Throughput Metrics
- Documents per second
- Documents per minute
- Documents per hour

#### 4. Latency Metrics
- Average document processing time
- Min/max processing times
- Median processing time
- Standard deviation

#### 5. Module Performance
For each module (M1-M10):
- Average processing time
- Min/max times
- Total calls

#### 6. Data Extraction
- Total assertions extracted
- Total entities recognized
- Total conditions extracted
- Total enriched assertions

#### 7. Error Tracking
- Error count
- Error details (first 10)
- Timestamps

## Running the Test

### Prerequisites

1. **Start all modules:**
```bash
python start_all_modules.py
```

2. **Verify module health:**
```bash
# The test script will check this automatically
# Or manually check:
curl http://localhost:8101/health  # M1
curl http://localhost:8102/health  # M2
# ... etc
```

### Execute Test

```bash
python test_performance_load.py
```

### Test Output

The script provides real-time progress:
```
[1/235] ✓ document1.pdf - 21.45s
[2/235] ✓ document2.pdf - 19.32s
[3/235] ✗ document3.pdf - Error: M4 failed
...
```

### Results

Results are saved to `performance_results/performance_test_YYYYMMDD_HHMMSS.json`

Example output:
```json
{
  "test_info": {
    "start_time": "2026-06-07T23:00:00",
    "end_time": "2026-06-07T23:45:00",
    "total_duration_seconds": 2700.0,
    "total_duration_minutes": 45.0
  },
  "documents": {
    "total": 235,
    "successful": 230,
    "failed": 5,
    "success_rate": 97.87
  },
  "throughput": {
    "documents_per_second": 0.09,
    "documents_per_minute": 5.11,
    "documents_per_hour": 306.67
  },
  "latency": {
    "avg_document_time_seconds": 11.74,
    "min_document_time_seconds": 8.23,
    "max_document_time_seconds": 45.67,
    "median_document_time_seconds": 10.89,
    "stdev_document_time_seconds": 3.45
  },
  "module_performance": {
    "M1": {"avg_time_seconds": 1.23, "min_time_seconds": 0.89, "max_time_seconds": 3.45},
    "M2": {"avg_time_seconds": 0.45, "min_time_seconds": 0.32, "max_time_seconds": 1.23},
    ...
  },
  "data_extracted": {
    "total_assertions": 1250,
    "total_entities": 3400,
    "total_conditions": 890,
    "enriched_assertions": 1200
  }
}
```

## Performance Targets

### Expected Performance (with optimizations)

Based on Phase 3 optimizations:
- **Caching**: 171x speedup for repeated content
- **Batch Processing**: 10-30x improvement
- **GPU Acceleration**: 2-5x speedup for NER tasks

### Target Metrics

**Throughput:**
- Minimum: 3-5 documents/minute
- Target: 5-10 documents/minute
- Optimal: 10+ documents/minute

**Latency:**
- Average: <15 seconds per document
- P50 (median): <12 seconds
- P95: <25 seconds
- P99: <40 seconds

**Success Rate:**
- Target: >95%
- Acceptable: >90%
- Critical: <85% (investigate issues)

**Module Performance:**
- M1 (File Reader): <2s
- M2 (Normalizer): <0.5s
- M3 (Latinizer): <0.5s
- M4 (Parser): <3s
- M6 (Assertions): <2s
- M7 (Entities): <3s (with GPU)
- M8 (Conditions): <2s
- M9 (Classifier): <1s
- M10 (Enrichment): <5s (with GPU)

## Optimization Strategies

### 1. Parallel Processing
- Current: 4 workers
- Adjust based on CPU cores: `MAX_WORKERS = os.cpu_count()`
- Monitor CPU usage to find optimal value

### 2. Batch Size
- Current: 10 documents
- Increase for better throughput: 20-50
- Decrease if memory issues occur

### 3. Caching
- Ensure cache is enabled in all modules
- Monitor cache hit rates
- Adjust TTL based on usage patterns

### 4. GPU Utilization
- Verify GPU is detected and used (M7, M10)
- Monitor GPU memory usage
- Consider batch size for GPU operations

### 5. Database Optimization
- Use unified database (already implemented)
- Monitor connection pool
- Consider read replicas for heavy loads

## Troubleshooting

### Common Issues

**1. Modules Not Responding**
```bash
# Check module status
python -c "import requests; print(requests.get('http://localhost:8101/health').json())"

# Restart modules
python start_all_modules.py
```

**2. Timeout Errors**
- Increase `TIMEOUT` value in script
- Check module logs for bottlenecks
- Verify system resources (CPU, RAM, GPU)

**3. Memory Issues**
- Reduce `MAX_WORKERS`
- Reduce `BATCH_SIZE`
- Monitor with: `nvidia-smi` (GPU) or Task Manager (RAM)

**4. High Error Rate**
- Check module logs
- Verify document quality
- Test with single document first

### Performance Degradation

If performance degrades over time:
1. Check cache memory usage
2. Monitor database connections
3. Restart modules periodically
4. Check for memory leaks in logs

## Monitoring During Test

### System Resources
```bash
# CPU and RAM
Task Manager (Windows) or top (Linux)

# GPU
nvidia-smi -l 1  # Update every second
```

### Module Health
```bash
# Check all modules
for port in 8101 8102 8103 8105 8106 8107 8108 8109 8110; do
  curl http://localhost:$port/health
done
```

### Cache Statistics
```bash
# Check cache stats for each module
curl http://localhost:8106/cache/stats  # M6
curl http://localhost:8107/cache/stats  # M7
# ... etc
```

## Analysis and Reporting

### Key Questions to Answer

1. **What is the average throughput?**
   - Documents per minute/hour
   - Compare to target metrics

2. **Which modules are bottlenecks?**
   - Identify slowest modules
   - Focus optimization efforts

3. **What is the success rate?**
   - Acceptable: >95%
   - Investigate failures if <90%

4. **How does performance scale?**
   - Linear with workers?
   - Diminishing returns?

5. **Are optimizations working?**
   - Cache hit rates
   - GPU utilization
   - Batch processing benefits

### Generating Reports

After test completion:
1. Review JSON results file
2. Calculate key metrics
3. Compare to baseline/targets
4. Identify optimization opportunities
5. Document findings

## Next Steps

After performance testing:
1. ✅ Analyze results
2. ✅ Identify bottlenecks
3. ✅ Implement optimizations
4. ✅ Re-test and compare
5. ✅ Document improvements
6. ⏳ Set up continuous monitoring (Prometheus/Grafana)

## Conclusion

This performance load test provides comprehensive insights into system behavior under realistic load conditions. Use the results to:
- Validate optimization efforts
- Identify bottlenecks
- Plan capacity
- Set SLAs
- Guide future improvements

**Status**: Ready for execution with 235 documents