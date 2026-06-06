# Shared Utilities

This directory contains shared utilities used across all GROOVE.AI modules.

## Components

### 1. Configuration Loader (`config_loader.py`)

Centralized configuration management using singleton pattern.

**Features:**
- Single source of truth for all configuration
- Reads from `config.yaml`
- Provides type-safe access to configuration values
- Singleton pattern ensures consistency

**Usage:**
```python
from shared.config_loader import config

# Get module port
port = config.get_module_port("file_reader")  # Returns 8101

# Get database URL
db_url = config.get_module_database("file_reader")

# Get sample file path
sample_file = config.get_sample_file()

# Get log level
log_level = config.get_log_level()
```

### 2. Logger (`logger.py`)

Standardized logging for all modules.

**Features:**
- Module-specific log files in `data/logs/`
- Consistent formatting across all modules
- Both file and console logging
- Windows-safe (no emojis, proper encoding)
- Daily log rotation (one file per day)

**Usage:**
```python
from shared.logger import get_module_logger

# Create logger
logger = get_module_logger("file_reader", "INFO")

# Log messages
logger.info("Module started")
logger.debug("Processing file: document.pdf")
logger.warning("Large file detected")
logger.error("Failed to read file", exc_info=True)
logger.critical("System failure")
```

**Log Format:**
- File: `2026-06-06 14:05:20 - file_reader - INFO - Module started`
- Console: `[INFO] file_reader: Module started`

**Log Files:**
- Location: `data/logs/`
- Naming: `{module_name}_{YYYYMMDD}.log`
- Example: `file_reader_20260606.log`

### 3. Database Base (`database_base.py`)

Base database manager class for all modules.

**Features:**
- Session management with context managers
- Common CRUD operations
- Connection pooling
- SQLite optimizations (WAL mode, foreign keys)
- Automatic table creation
- Type-safe generic operations

**Usage:**
```python
from shared.database_base import BaseDatabaseManager
from sqlalchemy.orm import DeclarativeBase

# Define your base
class Base(DeclarativeBase):
    pass

# Define your models
class MyModel(Base):
    __tablename__ = "my_table"
    # ... fields ...

# Create database manager
class MyDatabaseManager(BaseDatabaseManager):
    def __init__(self, db_url: str):
        super().__init__(db_url, Base)

# Use the manager
db = MyDatabaseManager("sqlite:///data/databases/my_module.db")

# CRUD operations
obj = MyModel(name="test")
created = db.create(obj)
retrieved = db.get_by_id(MyModel, created.id)
all_records = db.get_all(MyModel, limit=10, offset=0)
count = db.count(MyModel)
deleted = db.delete(MyModel, obj_id)
```

**Context Manager:**
```python
# Manual session management
with db.get_session() as session:
    obj = session.query(MyModel).first()
    obj.name = "updated"
    # Automatic commit on exit
```

## File Structure

```
shared/
├── __init__.py
├── config_loader.py      # Configuration management
├── logger.py             # Logging utilities
├── database_base.py      # Database base class
└── README.md            # This file
```

## Design Principles

1. **DRY (Don't Repeat Yourself)**: Common functionality in one place
2. **Consistency**: All modules use the same patterns
3. **Type Safety**: Proper type hints and generic types
4. **Error Handling**: Comprehensive error handling and logging
5. **Windows Compatibility**: No emojis, proper encoding
6. **Testability**: Easy to mock and test

## Integration with Modules

All modules should use these shared utilities:

```python
# In module's __init__.py or main.py
from shared.config_loader import config
from shared.logger import get_module_logger
from shared.database_base import BaseDatabaseManager

# Initialize
logger = get_module_logger("my_module")
port = config.get_module_port("my_module")
db_url = config.get_module_database("my_module")
```

## Testing

Each utility includes example usage in `if __name__ == "__main__"` block:

```bash
# Test config loader
python -m shared.config_loader

# Test logger
python -m shared.logger

# Test database base
python -m shared.database_base
```

## Dependencies

All shared utilities use only standard library and core dependencies:
- `pyyaml` - Configuration parsing
- `sqlalchemy` - Database ORM
- Standard library: `logging`, `pathlib`, `contextlib`, etc.

## Best Practices

1. **Always use shared logger** instead of print statements
2. **Always use config_loader** instead of hardcoding values
3. **Extend BaseDatabaseManager** for module-specific database operations
4. **Use context managers** for database sessions
5. **Log errors with exc_info=True** for full tracebacks
6. **Create module-specific loggers** with appropriate log levels

## Future Enhancements

Potential additions to shared utilities:
- HTTP client wrapper for inter-module communication
- Metrics collection and monitoring
- Caching utilities
- Validation utilities
- Error response standardization
- Rate limiting utilities