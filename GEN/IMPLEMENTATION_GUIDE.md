# ZAIKON - Implementation Guide

## Prerequisites

### Required Software
- **Python 3.12+**
- **Node.js 18+** and npm
- **Ollama** (for local LLM)
- **Git**

### Optional
- **Docker** (for containerized deployment)
- **PostgreSQL** (alternative to SQLite for production)

---

## Step-by-Step Implementation

### Phase 1: Project Setup (Day 1)

#### 1.1 Create Project Structure
```bash
mkdir ZAIKON
cd ZAIKON

# Backend structure
mkdir -p backend/zaikon/{api/routers,core,modules,pipeline/steps}
mkdir -p backend/zaikon/modules/{corpus,draft_reviews,conflicts,assertions,legal_parser,ontology}
mkdir -p backend/zaikon/pipeline/steps/{corpus,draft}

# Frontend structure
mkdir -p frontend/src/{components,utils}

# Data directories
mkdir -p data/qdrant_storage
mkdir -p DOCUMENTS

# Scripts
mkdir scripts
```

#### 1.2 Initialize Python Project
```bash
cd backend

# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[project]
name = "zaikon"
version = "1.0.0"
description = "AI-assisted legislative compliance review platform"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-multipart>=0.0.6",
    "qdrant-client>=1.7.0",
    "ollama>=0.1.0",
    "pypdf2>=3.0.0",
    "python-docx>=1.1.0",
    "pdfplumber>=0.10.0",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"
EOF

# Install dependencies
pip install -e .
```

#### 1.3 Initialize Frontend Project
```bash
cd ../frontend

npm init -y
npm install react react-dom
npm install -D vite @vitejs/plugin-react typescript @types/react @types/react-dom

# Create vite.config.ts
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8100',
        changeOrigin: true
      }
    }
  }
})
EOF
```

---

### Phase 2: Core Infrastructure (Days 2-3)

#### 2.1 Configuration Management
Create `backend/zaikon/core/config.py`:

```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Database
    database_path: str = "data/zaikon.db"
    
    # Qdrant
    qdrant_path: str = "data/qdrant_storage"
    qdrant_collection: str = "corpus_legal_units"
    
    # LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:latest"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8100
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### 2.2 Database Schema
Create `backend/zaikon/core/database.py`:

```python
import sqlite3
from pathlib import Path
from zaikon.core.config import settings

def init_database():
    """Initialize database with schema."""
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Corpora table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corpora (
            corpus_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            metadata TEXT
        )
    """)
    
    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corpus_documents (
            document_id TEXT PRIMARY KEY,
            corpus_id TEXT NOT NULL,
            source_uri TEXT NOT NULL,
            filename TEXT NOT NULL,
            title TEXT,
            document_type TEXT,
            canonical_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (corpus_id) REFERENCES corpora(corpus_id)
        )
    """)
    
    # Assertions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corpus_assertions (
            assertion_id TEXT PRIMARY KEY,
            corpus_id TEXT NOT NULL,
            document_id TEXT NOT NULL,
            assertion_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (corpus_id) REFERENCES corpora(corpus_id),
            FOREIGN KEY (document_id) REFERENCES corpus_documents(document_id)
        )
    """)
    
    # Draft reviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS draft_reviews (
            pipeline_run_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content_text TEXT NOT NULL,
            selected_corpus_id TEXT,
            status TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (selected_corpus_id) REFERENCES corpora(corpus_id)
        )
    """)
    
    # Draft artifacts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS draft_artifacts (
            pipeline_run_id TEXT NOT NULL,
            artifact_name TEXT NOT NULL,
            artifact_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (pipeline_run_id, artifact_name),
            FOREIGN KEY (pipeline_run_id) REFERENCES draft_reviews(pipeline_run_id)
        )
    """)
    
    # Findings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            finding_id TEXT PRIMARY KEY,
            draft_id TEXT NOT NULL,
            conflict_type TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            draft_assertion_id TEXT,
            corpus_assertion_id TEXT,
            explanation TEXT,
            recommendation TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (draft_id) REFERENCES draft_reviews(pipeline_run_id)
        )
    """)
    
    # Import progress table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS import_file_progress (
            corpus_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            status TEXT NOT NULL,
            document_id TEXT,
            assertions_count INTEGER DEFAULT 0,
            error_message TEXT,
            started_at TEXT,
            completed_at TEXT,
            PRIMARY KEY (corpus_id, filename)
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assertions_corpus ON corpus_assertions(corpus_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assertions_document ON corpus_assertions(document_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_draft ON findings(draft_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity)")
    
    conn.commit()
    conn.close()
```

#### 2.3 Pipeline Base Classes
Create `backend/zaikon/pipeline/base.py`:

```python
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class PipelineArtifact:
    """Represents an artifact produced by a pipeline step."""
    name: str
    artifact_type: str
    payload: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PipelineContext:
    """Context passed through pipeline steps."""
    pipeline_run_id: str
    chain_name: str
    inputs: Dict[str, Any]
    artifacts: Dict[str, PipelineArtifact] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_artifact(self, artifact: PipelineArtifact):
        """Add artifact to context."""
        self.artifacts[artifact.name] = artifact
    
    def get_artifact(self, name: str) -> Optional[PipelineArtifact]:
        """Get artifact by name."""
        return self.artifacts.get(name)
    
    def log(self, level: str, message: str, step_name: str):
        """Add log entry."""
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "step_name": step_name
        })

