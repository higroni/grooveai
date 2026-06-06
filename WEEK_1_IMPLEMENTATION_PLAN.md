# ZAIKON V2 - Week 1 Implementation Plan

**Nedelja**: 1 od 7  
**Fokus**: Core Infrastructure & Domain Layer  
**Trajanje**: 7 dana  
**Cilj**: Postaviti čvrstu osnovu projekta sa domain entitetima

---

## 📋 Pregled Nedelje 1

### Glavni Ciljevi
1. ✅ Kreirati kompletnu folder strukturu (DDD)
2. ✅ Setup Python backend projekat
3. ✅ Setup React frontend projekat
4. ✅ Implementirati konfiguraciju i logging
5. ✅ Kreirati database schema
6. ✅ Implementirati sve domain entitete
7. ✅ Implementirati value objects
8. ✅ Definisati domain events
9. ✅ Napisati unit testove

### Deliverables
- [ ] Funkcionalan Python projekat sa dependency management
- [ ] Funkcionalan React projekat sa TypeScript
- [ ] Centralizovana konfiguracija (Settings)
- [ ] Logging sistem sa verbosity nivoima
- [ ] SQLite database sa kompletnom šemom
- [ ] Svi domain entiteti (12 klasa)
- [ ] Svi value objects (15+ klasa)
- [ ] Svi domain events (10+ klasa)
- [ ] Unit testovi (80%+ coverage)

---

## Dan 1: Project Setup (Backend)

### Zadaci

#### 1.1 Kreirati Folder Strukturu
```bash
# Root folder
mkdir -p ZAIKON
cd ZAIKON

# Backend struktura (DDD)
mkdir -p backend/zaikon/{core,domain,application,infrastructure,presentation}
mkdir -p backend/zaikon/domain/{document_management,corpus_management,knowledge_representation,conflict_detection,draft_review,configuration}
mkdir -p backend/zaikon/domain/document_management/{entities,value_objects,services,events}
mkdir -p backend/zaikon/domain/corpus_management/{entities,value_objects,services,events}
mkdir -p backend/zaikon/domain/knowledge_representation/{entities,value_objects,services,events}
mkdir -p backend/zaikon/domain/conflict_detection/{entities,value_objects,services,events}
mkdir -p backend/zaikon/domain/draft_review/{entities,services,events}
mkdir -p backend/zaikon/domain/configuration/{entities,services}
mkdir -p backend/zaikon/application/{use_cases,dtos,services}
mkdir -p backend/zaikon/infrastructure/{repositories,external_services,persistence}
mkdir -p backend/zaikon/infrastructure/persistence/migrations
mkdir -p backend/zaikon/presentation/api/{routers,dependencies,middleware}
mkdir -p backend/zaikon/presentation/websocket
mkdir -p backend/tests/{unit,integration,e2e}
mkdir -p backend/scripts

# Data directories
mkdir -p data/{qdrant_storage,logs}
mkdir -p DOCUMENTS/{corpus,drafts}

# Frontend struktura
mkdir -p frontend/src/{components,hooks,services,stores,types,utils}
mkdir -p frontend/src/components/{corpus,draft,findings,common}
mkdir -p frontend/public

# Documentation
mkdir -p docs
```

#### 1.2 Python Project Setup (pyproject.toml)
```toml
[project]
name = "zaikon"
version = "2.0.0"
description = "AI-assisted legislative compliance review platform (V2 - DDD Architecture)"
requires-python = ">=3.12"
authors = [
    {name = "ZAIKON Team"}
]
readme = "README.md"
license = {text = "MIT"}

dependencies = [
    # Web Framework
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "python-multipart>=0.0.6",
    
    # Data Validation
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    
    # Database
    "sqlalchemy>=2.0.0",
    "alembic>=1.13.0",
    
    # Vector Store
    "qdrant-client>=1.7.0",
    
    # Document Processing
    "pymupdf>=1.24.13",
    "python-docx>=1.1.2",
    
    # NLP & Embeddings
    "torch>=2.5.1",
    "transformers>=4.36.0",
    "sentence-transformers>=2.2.2",
    "stanza>=1.9.2",
    
    # LLM Integration
    "ollama>=0.1.0",
    
    # Utilities
    "python-dateutil>=2.8.2",
    "httpx>=0.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
    "black>=23.11.0",
]

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=zaikon --cov-report=html --cov-report=term"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.black]
line-length = 100
target-version = ['py312']
```

#### 1.3 Install Dependencies
```bash
cd backend
pip install -e ".[dev]"
```

