# ZAIKON - Proces Uvoza i Obrade Podataka

## Pregled

Ovaj dokument objašnjava kako ZAIKON sistem uvozi, obrađuje i čuva pravne dokumente, od sirovih PDF/DOCX/TXT fajlova do strukturiranih podataka spremnih za detekciju konflikata.

---

## 1. Arhitektura Uvoza Podataka

### 1.1 Pipeline Pristup

ZAIKON koristi **modularni pipeline pristup** gde se svaki korak izvršava sekvencijalno:

```
Fajl → Ekstrakcija teksta → Normalizacija → Parsiranje → 
Ekstrakcija asercija → Indeksiranje → Skladištenje
```

Svaki korak:
- Prima **kontekst** sa rezultatima prethodnih koraka
- Proizvodi **artifakte** (rezultate) za sledeće korake
- Loguje napredak i greške
- Može da se izvršava nezavisno za testiranje

### 1.2 Tehnologije i Biblioteke

| Komponenta | Biblioteka | Verzija | Svrha |
|------------|-----------|---------|-------|
| **Backend Framework** | FastAPI | 0.115.0 | REST API server |
| **PDF Ekstrakcija** | PyMuPDF | 1.24.13 | Čitanje PDF dokumenata |
| **DOCX Ekstrakcija** | python-docx | 1.1.2 | Čitanje Word dokumenata |
| **Baza Podataka** | SQLite | 3.x | Centralno skladište |
| **ORM** | SQLAlchemy | 2.0.36 | Rad sa bazom |
| **Vektorska Baza** | Qdrant | 1.12.1 | Embedding pretraga |
| **Embeddings** | sentence-transformers | 3.3.1 | Generisanje vektora |
| **Embedding Model** | BAAI/bge-m3 | - | Multilingual embeddings |
| **Reranker Model** | BAAI/bge-reranker-v2-m3 | - | Poboljšanje rezultata |
| **NLP za Srpski** | Stanza | 1.9.2 | NER i lingvistička analiza |
| **Deep Learning** | PyTorch | 2.5.1 | Neural network backend |

---

## 2. Detaljni Proces Uvoza (Korak po Korak)

### Korak 1: Detekcija Fajlova

**Šta se dešava:**
- Sistem skenira folder koji korisnik izabere
- Identifikuje sve fajlove sa podržanim ekstenzijama (.pdf, .docx, .txt)
- Proverava duplikate pomoću SHA-256 hash-a sadržaja
- Proverava veličinu fajla (max 100MB po fajlu)

**Tehnologija:**
- Python `pathlib` za navigaciju fajl sistema
- `hashlib.sha256()` za detekciju duplikata

**Rezultat:**
```json
{
  "source_files": [
    {
      "source_uri": "file:///D:/docs/zakon.pdf",
      "filename": "zakon.pdf",
      "file_type": "pdf",
      "import_status": "pending",
      "content_hash": "abc123..."
    }
  ],
  "summary": {
    "total_files": 10,
    "supported_files": 8,
    "duplicate_files": 2
  }
}
```

### Korak 2: Ekstrakcija Teksta

**Šta se dešava:**
- Za svaki fajl, sistem ekstraktuje čist tekst
- PDF: PyMuPDF čita stranice i ekstraktuje tekst
- DOCX: python-docx čita paragrafe
- TXT: direktno čitanje

**Tehnologija:**
```python
# Za PDF
import fitz  # PyMuPDF
doc = fitz.open(filepath)
text = "\n".join(page.get_text() for page in doc)

# Za DOCX
from docx import Document
doc = Document(filepath)
text = "\n".join(p.text for p in doc.paragraphs)
```

**Rezultat:**
```json
{
  "document_id": "uuid-123",
  "source_uri": "file:///D:/docs/zakon.pdf",
  "content_text": "ZAKON O ŠUMAMA\nČlan 1\nOvim zakonom...",
  "metadata": {
    "page_count": 45,
    "char_count": 125000
  }
}
```

