# Unified Database Implementation - GROOVE.AI

## Overview

This document describes the implementation of the unified database architecture for GROOVE.AI, consolidating all module databases into a single SQLite instance for improved performance and maintainability.

## Motivation

### Previous Architecture Issues
- **Multiple Database Files**: Each module had its own `.db` file (11+ separate databases)
- **Connection Overhead**: Each module maintained separate connection pools
- **Disk I/O Inefficiency**: Multiple files meant more disk operations
- **Backup Complexity**: Required backing up 11+ separate files
- **Transaction Isolation**: Cross-module transactions were impossible

### Performance Optimization Goals
According to [`GEN/PERFORMANCE_OPTIMIZATION_PLAN.md`](GEN/PERFORMANCE_OPTIMIZATION_PLAN.md:1), the unified database is part of Phase 1 optimizations targeting:
- Reduced HTTP overhead between modules
- Better connection pooling
- Atomic transactions across modules
- Simplified deployment and maintenance

## Architecture

### Unified Database Structure

**Single Database File**: `data/databases/grooveai_unified.db`

All modules now share this single database instance, with each module having its own tables:

```
grooveai_unified.db
├── file_reader_jobs
├── text_normalizer_jobs
├── latinizer_jobs
├── legal_parser_jobs
├── assertion_extraction_jobs
├── entity_recognition_jobs
├── condition_extraction_jobs
├── extracted_conditions
├── assertion_classification_jobs
├── classification_stats
├── ontology_terms
├── ontology_relationships
├── legal_references
├── term_definitions
├── enriched_assertions
├── embedding_jobs (embedding_generator)
└── embedding_jobs (vector_store)
```

### Key Components

#### 1. Unified Database Manager ([`shared/unified_database.py`](shared/unified_database.py:1))

**UnifiedDatabaseManager**: Singleton class managing the shared database connection
- Single connection pool for all modules
- SQLite optimizations (WAL mode, foreign keys, caching)
- Automatic table creation for all registered base classes
- Thread-safe session management

**ModuleDatabaseManager**: Generic base class for module-specific operations
- Inherits from `UnifiedDatabaseManager`
- Provides CRUD operations
- Type-safe with generics
- Automatic session handling

#### 2. Configuration ([`config.yaml`](config.yaml:39))

```yaml
database:
  # Unified database URL - all modules use this single database
  unified_url: "sqlite:///data/databases/grooveai_unified.db"
```

#### 3. Config Loader ([`shared/config_loader.py`](shared/config_loader.py:126))

New method added:
```python
def get_unified_database_url(self) -> str:
    """Get unified database URL (all modules use this single database)."""
    return self.get("database.unified_url", "sqlite:///data/databases/grooveai_unified.db")
```

## Updated Modules

### Modules Using Unified Database

✅ **Completed**:
1. [`modules/file_reader/database.py`](modules/file_reader/database.py:1) - File Reader
2. [`modules/text_normalizer/database.py`](modules/text_normalizer/database.py:1) - Text Normalizer
3. [`modules/latinizer/database.py`](modules/latinizer/database.py:1) - Latinizer
4. [`modules/legal_parser/database.py`](modules/legal_parser/database.py:1) - Legal Parser
5. [`modules/assertion_extractor/database.py`](modules/assertion_extractor/database.py:1) - Assertion Extractor
6. [`modules/entity_recognizer/database.py`](modules/entity_recognizer/database.py:1) - Entity Recognizer
7. [`modules/embedding_generator/database.py`](modules/embedding_generator/database.py:1) - Embedding Generator
8. [`modules/vector_store/database.py`](modules/vector_store/database.py:1) - Vector Store

⚠️ **Pending** (require custom migration due to complex schemas):
- [`modules/condition_extractor/database.py`](modules/condition_extractor/database.py:1) - Condition Extractor
- [`modules/assertion_classifier/database.py`](modules/assertion_classifier/database.py:1) - Assertion Classifier
- [`modules/knowledge_enrichment/database.py`](modules/knowledge_enrichment/database.py:1) - Knowledge Enrichment

### Migration Pattern

**Before** (separate database):
```python
from shared.database_base import BaseDatabaseManager
from shared.config_loader import config

class ModuleDatabaseManager(BaseDatabaseManager[JobModel]):
    def __init__(self):
        db_url = config.get_database_url("module_name")
        super().__init__(db_url, Base)
```

**After** (unified database):
```python
from shared.unified_database import unified_db, ModuleDatabaseManager
from shared.config_loader import config

class ModuleDatabaseManager(ModuleDatabaseManager[JobModel]):
    def __init__(self):
        unified_db_url = config.get_unified_database_url()
        unified_db.__init__(database_url=unified_db_url)
        
        super().__init__(
            unified_db=unified_db,
            base_class=Base,
            model_class=JobModel
        )
        
        unified_db.create_all_tables()
```

## Performance Benefits

### Expected Improvements

1. **Connection Pooling**
   - Before: 11+ separate connection pools
   - After: 1 shared connection pool
   - Benefit: Reduced memory overhead, better resource utilization