#### 1.4 Create __init__.py Files
```bash
# Create all __init__.py files
find backend/zaikon -type d -exec touch {}/__init__.py \;
```

---

## Dan 2: Configuration & Logging

### Zadaci

#### 2.1 Core Configuration (backend/zaikon/core/config.py)
```python
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Literal

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "ZAIKON"
    app_version: str = "2.0.0"
    environment: Literal["development", "production", "test"] = "development"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8100
    api_prefix: str = "/api/v1"
    
    # Database
    database_path: str = "data/zaikon.db"
    database_echo: bool = False  # SQLAlchemy echo
    
    # Qdrant Vector Store
    qdrant_path: str = "data/qdrant_storage"
    qdrant_collection_corpus: str = "corpus_assertions"
    qdrant_collection_draft: str = "draft_assertions"
    qdrant_vector_size: int = 1024
    
    # Embedding Model
    embedding_model: str = "BAAI/bge-m3"
    embedding_device: str = "cuda"  # or "cpu"
    embedding_batch_size: int = 32
    
    # Reranker Model
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_device: str = "cuda"
    
    # NER Model
    ner_model: str = "sr"  # Stanza Serbian
    ner_device: str = "cpu"
    
    # LLM (Ollama)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:latest"
    ollama_temperature: float = 0.7
    ollama_timeout: int = 120
    
    # Hybrid Search Weights
    vector_weight: float = 0.45
    keyword_weight: float = 0.35
    graph_weight: float = 0.20
    
    # Performance
    max_workers: int = 4
    batch_size_documents: int = 100
    batch_size_embeddings: int = 32
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_file: str = "data/logs/zaikon.log"
    log_format: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    
    # Verbosity (0=silent, 1=normal, 2=debug, 3=trace)
    verbosity: int = 1
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()
```

#### 2.2 Logging Setup (backend/zaikon/core/logging.py)
```python
import logging
import sys
from pathlib import Path
from typing import Optional
from zaikon.core.config import settings

def setup_logging(
    verbosity: Optional[int] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Setup logging with console and file handlers.
    
    Args:
        verbosity: 0=ERROR, 1=INFO, 2=DEBUG, 3=TRACE (default from settings)
        log_file: Path to log file (default from settings)
    """
    verbosity = verbosity if verbosity is not None else settings.verbosity
    log_file = log_file or settings.log_file
    
    # Determine log level
    if verbosity == 0:
        level = logging.ERROR
    elif verbosity == 1:
        level = logging.INFO
    elif verbosity == 2:
        level = logging.DEBUG
    else:  # verbosity >= 3
        level = logging.DEBUG
    
    # Create formatter
    formatter = logging.Formatter(
        settings.log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # File handler
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Always DEBUG in file
    file_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()  # Remove existing handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info(f"ZAIKON {settings.app_version} - Logging initialized")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Verbosity: {verbosity}")
    logger.info(f"Log file: {log_file}")
    logger.info("="*80)

def get_logger(name: str) -> logging.Logger:
    """Get logger for module."""
    return logging.getLogger(name)
```

#### 2.3 Custom Exceptions (backend/zaikon/core/exceptions.py)
```python
class ZaikonException(Exception):
    """Base exception for ZAIKON."""
    pass

class ConfigurationError(ZaikonException):
    """Configuration error."""
    pass

class DatabaseError(ZaikonException):
    """Database error."""
    pass

class DocumentProcessingError(ZaikonException):
    """Document processing error."""
    pass

class EmbeddingGenerationError(ZaikonException):
    """Embedding generation error."""
    pass

class ConflictDetectionError(ZaikonException):
    """Conflict detection error."""
    pass

class ValidationError(ZaikonException):
    """Validation error."""
    pass

class NotFoundError(ZaikonException):
    """Resource not found."""
    pass
```

---

## Dan 3: Database Schema

### Zadaci

#### 3.1 Database Connection (backend/zaikon/infrastructure/persistence/sqlite_connection.py)
```python
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from zaikon.core.config import settings
from zaikon.core.logging import get_logger

logger = get_logger(__name__)

# Base class for models
Base = declarative_base()

# Engine
def create_db_engine():
    """Create SQLAlchemy engine."""
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    engine = create_engine(
        f"sqlite:///{db_path}",
        echo=settings.database_echo,
        connect_args={"check_same_thread": False}
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    return engine

# Session factory
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()

def init_database():
    """Initialize database with schema."""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")
```