### Korak 3: Normalizacija Teksta

**Šta se dešava:**
- Konvertuje ćirilicu u latinicu (ako je omogućeno)
- Omogućava konzistentnu obradu teksta
- Čuva informaciju o primenjenoj normalizaciji

**Tehnologija:**
```python
# Mapiranje ćirilice u latinicu
_CYRILLIC_TO_LATIN = {
    "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D",
    "Ђ": "Đ", "Е": "E", "Ж": "Ž", "З": "Z", "И": "I",
    # ... kompletna mapa
}

def serbian_cyrillic_to_latin(text: str) -> str:
    return text.translate(str.maketrans(_CYRILLIC_TO_LATIN))
```

**Rezultat:**
- Tekst u latinici spreman za parsiranje
- Metadata o primenjenoj transformaciji

### Korak 4: Parsiranje Pravne Strukture

**Šta se dešava:**
- Identifikuje pravne jedinice: članove, stavove, tačke, alinee
- Koristi regex pattern matching za srpski pravni format
- Gradi hijerarhijsku strukturu dokumenta

**Tehnologija:**
```python
# Regex za detekciju članova
_ARTICLE_RE = re.compile(
    r"^\s*Član\s+(\d+)\.?\s*$",
    re.MULTILINE | re.IGNORECASE
)

# Regex za stavove
_PARAGRAPH_RE = re.compile(
    r"^\s*\((\d+)\)\s+",
    re.MULTILINE
)
```

**Rezultat:**
```json
{
  "canonical_json": {
    "legal_units": [
      {
        "unit_id": "clan_1",
        "unit_type": "article",
        "unit_number": "1",
        "content_text": "Ovim zakonom uređuje se...",
        "hierarchy": ["clan_1"],
        "children": [
          {
            "unit_id": "clan_1_stav_1",
            "unit_type": "paragraph",
            "unit_number": "1",
            "content_text": "Šume su dobro od opšteg interesa."
          }
        ]
      }
    ]
  }
}
```

### Korak 5: Ekstrakcija Normativnih Asercija

**Šta se dešava:**
- Iz svake pravne jedinice ekstraktuje **normativne asercije**
- Asercija = strukturirana izjava o pravilu, obavezi, zabrani, roku, itd.
- Koristi **rule-based pristup** sa regex pattern matching
- Koristi **ontologiju** za prepoznavanje pravnih koncepata

**Tehnologija:**

#### 5.1 Pattern Matching za Tipove Asercija

```python
# Detekcija zabrana
_PROHIBITION_RE = re.compile(r"\b(?:ne\s+sme|zabranjuje\s+se|zabranjeno)\b")

# Detekcija obaveza
_OBLIGATION_RE = re.compile(r"\b(?:mora|dužan|dužna|obavezan)\b")

# Detekcija dozvola
_PERMISSION_RE = re.compile(r"\b(?:može|mogu|ima\s+pravo)\b")

# Detekcija rokova
_DEADLINE_RE = re.compile(
    r"\b(?:u\s+roku\s+od|najkasnije)\s+"
    r"(?P<value>\d+|jedan|dva|tri)\s+(?P<working>radnih\s+)?dan(?:a)?\b"
)
```

#### 5.2 Ontologija za Pravne Koncepte

**Šta je ontologija:**
- Strukturirana baza znanja o pravnim konceptima
- Mapira termine na standardizovane koncepte
- Podržava sinonime i varijacije

**Skladištenje:**
- **SQLite baza**: `data/zaikon.db`, tabela `ontology_terms`
- **Format**: JSON sa slot-based strukturom

**Primer ontologije:**
```json
{
  "concept_id": "legal_entity",
  "canonical_term": "pravno lice",
  "variants": [
    "pravno lice",
    "pravna lica",
    "privredni subjekt",
    "privredno društvo"
  ],
  "category": "actor",
  "metadata": {
    "language": "sr",
    "domain": "general_law"
  }
}
```