class PipelineStep:
    """Base class for pipeline steps."""
    
    step_name: str = "base_step"
    requires: Tuple[str, ...] = ()
    produces: Tuple[str, ...] = ()
    
    def validate_requirements(self, context: PipelineContext):
        """Validate required artifacts exist."""
        missing = []
        for req in self.requires:
            if req not in context.artifacts:
                missing.append(req)
        
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"Step '{self.step_name}' missing artifacts: {joined}")
    
    def run(self, context: PipelineContext) -> PipelineContext:
        """Execute step logic. Override in subclasses."""
        raise NotImplementedError
    
    @classmethod
    def artifact(cls, name: str, artifact_type: str, payload: Any) -> PipelineArtifact:
        """Create artifact."""
        return PipelineArtifact(
            name=name,
            artifact_type=artifact_type,
            payload=payload
        )

class PipelineChain:
    """Chain of pipeline steps."""
    
    def __init__(self, chain_name: str, steps: List[PipelineStep]):
        self.chain_name = chain_name
        self.steps = steps
    
    def run(self, context: PipelineContext) -> PipelineContext:
        """Execute all steps in sequence."""
        for step in self.steps:
            # Validate requirements
            step.validate_requirements(context)
            
            # Execute step
            context = step.run(context)
            
            context.log("INFO", f"Step completed", step.step_name)
        
        return context
```

---

### Phase 3: Legal Document Parser (Days 4-5)

#### 3.1 Parser Service
Create `backend/zaikon/modules/legal_parser/service.py`:

```python
import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ParsedSection:
    """Represents a parsed legal section."""
    section_id: str
    section_type: str
    ordinal: int
    title: str
    content: str
    subsections: List['ParsedSection']

class LegalParserService:
    """Service for parsing legal documents."""
    
    # Article patterns (Latin and Cyrillic)
    ARTICLE_PATTERNS = [
        r'^Član\s+(\d+)',
        r'^Члан\s+(\d+)',
        r'^Article\s+(\d+)',
    ]
    
    # Paragraph patterns
    PARAGRAPH_PATTERNS = [
        r'^\((\d+)\)',
        r'^(\d+)\)',
    ]
    
    def parse_document(self, text: str) -> Dict[str, Any]:
        """Parse legal document text into structured format."""
        lines = text.split('\n')
        sections = []
        current_article = None
        current_paragraphs = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for article
            article_match = self._match_article(line)
            if article_match:
                # Save previous article
                if current_article:
                    current_article['subsections'] = current_paragraphs
                    sections.append(current_article)
                
                # Start new article
                current_article = {
                    'section_type': 'clan',
                    'ordinal': int(article_match),
                    'title': line,
                    'content': '',
                    'subsections': []
                }
                current_paragraphs = []
                continue
            
            # Check for paragraph
            para_match = self._match_paragraph(line)
            if para_match and current_article:
                para = {
                    'section_type': 'stav',
                    'ordinal': int(para_match),
                    'title': f'Stav {para_match}',
                    'content': line,
                    'subsections': []
                }
                current_paragraphs.append(para)
                continue
            
            # Add to current article content
            if current_article:
                if current_article['content']:
                    current_article['content'] += ' '
                current_article['content'] += line
        
        # Save last article
        if current_article:
            current_article['subsections'] = current_paragraphs
            sections.append(current_article)
        
        return {
            'sections': sections,
            'total_articles': len(sections)
        }
    
    def _match_article(self, line: str) -> Optional[str]:
        """Match article pattern."""
        for pattern in self.ARTICLE_PATTERNS:
            match = re.match(pattern, line)
            if match:
                return match.group(1)
        return None
    
    def _match_paragraph(self, line: str) -> Optional[str]:
        """Match paragraph pattern."""
        for pattern in self.PARAGRAPH_PATTERNS:
            match = re.match(pattern, line)
            if match:
                return match.group(1)
        return None