#### 3.2 Database Models (backend/zaikon/infrastructure/persistence/models.py)
```python
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from zaikon.infrastructure.persistence.sqlite_connection import Base

class DomainModel(Base):
    """Domain (pravna oblast)."""
    __tablename__ = "domains"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    
    # Relationships
    ontology_sets = relationship("OntologySetModel", back_populates="domain")
    conflict_rule_sets = relationship("ConflictRuleSetModel", back_populates="domain")
    corpora = relationship("CorpusModel", back_populates="domain")

class OntologySetModel(Base):
    """Ontology Set (verzionisana ontologija)."""
    __tablename__ = "ontology_sets"
    
    id = Column(String, primary_key=True)
    domain_id = Column(String, ForeignKey("domains.id"), nullable=False)
    version = Column(String, nullable=False)
    name = Column(String, nullable=False)
    language = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    domain = relationship("DomainModel", back_populates="ontology_sets")
    terms = relationship("OntologyTermModel", back_populates="ontology_set")

class OntologyTermModel(Base):
    """Ontology Term."""
    __tablename__ = "ontology_terms"
    
    id = Column(String, primary_key=True)
    ontology_set_id = Column(String, ForeignKey("ontology_sets.id"), nullable=False)
    name = Column(String, nullable=False)
    term = Column(String, nullable=False)
    language = Column(String, nullable=False)
    rule = Column(Text)
    term_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ontology_set = relationship("OntologySetModel", back_populates="terms")

class ConflictRuleSetModel(Base):
    """Conflict Rule Set (verzionisana pravila)."""
    __tablename__ = "conflict_rule_sets"
    
    id = Column(String, primary_key=True)
    domain_id = Column(String, ForeignKey("domains.id"), nullable=False)
    version = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    domain = relationship("DomainModel", back_populates="conflict_rule_sets")
    rules = relationship("ConflictRuleModel", back_populates="rule_set")

class ConflictRuleModel(Base):
    """Conflict Rule."""
    __tablename__ = "conflict_rules"
    
    id = Column(String, primary_key=True)
    rule_set_id = Column(String, ForeignKey("conflict_rule_sets.id"), nullable=False)
    conflict_type = Column(String, nullable=False)
    category = Column(String, nullable=False)
    pattern = Column(Text)
    severity = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rule_set = relationship("ConflictRuleSetModel", back_populates="rules")

class ParamSetModel(Base):
    """Parameter Set (za reproducibilnost)."""
    __tablename__ = "param_sets"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    llm_model = Column(String)
    llm_temperature = Column(Float)
    ontology_set_id = Column(String, ForeignKey("ontology_sets.id"))
    conflict_rule_set_id = Column(String, ForeignKey("conflict_rule_sets.id"))
    embedding_model = Column(String)
    vector_weight = Column(Float)
    keyword_weight = Column(Float)
    graph_weight = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class CorpusModel(Base):
    """Corpus (kolekcija dokumenata)."""
    __tablename__ = "corpora"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    domain_id = Column(String, ForeignKey("domains.id"), nullable=False)
    language = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)
    
    # Relationships
    domain = relationship("DomainModel", back_populates="corpora")
    runs = relationship("CorpusRunModel", back_populates="corpus")
    documents = relationship("DocumentModel", back_populates="corpus")

class CorpusRunModel(Base):
    """Corpus Run (tracking izvršavanja)."""
    __tablename__ = "corpus_runs"
    
    id = Column(String, primary_key=True)
    corpus_id = Column(String, ForeignKey("corpora.id"), nullable=False)
    param_set_id = Column(String, ForeignKey("param_sets.id"))
    ontology_set_id = Column(String, ForeignKey("ontology_sets.id"))
    conflict_rule_set_id = Column(String, ForeignKey("conflict_rule_sets.id"))
    status = Column(String, default="running")
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    stats = Column(JSON)
    
    # Relationships
    corpus = relationship("CorpusModel", back_populates="runs")

class DocumentModel(Base):
    """Document (pravni dokument)."""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    corpus_id = Column(String, ForeignKey("corpora.id"), nullable=False)
    corpus_run_id = Column(String, ForeignKey("corpus_runs.id"))
    language = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    title = Column(String)
    document_type = Column(String)
    is_draft = Column(Boolean, default=False)
    canonical_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    corpus = relationship("CorpusModel", back_populates="documents")
    legal_units = relationship("LegalUnitModel", back_populates="document")

class LegalUnitModel(Base):
    """Legal Unit (pravna jedinica)."""
    __tablename__ = "legal_units"
    
    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    corpus_run_id = Column(String, ForeignKey("corpus_runs.id"))
    language = Column(String, nullable=False)
    unit_type = Column(String, nullable=False)
    number = Column(Integer, nullable=False)
    title = Column(String)
    content = Column(Text, nullable=False)
    parent_id = Column(String, ForeignKey("legal_units.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("DocumentModel", back_populates="legal_units")
    assertions = relationship("AssertionModel", back_populates="legal_unit")
    parent = relationship("LegalUnitModel", remote_side=[id])

class AssertionModel(Base):
    """Assertion (normativna tvrdnja)."""
    __tablename__ = "assertions"
    
    id = Column(String, primary_key=True)
    legal_unit_id = Column(String, ForeignKey("legal_units.id"), nullable=False)
    corpus_run_id = Column(String, ForeignKey("corpus_runs.id"))
    language = Column(String, nullable=False)
    assertion_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    entities = Column(JSON)
    conditions = Column(JSON)
    exceptions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    legal_unit = relationship("LegalUnitModel", back_populates="assertions")
    embedding = relationship("EmbeddingModel", back_populates="assertion", uselist=False)

class EmbeddingModel(Base):
    """Embedding (vektorska reprezentacija)."""
    __tablename__ = "embeddings"
    
    id = Column(String, primary_key=True)
    assertion_id = Column(String, ForeignKey("assertions.id"), nullable=False)
    corpus_run_id = Column(String, ForeignKey("corpus_runs.id"))
    language = Column(String, nullable=False)
    vector = Column(JSON, nullable=False)  # List[float]
    model = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assertion = relationship("AssertionModel", back_populates="embedding")

class DraftReviewModel(Base):
    """Draft Review."""
    __tablename__ = "draft_reviews"
    
    id = Column(String, primary_key=True)
    draft_document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    corpus_id = Column(String, ForeignKey("corpora.id"), nullable=False)
    param_set_id = Column(String, ForeignKey("param_sets.id"))
    status = Column(String, default="pending")
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    # Relationships
    findings = relationship("FindingModel", back_populates="draft_review")

class FindingModel(Base):
    """Finding (detektovani konflikt)."""
    __tablename__ = "findings"
    
    id = Column(String, primary_key=True)
    draft_review_id = Column(String, ForeignKey("draft_reviews.id"), nullable=False)
    assertion1_id = Column(String, ForeignKey("assertions.id"), nullable=False)
    assertion2_id = Column(String, ForeignKey("assertions.id"), nullable=False)
    conflict_rule_id = Column(String, ForeignKey("conflict_rules.id"), nullable=False)
    severity = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    explanation = Column(Text)
    recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    draft_review = relationship("DraftReviewModel", back_populates="findings")
    resolution = relationship("ResolutionModel", back_populates="finding", uselist=False)

class ResolutionModel(Base):
    """Resolution (rešenje konflikta)."""
    __tablename__ = "resolutions"
    
    id = Column(String, primary_key=True)
    finding_id = Column(String, ForeignKey("findings.id"), nullable=False)
    status = Column(String, nullable=False)
    decision = Column(String)
    comment = Column(Text)
    resolved_by = Column(String)
    resolved_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    finding = relationship("FindingModel", back_populates="resolution")
```