**Kako se koristi:**
```python
# Pretraga ontologije
ontology_service = get_ontology_service()
matches = ontology_service.match_text(
    text="Pravno lice mora da podnese prijavu",
    top_k=5
)

# Rezultat
[
  OntologyMatch(
    concept_id="legal_entity",
    canonical_term="pravno lice",
    matched_text="Pravno lice",
    confidence=0.95
  )
]
```

#### 5.3 Auto-Tuning Ontologije

**Šta je auto-tuning:**
- Sistem automatski uči nove termine iz korpusa
- Kada detektuje nepoznat termin, predlaže dodavanje u ontologiju
- Korisnik može odobriti ili odbiti predlog

**Proces:**
1. Sistem parsira dokument i nalazi termine
2. Proverava da li termin postoji u ontologiji
3. Ako ne postoji, kreira predlog sa kontekstom
4. Čuva predlog u `ontology_suggestions` tabeli
5. Admin može pregledati i odobriti predloge

**Skladištenje predloga:**
```sql
CREATE TABLE ontology_suggestions (
    id TEXT PRIMARY KEY,
    suggested_term TEXT NOT NULL,
    context TEXT,
    frequency INTEGER DEFAULT 1,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP
);
```

#### 5.4 NER (Named Entity Recognition) sa Stanza

**Šta je NER:**
- Automatska identifikacija imenovanih entiteta u tekstu
- Prepoznaje: osobe, organizacije, lokacije, datume, iznose

**Tehnologija:**
```python
import stanza

# Inicijalizacija Stanza modela za srpski
nlp = stanza.Pipeline(
    lang='sr',
    processors='tokenize,ner',
    use_gpu=True  # ako je dostupan CUDA
)

# Obrada teksta
doc = nlp("Ministarstvo šumarstva donosi pravilnik.")

# Rezultat
for entity in doc.entities:
    print(f"{entity.text} -> {entity.type}")
    # "Ministarstvo šumarstva" -> ORG
```

**Integracija sa ontologijom:**
- NER detektuje entitete
- Ontologija ih mapira na pravne koncepte
- Kombinacija daje preciznije rezultate

**Rezultat ekstrakcije asercija:**
```json
{
  "assertion_id": "uuid-456",
  "assertion_type": "obligation",
  "source_unit_id": "clan_5_stav_1",
  "content_text": "Pravno lice mora da podnese prijavu u roku od 30 dana",
  "slots": {
    "actor": {
      "text": "Pravno lice",
      "concept_id": "legal_entity",
      "confidence": 0.95
    },
    "action": {
      "text": "podnese prijavu",
      "concept_id": "submit_application",
      "confidence": 0.88
    },
    "deadline": {
      "value": 30,
      "unit": "days",
      "working_days": false
    }
  }
}
```

### Korak 6: Generisanje Embeddings

**Šta su embeddings:**
- Numerička reprezentacija teksta u vektorskom prostoru
- Omogućava semantičku pretragu (pronalaženje sličnih značenja)
- Svaki tekst se pretvara u vektor brojeva (npr. 1024 dimenzije)

**Tehnologija:**

#### 6.1 Sentence Transformers

```python
from sentence_transformers import SentenceTransformer

# Učitavanje modela
model = SentenceTransformer('BAAI/bge-m3')

# Generisanje embedding-a
text = "Pravno lice mora da podnese prijavu"
embedding = model.encode(text)
# Rezultat: numpy array sa 1024 float vrednosti
```

**Model: BAAI/bge-m3**
- **BGE** = Beijing Academy of Artificial Intelligence, General Embedding
- **M3** = Multi-lingual, Multi-functionality, Multi-granularity
- Podržava 100+ jezika uključujući srpski
- 1024 dimenzije
- Optimizovan za semantičku pretragu

#### 6.2 Fallback: Deterministički Embeddings

**Kada se koristi:**
- Ako GPU nije dostupan
- Za brzo testiranje bez ML modela
- Kao backup opcija