```

---

### Phase 4: Assertion Extraction (Days 6-7)

#### 4.1 Assertion Service
Create `backend/zaikon/modules/assertions/service.py`:

```python
from typing import List, Dict, Any
from pydantic import BaseModel
import uuid

class NormativeAssertion(BaseModel):
    """Represents a normative assertion."""
    assertion_id: str
    document_id: str
    section_id: str
    text: str
    action: str
    object: str
    domain: str
    modality: str
    conditions: List[str] = []
    exceptions: List[str] = []

class AssertionExtractionService:
    """Service for extracting normative assertions."""
    
    def extract_from_document(
        self,
        document: Dict[str, Any],
        corpus_id: str,
        document_id: str
    ) -> List[NormativeAssertion]:
        """Extract assertions from canonical document."""
        assertions = []
        
        for section in document.get('sections', []):
            section_assertions = self._extract_from_section(
                section,
                document_id,
                corpus_id
            )
            assertions.extend(section_assertions)
        
        return assertions
    
    def _extract_from_section(
        self,
        section: Dict[str, Any],
        document_id: str,
        corpus_id: str
    ) -> List[NormativeAssertion]:
        """Extract assertions from a section."""
        assertions = []
        content = section.get('content', '')
        
        # Simple extraction logic (enhance with LLM)
        if self._is_obligation(content):
            assertion = NormativeAssertion(
                assertion_id=str(uuid.uuid4()),
                document_id=document_id,
                section_id=section.get('section_id', ''),
                text=content,
                action='obaveza',
                object=self._extract_object(content),
                domain='general',
                modality='must'
            )
            assertions.append(assertion)
        
        return assertions
    
    def _is_obligation(self, text: str) -> bool:
        """Check if text contains obligation."""
        obligation_markers = [
            'dužan', 'obavezan', 'mora', 'treba',
            'дужан', 'обавезан', 'мора', 'треба'
        ]
        return any(marker in text.lower() for marker in obligation_markers)
    
    def _extract_object(self, text: str) -> str:
        """Extract object from text."""
        # Simple extraction (enhance with NLP)
        objects = ['poslodavac', 'zaposleni', 'radnik']
        for obj in objects:
            if obj in text.lower():
                return obj
        return 'unknown'
```

---

### Phase 5: Conflict Detection (Days 8-10)

#### 5.1 Conflict Detection Service
Create `backend/zaikon/modules/conflicts/service.py`:

```python
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class ConflictFinding:
    """Represents a detected conflict."""
    finding_id: str
    conflict_type: str
    category: str
    severity: str
    draft_assertion: Dict[str, Any]
    corpus_assertion: Dict[str, Any]
    explanation: str
    recommendation: str
    score: float