---

## Dan 4-5: Domain Entities

### Zadaci

#### 4.1 Document Management Entities

**backend/zaikon/domain/document_management/entities/document.py**
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

@dataclass
class Document:
    """Document aggregate root."""
    
    id: UUID = field(default_factory=uuid4)
    corpus_id: UUID = field(default_factory=uuid4)
    corpus_run_id: Optional[UUID] = None
    language: str = "sr"
    filename: str = ""
    title: Optional[str] = None
    document_type: Optional[str] = None
    is_draft: bool = False
    canonical_json: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    legal_units: List['LegalUnit'] = field(default_factory=list)
    
    def add_legal_unit(self, legal_unit: 'LegalUnit') -> None:
        """Add legal unit to document."""
        self.legal_units.append(legal_unit)
    
    def get_legal_unit_by_id(self, unit_id: UUID) -> Optional['LegalUnit']:
        """Get legal unit by ID."""
        return next((u for u in self.legal_units if u.id == unit_id), None)
    
    def count_assertions(self) -> int:
        """Count total assertions in document."""
        return sum(len(unit.assertions) for unit in self.legal_units)
```

**backend/zaikon/domain/document_management/entities/legal_unit.py**
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

@dataclass
class LegalUnit:
    """Legal unit entity."""
    
    id: UUID = field(default_factory=uuid4)
    document_id: UUID = field(default_factory=uuid4)
    corpus_run_id: Optional[UUID] = None
    language: str = "sr"
    unit_type: str = "clan"  # clan, stav, tacka
    number: int = 1
    title: str = ""
    content: str = ""
    parent_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    assertions: List['Assertion'] = field(default_factory=list)
    
    def add_assertion(self, assertion: 'Assertion') -> None:
        """Add assertion to legal unit."""
        self.assertions.append(assertion)
    
    def get_assertion_by_id(self, assertion_id: UUID) -> Optional['Assertion']:
        """Get assertion by ID."""
        return next((a for a in self.assertions if a.id == assertion_id), None)
```