**Kako radi:**
```python
def deterministic_embedding(text: str, dimensions: int = 64) -> list[float]:
    # Tokenizacija
    tokens = extract_tokens(text)
    
    # Kreiranje vektora
    vector = [0.0] * dimensions
    
    # Popunjavanje vektora bazom na hash-u tokena
    for token in tokens:
        hash_value = hash(token)
        index = hash_value % dimensions
        vector[index] += 1.0
    
    # Normalizacija
    magnitude = sqrt(sum(v * v for v in vector))
    return [v / magnitude for v in vector]
```

**Karakteristike:**
- Brz (bez ML modela)
- Deterministički (isti tekst = isti vektor)
- Manje precizan od ML modela
- 64 dimenzije (umesto 1024)

#### 6.3 Skladištenje Embeddings

**Qdrant Vektorska Baza:**

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Inicijalizacija (embedded mode)
client = QdrantClient(path="./data/qdrant_storage")

# Kreiranje kolekcije
client.create_collection(
    collection_name="corpus_legal_units",
    vectors_config=VectorParams(
        size=1024,  # dimenzije
        distance=Distance.COSINE  # metrika sličnosti
    )
)

# Dodavanje vektora
client.upsert(
    collection_name="corpus_legal_units",
    points=[
        {
            "id": "uuid-789",
            "vector": embedding.tolist(),
            "payload": {
                "unit_id": "clan_5_stav_1",
                "content_text": "Pravno lice mora...",
                "document_id": "uuid-123"
            }
        }
    ]
)
```

**Zašto Qdrant:**
- Optimizovan za brzu pretragu vektora
- Podržava embedded mode (bez eksternog servera)
- Skalabilan (milioni vektora)
- Podržava filtriranje po metadata

**Skladištenje:**
- **Lokacija**: `data/qdrant_storage/`
- **Format**: Binarne datoteke + SQLite indeks
- **Kolekcije**: 
  - `corpus_legal_units` - pravne jedinice iz korpusa
  - `zaikon_smoke` - test kolekcija

### Korak 7: Indeksiranje

**Šta se indeksira:**

#### 7.1 Keyword Index (BM25)
- Tradicionalna pretraga po ključnim rečima
- Koristi TF-IDF (Term Frequency - Inverse Document Frequency)
- Brza pretraga po tačnim terminima

```python
# Ekstrakcija tokena
tokens = [
    token for token in re.findall(r"\w+", text.lower())
    if len(token) >= 3
]

# Računanje frekvencije
term_frequency = Counter(tokens)
```

#### 7.2 Vector Index
- Semantička pretraga pomoću embeddings
- Pronalazi slične koncepte čak i sa različitim rečima
- Koristi Qdrant

#### 7.3 Structure Index
- Indeks hijerarhijske strukture
- Omogućava pretragu po tipu jedinice (član, stav, tačka)
- Čuva se u SQLite

```sql
CREATE TABLE legal_units (
    unit_id TEXT PRIMARY KEY,
    document_id TEXT,
    unit_type TEXT,
    unit_number TEXT,
    content_text TEXT,
    hierarchy_path TEXT,
    parent_unit_id TEXT
);
```

#### 7.4 Reference Graph
- Graf međusobnih referenci između dokumenata
- "Član 5 ovog zakona primenjuje se..."
- "U skladu sa Zakonom o šumama..."

**Skladištenje:**
```sql
CREATE TABLE legal_references (
    reference_id TEXT PRIMARY KEY,
    source_unit_id TEXT,
    target_document TEXT,
    target_unit TEXT,
    reference_type TEXT,
    resolved BOOLEAN
);
```

### Korak 8: Skladištenje u Bazu

**Centralna SQLite Baza: `data/zaikon.db`**

#### 8.1 Struktura Baze

```sql
-- Korpusi (kolekcije dokumenata)
CREATE TABLE corpora (
    corpus_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP,
    document_count INTEGER DEFAULT 0
);

