# GROOVE.AI - AI-Assisted Legislative Compliance Review Platform

**Version**: 2.0.0  
**Architecture**: Modular Microservices  
**Status**: In Development

---

## 📋 Project Overview

GROOVE.AI is an AI-assisted platform for analyzing draft regulations against existing legal corpus to detect conflicts, inconsistencies, and compliance issues. The system uses a modular microservice architecture where each module performs a single function and can be called independently or orchestrated through workflows.

---

## 🏗️ Architecture

### Modular Microservice Design

- **20 Independent Modules** (Ports 8101-8120)
- **1 Central Orchestrator** (Port 8100)
- **Centralized Configuration** (`config.yaml`)
- **Shared Libraries** (`shared/config_loader.py`)

### Module Groups

1. **Document Processing** (5 modules)
   - File Reader, Text Normalizer, Latinizer, Legal Parser, Legal Unit Extractor

2. **Assertion Processing** (4 modules)
   - Assertion Extractor, Entity Recognizer, Condition Extractor, Assertion Classifier

3. **Embedding & Search** (4 modules)
   - Embedding Generator, Vector Store, Keyword Indexer, Hybrid Search

4. **Ontology & Knowledge** (3 modules)
   - Ontology Matcher, Reference Resolver, Definition Extractor

5. **Conflict Detection** (4 modules)
   - Candidate Finder, Conflict Detector, Severity Calculator, Recommendation Generator

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+ (for frontend)
- Ollama (for LLM, optional)

### Installation

```bash
# Clone repository
git clone https://github.com/higroni/grooveai.git
cd grooveai

# Install shared dependencies
pip install pyyaml

# Install module dependencies (example: file_reader)
cd modules/file_reader
pip install -r requirements.txt
```

### Configuration

All configuration is in [`config.yaml`](config.yaml). Key settings:

```yaml
# Sample file for development
development:
  sample_file: "D:/POSAO/OllamaProjects/GROOVE.AI/DOCUMENTS/DEV/radni_odnosi_0001_000001.pdf"

# Module ports
network:
  orchestrator:
    port: 8100
  modules:
    file_reader:
      port: 8101
    # ... (8102-8120)
```

### Running Modules

```bash
# Start a module (example: file_reader)
cd modules/file_reader
python main.py

# Module will start on configured port (8101)
```

---

## 📚 Documentation

### Architecture Documents

- [`ARCHITECTURE_V2.md`](ARCHITECTURE_V2.md) - Complete DDD architecture (1089 lines)
- [`MODULAR_ARCHITECTURE.md`](MODULAR_ARCHITECTURE.md) - Modular microservice design (1489 lines)
- [`WEEK_1_IMPLEMENTATION_PLAN.md`](WEEK_1_IMPLEMENTATION_PLAN.md) - Week 1 implementation plan
- [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) - Implementation summary

### Configuration

- [`config.yaml`](config.yaml) - Master configuration file (523 lines)
- [`shared/config_loader.py`](shared/config_loader.py) - Configuration loader library (451 lines)
- [`CONFIG_USAGE_EXAMPLES.md`](CONFIG_USAGE_EXAMPLES.md) - Usage examples (509 lines)

### Original Documentation (GEN/)

- [`GEN/README.md`](GEN/README.md) - Overview of all documentation
- [`GEN/LESSONS_LEARNED.md`](GEN/LESSONS_LEARNED.md) - **Critical lessons** (50+ hours saved)
- [`GEN/DDD_ARCHITECTURE.md`](GEN/DDD_ARCHITECTURE.md) - DDD specification
- [`GEN/DOMAIN_MODEL_V3.md`](GEN/DOMAIN_MODEL_V3.md) - Production-ready domain model
- [`GEN/MODULAR_ARCHITECTURE.md`](GEN/MODULAR_ARCHITECTURE.md) - Complete API specs

---

## 🔧 Technology Stack

### Backend
- **Python 3.12+**
- **FastAPI** - REST API framework
- **SQLAlchemy** - ORM
- **SQLite** - Database (per-module)
- **Qdrant** - Vector store
- **PyMuPDF** - PDF processing
- **python-docx** - DOCX processing

### AI Models
- **BAAI/bge-m3** - Embeddings (1024 dim)
- **BAAI/bge-reranker-v2-m3** - Reranking
- **Stanza** - NER (Serbian)
- **Ollama** - LLM (optional)

### Frontend (Planned)
- **React 18**
- **TypeScript**
- **Vite**
- **Tailwind CSS**

---

## 📦 Project Structure

```
GROOVE.AI/
├── config.yaml                    # Master configuration
├── shared/
│   └── config_loader.py          # Shared config library
├── modules/
│   ├── file_reader/              # Port 8101
│   ├── text_normalizer/          # Port 8102
│   ├── latinizer/                # Port 8103
│   └── ... (17 more modules)
├── orchestrator/                  # Port 8100
├── data/
│   ├── databases/                # Per-module SQLite
│   ├── logs/                     # Per-module logs
│   └── qdrant_storage/           # Vector store
├── DOCUMENTS/
│   └── DEV/                      # Test documents
└── GEN/                          # Original documentation
```

---

## 🎯 Development Status

### ✅ Completed
- Architecture design (DDD + Modular)
- Configuration system (centralized)
- Documentation (5000+ lines)
- Module specifications (20 modules)
- Orchestrator design (3 workflows)

### 🚧 In Progress
- Module 1: File Reader (starting)

### 📋 Planned
- Modules 2-20
- Orchestrator implementation
- Frontend
- Testing & deployment

---

## 🔑 Key Features

### Modular Design
- Each module is **independent**
- **Single responsibility** per module
- **Own database** and logs
- Can be called **standalone** or via orchestrator

### Centralized Configuration
- All settings in `config.yaml`
- Shared `config_loader.py` library
- Type-safe getters
- Easy to modify

### Production-Ready
- Versioning (OntologySet, ConflictRuleSet)
- Parameterization (ParamSet)
- Export/Import capabilities
- A/B testing support

---

## 📊 Performance Targets

- **Import**: < 10 min for 100 documents
- **Search**: < 200ms (hybrid + reranking)
- **Conflict Detection**: < 30s for draft with 100 assertions
- **Memory**: ~7GB (fits RTX 5070 Ti 16GB)

---

## 🤝 Contributing

This is a private development project. For questions or issues, refer to the documentation in `GEN/` folder.

---

## 📝 License

Private project - All rights reserved

---

## 🎓 Learning from Previous Iteration

This V2 architecture incorporates critical lessons learned:

### Top 5 Mistakes to Avoid
1. **StoreAssertionsStep in wrong chain** (4h lost) - Must be in per-file chain
2. **JSON instead of SQLite** (6h lost) - Use SQLite for structured data
3. **No Cyrillic support** (2h lost) - UTF-8 everywhere + regex for both scripts
4. **Large batch sizes** (2h lost) - Use 32-64 for embeddings, not 1000
5. **No debug output** (10h lost) - Comprehensive logging with phases

### Top 5 Optimizations
1. **Hybrid Search** (45% vector + 35% keyword + 20% graph) - ~140ms
2. **Batch Processing** - 10x faster
3. **Parallel Execution** - 2x faster
4. **Caching** - 45x faster for repeated queries
5. **Database Indexing** - 100x faster queries

See [`GEN/LESSONS_LEARNED.md`](GEN/LESSONS_LEARNED.md) for complete details.

---

## 📞 Contact

For development questions, consult the documentation or check the lessons learned.

---

**Status**: Architecture Complete - Ready for Implementation  
**Last Updated**: 2026-06-06  
**Version**: 2.0.0