**backend/zaikon/domain/document_management/entities/assertion.py**
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import UUID, uuid4

@dataclass
class Assertion:
    """Assertion entity."""
    
    id: UUID = field(default_factory=uuid4)
    legal_unit_id: UUID = field(default_factory=uuid4)
    corpus_run_id: Optional[UUID] = None
    language: str = "sr"
    assertion_type: str = "obaveza"  # obaveza, zabrana, pravo
    content: str = ""
    entities: Dict[str, Any] = field(default_factory=dict)
    conditions: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    embedding: Optional['Embedding'] = None
    
    def set_embedding(self, embedding: 'Embedding') -> None:
        """Set embedding for assertion."""
        self.embedding = embedding
    
    def has_embedding(self) -> bool:
        """Check if assertion has embedding."""
        return self.embedding is not None
```

#### 4.2 Implementirati Ostale Entitete
- Corpus, CorpusRun (Corpus Management)
- OntologySet, OntologyTerm, Embedding (Knowledge Representation)
- ConflictRuleSet, ConflictRule, Finding, Resolution (Conflict Detection)
- DraftReview (Draft Review)
- Domain, ParamSet (Configuration)

---

## Dan 6: Value Objects & Domain Events

### Zadaci

#### 6.1 Value Objects
- DocumentMetadata
- LegalUnitReference
- AssertionContent
- CorpusMetadata
- RunParameters
- OntologyMetadata
- TermDefinition
- VectorRepresentation
- RuleDefinition
- ConflictScore
- ResolutionDecision

#### 6.2 Domain Events
- DocumentImported
- DocumentParsed
- AssertionsExtracted
- CorpusCreated
- CorpusRunCompleted
- EmbeddingsGenerated
- ConflictDetected
- FindingCreated
- ResolutionApplied

---

## Dan 7: Unit Tests

### Zadaci

#### 7.1 Test Infrastructure
- Test fixtures
- Test database
- Mock services

#### 7.2 Entity Tests
- Test all domain entities
- Test value objects
- Test domain events

#### 7.3 Coverage
- Aim for 80%+ coverage
- Focus on domain logic

---

## 📊 Success Criteria

### Must Have
- [x] Kompletna folder struktura
- [ ] Python projekat sa svim dependencies
- [ ] React projekat setup
- [ ] Centralizovana konfiguracija
- [ ] Logging sistem
- [ ] Database schema
- [ ] Svi domain entiteti
- [ ] Svi value objects
- [ ] Svi domain events
- [ ] Unit testovi (80%+ coverage)

### Nice to Have
- [ ] Docker setup
- [ ] CI/CD pipeline
- [ ] Pre-commit hooks
- [ ] Code formatting (black, ruff)

---

## 🎯 Deliverables Checklist

- [ ] `backend/` folder sa kompletnom strukturom
- [ ] `frontend/` folder sa kompletnom strukturom
- [ ] `pyproject.toml` sa svim dependencies
- [ ] `package.json` sa svim dependencies
- [ ] `backend/zaikon/core/config.py` - Settings
- [ ] `backend/zaikon/core/logging.py` - Logging
- [ ] `backend/zaikon/core/exceptions.py` - Custom exceptions
- [ ] `backend/zaikon/infrastructure/persistence/sqlite_connection.py` - DB connection
- [ ] `backend/zaikon/infrastructure/persistence/models.py` - SQLAlchemy models
- [ ] Svi domain entiteti (12 klasa)
- [ ] Svi value objects (15+ klasa)
- [ ] Svi domain events (10+ klasa)
- [ ] `backend/tests/` sa unit testovima
- [ ] `README.md` sa uputstvima

---

## 📝 Notes

### Važno
- Koristiti UTF-8 encoding svuda
- Centralizovana baza na `data/zaikon.db`
- Logging sa verbosity nivoima
- Validacija međurezultata
- Error handling

### Sledeća Nedelja
- Infrastructure Layer (Repositories, External Services)
- Domain Services
- Application Layer (Use Cases)

---

**Status**: Ready for Implementation  
**Estimated Time**: 7 dana  
**Priority**: High