-- Dokumenti
CREATE TABLE documents (
    document_id TEXT PRIMARY KEY,
    corpus_id TEXT,
    source_uri TEXT,
    filename TEXT,
    document_type TEXT,
    content_text TEXT,
    canonical_json TEXT,  -- JSON sa parsiranom strukturom
    created_at TIMESTAMP,
    FOREIGN KEY (corpus_id) REFERENCES corpora(corpus_id)
);

-- Normativne asercije
CREATE TABLE corpus_assertions (
    assertion_id TEXT PRIMARY KEY,
    corpus_id TEXT,
    document_id TEXT,
    source_unit_id TEXT,
    assertion_type TEXT,
    content_text TEXT,
    slots_json TEXT,  -- JSON sa ekstraktovanim slot-ovima
    created_at TIMESTAMP,
    FOREIGN KEY (corpus_id) REFERENCES corpora(corpus_id)
);

-- Ontologija
CREATE TABLE ontology_terms (
    concept_id TEXT PRIMARY KEY,
    canonical_term TEXT,
    variants_json TEXT,  -- JSON lista varijanti
    category TEXT,
    metadata_json TEXT,
    created_at TIMESTAMP
);

-- Predlozi za ontologiju
CREATE TABLE ontology_suggestions (
    suggestion_id TEXT PRIMARY KEY,
    suggested_term TEXT,
    context TEXT,
    frequency INTEGER,
    status TEXT,  -- pending, approved, rejected
    created_at TIMESTAMP
);