class ConflictDetectionService:
    """Service for detecting conflicts."""
    
    def detect_conflicts(
        self,
        draft_assertions: List[Dict[str, Any]],
        corpus_assertions: List[Dict[str, Any]]
    ) -> List[ConflictFinding]:
        """Detect conflicts between draft and corpus."""
        findings = []
        
        for draft_assertion in draft_assertions:
            # Find candidate corpus assertions
            candidates = self._find_candidates(
                draft_assertion,
                corpus_assertions
            )
            
            # Check for conflicts
            for corpus_assertion, score in candidates:
                conflict = self._check_conflict(
                    draft_assertion,
                    corpus_assertion,
                    score
                )
                if conflict:
                    findings.append(conflict)
        
        return findings
    
    def _find_candidates(
        self,
        draft_assertion: Dict[str, Any],
        corpus_assertions: List[Dict[str, Any]]
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Find candidate corpus assertions."""
        candidates = []
        
        for corpus_assertion in corpus_assertions:
            score = self._calculate_similarity(
                draft_assertion,
                corpus_assertion
            )
            
            # Minimum threshold
            if score < 0.25:
                continue
            
            # Require action or deadline match
            if not (self._matches_action(draft_assertion, corpus_assertion) or
                    self._matches_deadline(draft_assertion, corpus_assertion)):
                continue
            
            candidates.append((corpus_assertion, score))
        
        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
    
    def _calculate_similarity(
        self,
        draft: Dict[str, Any],
        corpus: Dict[str, Any]
    ) -> float:
        """Calculate similarity score."""
        score = 0.0
        
        # Action match
        if draft.get('action') == corpus.get('action'):
            score += 0.3
        
        # Object match
        if draft.get('object') == corpus.get('object'):
            score += 0.3
        
        # Domain match
        if draft.get('domain') == corpus.get('domain'):
            score += 0.2
        
        # Modality match
        if draft.get('modality') == corpus.get('modality'):
            score += 0.2
        
        return score
    
    def _check_conflict(
        self,
        draft: Dict[str, Any],
        corpus: Dict[str, Any],
        score: float
    ) -> Optional[ConflictFinding]:
        """Check for specific conflict type."""
        # Contradictory obligation
        if (draft.get('action') == 'obaveza' and
            corpus.get('action') == 'obaveza' and
            draft.get('object') == corpus.get('object') and
            draft.get('modality') != corpus.get('modality')):
            
            return ConflictFinding(
                finding_id=str(uuid.uuid4()),
                conflict_type='contradictory_obligation',
                category='normative_conflicts',
                severity='high',
                draft_assertion=draft,
                corpus_assertion=corpus,
                explanation='Draft obligation contradicts corpus obligation',
                recommendation='Align obligations or provide justification',
                score=score
            )
        
        return None
```

---

### Phase 6: FastAPI Application (Days 11-12)

#### 6.1 Main Application
Create `backend/zaikon/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from zaikon.core.database import init_database
from zaikon.api.routers import (
    corpus,
    draft_reviews,
    conflicts,
    health
)

# Initialize database
init_database()

# Create FastAPI app
app = FastAPI(
    title="ZAIKON API",
    description="AI-assisted legislative compliance review platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(corpus.router, prefix="/api/v1/corpora", tags=["corpus"])
app.include_router(draft_reviews.router, prefix="/api/v1/draft-reviews", tags=["drafts"])
app.include_router(conflicts.router, prefix="/api/v1/conflicts", tags=["conflicts"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])

@app.get("/")
def root():
    return {"message": "ZAIKON API", "version": "1.0.0"}
```

---

### Phase 7: Frontend (Days 13-15)

#### 7.1 Main App Component
Create `frontend/src/App.tsx`:

```typescript
import React, { useState } from 'react';
import CorpusManagement from './components/CorpusManagement';
import DraftReview from './components/DraftReview';
import ConflictFindings from './components/ConflictFindings';

function App() {
  const [activeTab, setActiveTab] = useState('corpus');
  const [selectedCorpusId, setSelectedCorpusId] = useState<string | null>(null);
  const [selectedDraftId, setSelectedDraftId] = useState<string | null>(null);

  return (
    <div className="app">
      <header>
        <h1>ZAIKON - Legislative Compliance Review</h1>
        <nav>
          <button onClick={() => setActiveTab('corpus')}>Corpus</button>
          <button onClick={() => setActiveTab('draft')}>Draft Review</button>
          <button onClick={() => setActiveTab('findings')}>Findings</button>
        </nav>
      </header>

      <main>
        {activeTab === 'corpus' && (
          <CorpusManagement onSelectCorpus={setSelectedCorpusId} />
        )}
        {activeTab === 'draft' && (
          <DraftReview 
            corpusId={selectedCorpusId}
            onDraftCreated={setSelectedDraftId}
          />
        )}
        {activeTab === 'findings' && (
          <ConflictFindings draftId={selectedDraftId} />
        )}
      </main>
    </div>
  );
}

export default App;
```

---

## Testing

### Unit Tests
```bash
cd backend
pytest tests/
```

### Integration Tests
```bash
cd backend
pytest tests/integration/
```

### End-to-End Tests
```bash
cd frontend
npm run test:e2e
```

---

## Deployment

### Development
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn zaikon.main:app --reload --port 8100

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Production
```bash
# Build frontend
cd frontend
npm run build

# Run backend with gunicorn
cd backend
gunicorn zaikon.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## Troubleshooting

### Common Issues

1. **Database locked**: Close all connections before migration
2. **Qdrant connection failed**: Check if Qdrant is running
3. **LLM timeout**: Increase timeout in settings
4. **Import fails**: Check file encoding (must be UTF-8)

---

This implementation guide provides step-by-step instructions for building the ZAIKON system from scratch.