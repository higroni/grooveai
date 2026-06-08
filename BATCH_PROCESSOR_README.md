# GROOVE.AI Batch Processor

High-performance batch document processor that eliminates HTTP overhead and uses multiprocessing for maximum throughput.

## Performance Target

- **Goal**: Process 8,000 documents in 2-3 hours (2-3s per document)
- **Current HTTP-based**: ~3 minutes per document
- **Required Speedup**: **60x improvement**

## Architecture

### Key Improvements Over HTTP-based Pipeline

1. **Direct Function Calls** - No HTTP overhead (saves 50-100s per document)
2. **Multiprocessing** - Process multiple documents in parallel
3. **Shared Models** - Single CLASSLA/embedding model instance per worker
4. **Batch Database Operations** - Minimize I/O overhead
5. **Unified Database** - Single database for all modules

### Processing Flow

```
Input Directory
    ↓
Document Queue Manager
    ↓
Worker Pool (N processes)
    ↓
Pipeline Instance (per worker)
    ├─ M1: File Reader
    ├─ M2: Text Normalizer
    ├─ M3: Latinizer
    ├─ M4: Legal Parser
    ├─ M6: Assertion Extractor
    ├─ M7: Entity Recognizer (GPU)
    ├─ M8: Condition Extractor
    ├─ M9: Assertion Classifier
    └─ M10: Knowledge Enrichment (GPU)
    ↓
Unified Database
```

## Usage

### Basic Usage

```bash
# Process all PDFs in a directory
python batch_processor.py /path/to/documents

# Process with custom worker count
python batch_processor.py /path/to/documents --workers 8

# Process with custom batch size
python batch_processor.py /path/to/documents --batch-size 20

# Save results to specific directory
python batch_processor.py /path/to/documents --output /path/to/results
```

### Advanced Usage

```python
from batch_processor import BatchProcessor

# Create processor
processor = BatchProcessor(
    num_workers=8,          # Number of parallel workers
    batch_size=10,          # Documents per batch
    unified_db_path="data/databases/grooveai_unified.db"
)

# Process documents
document_paths = [
    "doc1.pdf",
    "doc2.pdf",
    "doc3.pdf"
]

stats = processor.process_documents(
    document_paths=document_paths,
    output_dir="results/"
)

print(f"Processed {stats['successful']} documents")
print(f"Average time: {stats['average_time_per_document']:.2f}s")
print(f"Throughput: {stats['documents_per_second']:.2f} docs/s")
```

## Configuration

### Worker Count

- **Default**: CPU cores - 1
- **Recommended**: 
  - For CPU-bound tasks: CPU cores - 1
  - For GPU-bound tasks: 2-4 (to avoid GPU contention)
  - For I/O-bound tasks: 2 × CPU cores

### Batch Size

- **Default**: 10 documents
- **Recommended**:
  - Small documents (<10 pages): 20-50
  - Medium documents (10-50 pages): 10-20
  - Large documents (>50 pages): 5-10

## Performance Optimization

### Phase 1: Eliminate HTTP Overhead
- Direct Python function calls
- **Expected**: 3 min → 30s per document (6x speedup)

### Phase 2: Add Multiprocessing
- Process 8 documents in parallel
- **Expected**: 30s → 4s per document (7.5x speedup)

### Phase 3: Optimize GPU Usage
- Batch GPU operations
- Share models across workers
- **Expected**: 4s → 2-3s per document (1.5x speedup)

### Total Expected Speedup: **60-90x**

## Output

### Statistics File

`batch_processing_stats.json`:
```json
{
  "total_documents": 8000,
  "successful": 7998,
  "failed": 2,
  "success_rate": 99.98,
  "total_time_seconds": 7200,
  "average_time_per_document": 0.9,
  "documents_per_second": 1.11,
  "failed_documents": ["doc1.pdf", "doc2.pdf"]
}
```

### Database

All results stored in unified database:
- `file_reader_jobs` - Document metadata
- `extraction_jobs` - Extracted assertions
- `recognition_jobs` - Recognized entities
- `condition_extraction_jobs` - Extracted conditions
- `classification_jobs` - Assertion classifications
- `enriched_assertions` - Final enriched data

## Monitoring

### Progress Tracking

The processor logs progress every 10 documents:
```
[10/8000] Progress: 10/8000 (0.1%) - Rate: 1.2 docs/s - ETA: 110.0 min
[20/8000] Progress: 20/8000 (0.3%) - Rate: 1.3 docs/s - ETA: 102.0 min
```

### Real-time Statistics

```bash
# Watch progress in real-time
tail -f batch_processing.log
```

## Error Handling

### Failed Documents

Failed documents are logged and saved to statistics file:
```json
{
  "failures": [
    {
      "document": "problematic.pdf",
      "path": "/path/to/problematic.pdf",
      "error": "PDF parsing error: corrupted file",
      "processing_time": 5.2
    }
  ]
}
```

### Recovery

To reprocess failed documents:
```bash
# Extract failed document paths from stats
python -c "import json; stats = json.load(open('batch_processing_stats.json')); print('\n'.join(stats['failed_documents']))" > failed.txt

# Reprocess
python batch_processor.py failed.txt
```

## Implementation Status

### ✅ Completed
- [x] Batch processor skeleton
- [x] Multiprocessing infrastructure
- [x] Progress tracking
- [x] Statistics collection
- [x] CLI interface

### 🚧 In Progress
- [ ] Direct function call implementation
- [ ] Pipeline processing logic
- [ ] GPU optimization

### 📋 Planned
- [ ] Checkpoint/resume functionality
- [ ] Distributed processing (multiple machines)
- [ ] Real-time dashboard
- [ ] Performance profiling

## Next Steps

1. **Implement Direct Function Calls**
   - Extract core logic from module services
   - Create pipeline processor class
   - Test with single document

2. **Add Pipeline Logic**
   - Integrate all M1-M10 modules
   - Handle errors gracefully
   - Test with 10 documents

3. **Optimize Performance**
   - Profile bottlenecks
   - Optimize GPU usage
   - Test with 100 documents

4. **Scale Testing**
   - Test with 1,000 documents
   - Measure actual speedup
   - Tune parameters

5. **Production Run**
   - Process all 8,000 documents
   - Validate results
   - Generate final statistics

## Troubleshooting

### Out of Memory

```bash
# Reduce worker count
python batch_processor.py docs/ --workers 4

# Reduce batch size
python batch_processor.py docs/ --batch-size 5
```

### GPU Out of Memory

```bash
# Use fewer workers for GPU-bound tasks
python batch_processor.py docs/ --workers 2
```

### Slow Performance

```bash
# Check system resources
htop  # CPU usage
nvidia-smi  # GPU usage

# Profile single document
python -m cProfile batch_processor.py single_doc.pdf
```

## Support

For issues or questions:
1. Check logs: `batch_processing.log`
2. Review statistics: `batch_processing_stats.json`
3. Test with single document first
4. Check system resources (CPU, GPU, RAM, disk)