-- Pravne jedinice (za strukturnu pretragu)
CREATE TABLE legal_units (
    unit_id TEXT PRIMARY KEY,
    document_id TEXT,
    unit_type TEXT,
    unit_number TEXT,
    content_text TEXT,
    hierarchy_path TEXT,
    parent_unit_id TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

-- Reference između dokumenata
CREATE TABLE legal_references (
    reference_id TEXT PRIMARY KEY,
    source_unit_id TEXT,
    target_document TEXT,
    target_unit TEXT,
    reference_type TEXT,
    resolved BOOLEAN,
    FOREIGN KEY (source_unit_id) REFERENCES legal_units(unit_id)
);
```

#### 8.2 Zašto SQLite?

**Prednosti:**
- **Jednostavnost**: Jedna datoteka, bez servera
- **Brzina**: Dovoljno brz za hiljade dokumenata
- **Pouzdanost**: ACID transakcije
- **Portabilnost**: Lako premeštanje i backup
- **Integracija**: Odlična podrška u Python-u

**Ograničenja:**
- Nije optimalan za milione dokumenata
- Jedan pisač u isto vreme
- Za produkciju sa velikim opterećenjem: PostgreSQL

### Korak 9: Generisanje Izveštaja

**Finalni izveštaj uvoza:**

```json
{
  "import_id": "uuid-import-123",
  "corpus_id": "uuid-corpus-456",
  "status": "completed",
  "summary": {
    "total_files": 10,
    "processed_files": 8,
    "failed_files": 2,
    "total_documents": 8,
    "total_legal_units": 450,
    "total_assertions": 1250
  },
  "indexes": {
    "keyword_index": {
      "unique_terms": 5000,
      "top_terms": ["šuma", "gazdovanje", "pravno lice"]
    },
    "vector_index": {
      "computed_vectors": 450,
      "embedding_model": "BAAI/bge-m3",
      "dimensions": 1024
    },
    "structure_index": {
      "document_types": {"zakon": 3, "pravilnik": 5},
      "unit_types": {"article": 120, "paragraph": 330}
    },
    "reference_graph": {
      "resolved_references": 85,
      "missing_references": 12
    }
  },
  "duration_seconds": 45.2,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## 3. Formati Podataka i Razlozi

### 3.1 Tekstualni Podaci

**Format**: UTF-8 string
**Lokacija**: SQLite `documents.content_text`, `legal_units.content_text`
**Razlog**: 
- Jednostavna pretraga
- Lako čitljivo
- Kompatibilno sa svim alatima

### 3.2 Strukturirani Podaci (JSON)

**Format**: JSON string
**Lokacija**: SQLite `documents.canonical_json`, `corpus_assertions.slots_json`
**Razlog**:
- Fleksibilna struktura
- Lako parsiranje u Python
- Čitljivo za ljude
- Podržava hijerarhiju

**Primer:**
```json
{
  "legal_units": [
    {
      "unit_id": "clan_1",
      "unit_type": "article",
      "children": [...]
    }
  ]
}
```

### 3.3 Vektorski Podaci (Embeddings)

**Format**: Binary float32 array
**Lokacija**: Qdrant `data/qdrant_storage/`
**Razlog**:
- Kompaktno skladištenje (4 bytes po dimenziji)
- Brza pretraga (optimizovani indeksi)
- Specijalizovana baza za vektore

**Veličina:**
- 1024 dimenzije × 4 bytes = 4KB po vektoru
- 1000 vektora = ~4MB
- 100,000 vektora = ~400MB

### 3.4 Metadata

**Format**: JSON
**Lokacija**: SQLite i Qdrant payload
**Razlog**:
- Fleksibilno dodavanje novih polja
- Lako filtriranje
- Čuvanje konteksta

---

## 4. Optimizacije i Performance

### 4.1 Batch Processing

**Embeddings:**
```python
# Umesto jedan po jedan
for text in texts:
    embedding = model.encode(text)  # Sporo

# Batch obrada
embeddings = model.encode(texts, batch_size=128)  # Brže
```

**Razlog**: GPU efikasnije procesira više tekstova odjednom

### 4.2 Caching

**Ontologija:**
```python
@lru_cache(maxsize=1000)
def match_concept(text: str) -> OntologyMatch:
    # Keširani rezultati za često korišćene termine
    ...
```

**Razlog**: Isti termini se često ponavljaju

### 4.3 Parallel Processing

**File-by-File Import:**
- Svaki fajl se procesira nezavisno
- Moguća paralelizacija u budućnosti
- Thread-safe skladištenje

### 4.4 Incremental Updates

**Dodavanje novih dokumenata:**
- Ne procesira ponovo postojeće dokumente
- Samo novi dokumenti se indeksiraju
- Qdrant podržava upsert operacije

---

## 5. Konfiguracija

**Fajl: `backend/zaikon/core/config.py`**

```python
class Settings(BaseSettings):
    # Baza podataka
    database_url: str = "sqlite:///data/zaikon.db"
    
    # Embeddings
    embedding_model: str = "BAAI/bge-m3"
    embedding_dimensions: int = 1024
    embedding_batch_size: int = 128
    embedding_device: str = "cuda"  # ili "cpu"
    
    # Qdrant
    qdrant_path: Path = Path("./data/qdrant_storage")
    
    # NER
    ner_enabled: bool = True
    ner_fallback_to_ontology: bool = True
    
    # Parsiranje
    parser_min_confidence: float = 0.70
    enable_cyrillic_latin_normalization: bool = True
    
    # Import
    import_max_file_mb: int = 100
    import_skip_duplicates: bool = True
```

---

## 6. Dijagram Toka Podataka

```
┌─────────────────┐
│  PDF/DOCX/TXT   │
│     Fajlovi     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PyMuPDF/docx   │ ◄── Ekstrakcija teksta
│  Text Extract   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Normalizacija  │ ◄── Ćirilica → Latinica
│  (Cyrillic→Lat) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Legal Parser    │ ◄── Regex pattern matching
│ (Član, Stav...) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Ontologija    │ ◄── SQLite + Auto-tuning
│  + NER (Stanza) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Ekstrakcija   │ ◄── Rule-based + Ontology
│    Asercija     │
└────────┬────────┘
         │
         ├─────────────────┬─────────────────┐
         ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   SQLite     │  │   Qdrant     │  │  Embeddings  │
│  (Struktura) │  │  (Vektori)   │  │ (BGE-M3)     │
└──────────────┘  └──────────────┘  └──────────────┘
         │                 │                 │
         └─────────────────┴─────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Spremno za     │
                  │  Detekciju      │
                  │  Konflikata     │
                  └─────────────────┘
```

---

## 7. Primer Kompletnog Toka

**Input:** `zakon_o_sumama.pdf` (45 strana)

**Korak 1:** Detekcija
- Fajl pronađen: ✓
- Tip: PDF
- Veličina: 2.5 MB
- Hash: `abc123...`

**Korak 2:** Ekstrakcija
- PyMuPDF čita 45 strana
- Ekstraktovano: 125,000 karaktera
- Vreme: 2.3 sekunde

**Korak 3:** Normalizacija
- Detektovana ćirilica: 35% teksta
- Konvertovano u latinicu
- Vreme: 0.1 sekunda

**Korak 4:** Parsiranje
- Pronađeno: 120 članova
- Pronađeno: 330 stavova
- Pronađeno: 85 tačaka
- Vreme: 1.5 sekundi

**Korak 5:** Ekstrakcija asercija
- Ontologija: 450 match-eva
- NER: 120 entiteta
- Ekstraktovano: 1,250 asercija
  - Obaveze: 450
  - Zabrane: 180
  - Dozvole: 320
  - Rokovi: 95
  - Ostalo: 205
- Vreme: 3.2 sekunde

**Korak 6:** Embeddings
- Model: BAAI/bge-m3
- Generisano: 450 vektora (1024 dim)
- Batch size: 128
- Device: CUDA
- Vreme: 5.8 sekundi

**Korak 7:** Indeksiranje
- Keyword: 5,000 unique terms
- Vector: 450 vektora u Qdrant
- Structure: 535 legal units
- References: 85 resolved
- Vreme: 2.1 sekunda

**Korak 8:** Skladištenje
- SQLite: 1 document, 535 units, 1,250 assertions
- Qdrant: 450 vectors
- Veličina: ~2.5 MB (SQLite) + ~1.8 MB (Qdrant)
- Vreme: 0.8 sekundi

**Ukupno vreme:** ~15.8 sekundi
**Rezultat:** Dokument spreman za detekciju konflikata

---

## 8. Troubleshooting

### Problem: Sporo generisanje embeddings

**Rešenje:**
```python
# Proveri da li koristi GPU
settings.embedding_device = "cuda"

# Povećaj batch size
settings.embedding_batch_size = 256

# Koristi FP16 precision
settings.embedding_precision = "fp16"
```

### Problem: Ontologija ne prepoznaje termine

**Rešenje:**
1. Proveri da li termin postoji u bazi
2. Dodaj varijante termina
3. Omogući auto-tuning
4. Koristi NER kao fallback

### Problem: Parser ne prepoznaje strukturu

**Rešenje:**
1. Proveri format dokumenta (ćirilica/latinica)
2. Omogući normalizaciju
3. Smanji `parser_min_confidence`
4. Proveri regex pattern-e

---

## 9. Zaključak

ZAIKON sistem koristi moderan stack tehnologija za efikasnu obradu pravnih dokumenata:

- **PyMuPDF/python-docx** za ekstrakciju teksta
- **Regex + Ontologija** za parsiranje i ekstrakciju
- **Stanza** za NER i lingvističku analizu
- **BAAI/bge-m3** za semantičke embeddings
- **Qdrant** za vektorsku pretragu
- **SQLite** za strukturirano skladištenje

Proces je optimizovan za:
- **Brzinu**: Batch processing, GPU acceleration
- **Preciznost**: Ontologija + NER + Auto-tuning
- **Skalabilnost**: Modularni pipeline, incremental updates
- **Održivost**: Čist kod, jasna arhitektura

Rezultat je sistem koji može da procesira hiljade pravnih dokumenata i pripremi ih za automatsku detekciju konflikata.