2. **Disk I/O**
   - Before: Multiple file operations across 11+ databases
   - After: Single file with optimized SQLite settings
   - Benefit: Faster reads/writes, better caching

3. **Transaction Management**
   - Before: Separate transactions per module
   - After: Atomic transactions across modules possible
   - Benefit: Data consistency, rollback capabilities

4. **Backup & Maintenance**
   - Before: 11+ files to backup/restore
   - After: 1 file to backup/restore
   - Benefit: Simplified operations, faster backups

### SQLite Optimizations Applied

```python
PRAGMA journal_mode=WAL        # Write-Ahead Logging for concurrency
PRAGMA foreign_keys=ON         # Enforce referential integrity
PRAGMA cache_size=-20000       # 20MB cache
PRAGMA synchronous=NORMAL      # Balance safety/performance
PRAGMA temp_store=MEMORY       # In-memory temp tables
PRAGMA mmap_size=30000000000   # Memory-mapped I/O
```

## Usage Examples

### Basic CRUD Operations

```python
from modules.file_reader.database import db
from modules.file_reader.models import FileReaderJob

# Create
job = FileReaderJob(file_path="test.pdf", status="pending")
created_job = db.create(job)

# Read
job = db.get_by_id(created_job.id)

# Update
job.status = "completed"
updated_job = db.update(job)

# Delete
db.delete(job.id)

# Count
total = db.count()
```

### Session Management

```python
from modules.file_reader.database import db

# Automatic session handling
with db.get_session() as session:
    job = session.query(FileReaderJob).first()
    job.status = "processing"
    # Automatic commit on exit
```

### Cross-Module Queries (Future Enhancement)

```python
# With unified database, cross-module queries become possible
with unified_db.get_session() as session:
    # Join data from multiple modules
    results = session.query(
        FileReaderJob, LatinizerJob
    ).join(
        LatinizerJob, 
        FileReaderJob.job_id == LatinizerJob.source_job_id
    ).all()
```

## Migration Strategy

### Phase 1: Core Modules (Completed)
- ✅ File Reader
- ✅ Text Normalizer
- ✅ Latinizer
- ✅ Legal Parser
- ✅ Assertion Extractor
- ✅ Entity Recognizer
- ✅ Embedding Generator
- ✅ Vector Store

### Phase 2: Complex Modules (In Progress)
- ⚠️ Condition Extractor (custom schema with relationships)
- ⚠️ Assertion Classifier (statistics tables)
- ⚠️ Knowledge Enrichment (ontology with complex relationships)

### Phase 3: Data Migration
1. Create migration script to copy data from old databases
2. Verify data integrity
3. Update all references
4. Archive old database files

## Testing

### Test Checklist

- [ ] Verify all modules can connect to unified database
- [ ] Test CRUD operations for each module
- [ ] Verify table creation and schema
- [ ] Test concurrent access from multiple modules
- [ ] Benchmark performance vs. separate databases
- [ ] Test backup and restore procedures
- [ ] Verify foreign key constraints
- [ ] Test transaction rollback scenarios

### Performance Benchmarks

**Target Metrics** (from optimization plan):
- Database connection time: < 10ms
- Query response time: < 50ms for simple queries
- Concurrent connections: Support 20+ simultaneous connections
- Memory usage: < 500MB for database operations

## Rollback Plan

If issues arise, rollback is straightforward:

1. Revert database.py files to use separate databases
2. Restore from backup of individual database files
3. Update config.yaml to use module-specific database URLs
4. Restart all modules

## Future Enhancements

### Planned Improvements

1. **Connection Pooling Tuning**
   - Monitor connection usage patterns
   - Adjust pool size based on load
   - Implement connection timeout handling

2. **Query Optimization**
   - Add indexes for frequently queried columns
   - Implement query result caching
   - Use prepared statements for common queries

3. **Monitoring & Metrics**
   - Track query performance
   - Monitor database size growth
   - Alert on slow queries or connection issues

4. **Advanced Features**
   - Implement database sharding if needed
   - Add read replicas for scaling
   - Consider PostgreSQL migration for production

## Conclusion

The unified database implementation is a critical first step in the performance optimization plan. By consolidating 11+ separate databases into a single, optimized SQLite instance, we achieve:

- **Better Performance**: Reduced overhead, optimized I/O
- **Simplified Operations**: Single file to manage
- **Improved Reliability**: Atomic transactions, better consistency
- **Easier Maintenance**: Centralized schema management

This foundation enables future optimizations including batch processing, parallel execution, and advanced caching strategies outlined in the performance optimization plan.

## References

- [`GEN/PERFORMANCE_OPTIMIZATION_PLAN.md`](GEN/PERFORMANCE_OPTIMIZATION_PLAN.md:1) - Overall optimization strategy
- [`shared/unified_database.py`](shared/unified_database.py:1) - Unified database implementation
- [`shared/config_loader.py`](shared/config_loader.py:1) - Configuration management
- [`config.yaml`](config.yaml:1) - System configuration

---

**Status**: Phase 1 Complete (8/11 modules migrated)  
**Next Steps**: Complete Phase 2 (complex modules), create migration script, run tests  
**Expected Completion**: Week 1 of optimization plan

*Made with Bob*