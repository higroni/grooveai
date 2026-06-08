# Plan za Implementaciju Sistema za Detekciju Konflikata u Zakonima

## 1. QDRANT BATCH LOADER - Punjenje Vektorske Baze

### 1.1 Arhitektura Kolekcija u Qdrant

**PREPORUKA: Multi-Collection Approach**

#### Kolekcija 1: `legal_units` (Glavna kolekcija)
- **Šta sadrži**: Sve pravne jedinice (članci, stavovi, tačke)
- **Vector**: Embedding celokupnog teksta pravne jedinice
- **Payload**:
  ```json
  {
    "unit_id": "uuid",
    "document_id": "zakon_o_radu.pdf",
    "document_title": "Zakon o radu",
    "document_type": "law",
    "unit_type": "article|paragraph|item",
    "unit_number": "123",
    "unit_title": "Član 123",
    "full_text": "Tekst pravne jedinice...",
    "parent_unit_id": "uuid",
    "hierarchy_level": 2,
    "
": {
      "obligations": [...],
      "prohibitions": [...],
      "permissions": [...],
      "definitions": [...]
    },
    "entities": {
      "dates": [...],
      "amounts": [...],
      "organizations": [...]
    },
    "temporal_references": [...],
    "legal_hierarchy": {
      "document_level": "primary|secondary",
      "authority_level": "constitutional|legislative|regulatory"
    }
  }
  ```

#### Kolekcija 2: `normative_content` (Specijalizovana)
- **Šta sadrži**: Samo normativni sadržaj (obaveze, zabrane, dozvole)
- **Vector**: Embedding normativnog sadržaja
- **Payload**:
  ```json
  {
    "normative_id": "uuid",
    "source_unit_id": "uuid",
    "document_id": "zakon_o_radu.pdf",
    "normative_type": "obligation|prohibition|permission|definition",
    "text": "Poslodavac je dužan da...",
    "subject": "poslodavac",
    "action": "isplati zaradu",
    "conditions": [...],
    "temporal_scope": "ongoing|temporary|conditional"
  }
  ```

#### Kolekcija 3: `document_metadata` (Metapodaci)
- **Šta sadrži**: Informacije o dokumentima
- **Vector**: Embedding naslova i sažetka dokumenta
- **Payload**:
  ```json
  {
    "document_id": "zakon_o_radu.pdf",
    "title": "Zakon o radu",
    "document_type": "law|regulation|decree",
    "effective_date": "2005-03-15",
    "legal_hierarchy_level": "primary",
    "total_units": 311,
    "summary": "Zakon koji uređuje radne odnose..."
  }
  ```

### 1.2 Batch Loader Modul

**Fajl**: `modules/qdrant_loader/service.py`

**Funkcionalnost**:
1. Čita JSON fajlove iz batch output-a
2. Generiše embeddings za svaku pravnu jedinicu
3. Kreira payload sa svim relevantnim podacima
4. Bulk insert u Qdrant (batch od 100 dokumenata)
5. Loguje progress i greške

**Embedding Strategy**:
- Model: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (podržava srpski)
- Alternativa: `intfloat/multilingual-e5-large` (bolji za pravne tekstove)
- Dimenzije: 768

---

## 2. PROPOSAL PROCESSOR - Priprema Predloga Zakona

### 2.1 Input Formati
- PDF fajl
- Word dokument (.docx)
- Plain text (paste u UI)

### 2.2 Processing Pipeline
**Isti pipeline kao za postojeće zakone**:
1. File Reader (M1)
2. Latinizer (M2)
3. Text Normalizer (M3)
4. Legal Parser (M4)
5. Entity Recognizer (M6)
6. Assertion Extractor (M7)
7. Condition Extractor (M8)
8. Assertion Classifier (M9)
9. Semantic Extraction (M10)

### 2.3 Output Format
- Isti JSON format kao postojeći dokumenti
- Dodatno polje: `is_proposal: true`
- Dodatno polje: `proposal_metadata`:
  ```json
  {
    "submitted_date": "2026-06-08",
    "proposer": "Ministarstvo rada",
    "status": "draft|submitted|in_review"
  }
  ```

---

## 3. CONFLICT DETECTOR - Detekcija Konflikata

### 3.1 Tipovi Konflikata

#### 3.1.1 Direktni Konflikti
- **Kontradikcija**: Predlog kaže "A", postojeći zakon kaže "ne-A"
- **Primer**: 
  - Predlog: "Minimalna zarada je 50,000 RSD"
  - Postojeći: "Minimalna zarada je 40,000 RSD"

#### 3.1.2 Hijerarhijski Konflikti
- Predlog (podzakonski akt) je u suprotnosti sa zakonom (viši nivo)
- **Primer**:
  - Predlog (pravilnik): "Radna nedelja može biti 50 sati"
  - Zakon: "Radna nedelja ne može biti duža od 40 sati"

#### 3.1.3 Temporalni Konflikti
- Preklapanje vremenskih perioda sa različitim pravilima
- **Primer**:
  - Predlog: "Od 1.1.2027. minimalna zarada je 60,000"
  - Postojeći: "Od 1.1.2027. minimalna zarada je 55,000"

#### 3.1.4 Semantički Konflikti
- Različite definicije istog pojma
- **Primer**:
  - Predlog: "Zaposleni je lice u radnom odnosu"
  - Postojeći: "Zaposleni je lice u radnom odnosu ili angažovano ugovorom"

### 3.2 Conflict Detection Algorithm

```python
def detect_conflicts(proposal_json, qdrant_client):
    conflicts = []
    
    # Za svaku pravnu jedinicu u predlogu
    for unit in proposal_json['parsed_structure']['units']:
        
        # 1. SEMANTIC SEARCH u Qdrant
        similar_units = qdrant_client.search(
            collection_name="legal_units",
            query_vector=embed(unit['text']),
            limit=10,
            score_threshold=0.7
        )
        
        # 2. FILTER po tipu normativnog sadržaja
        for similar in similar_units:
            # Proveri da li su oba obligation/prohibition/permission
            if has_same_normative_type(unit, similar):
                
                # 3. EXTRACT ključne entitete
                proposal_entities = extract_key_entities(unit)
                existing_entities = extract_key_entities(similar)
                
                # 4. COMPARE vrednosti
                if entities_conflict(proposal_entities, existing_entities):
                    conflicts.append({
                        'type': 'direct_conflict',
                        'proposal_unit': unit,
                        'existing_unit': similar,
                        'conflict_reason': 'Different values for same subject',
                        'severity': 'high'
                    })
                
                # 5. CHECK hijerarhija
                if is_hierarchical_conflict(proposal_json, similar):
                    conflicts.append({
                        'type': 'hierarchical_conflict',
                        'proposal_unit': unit,
                        'existing_unit': similar,
                        'conflict_reason': 'Lower-level document contradicts higher-level',
                        'severity': 'critical'
                    })
    
    return conflicts
```

### 3.3 Conflict Scoring
- **Critical** (100): Direktna kontradikcija sa zakonom višeg nivoa
- **High** (75): Direktna kontradikcija sa zakonom istog nivoa
- **Medium** (50): Semantička neusaglašenost
- **Low** (25): Potencijalni konflikt (treba ljudska provera)

---

## 4. RUDIMENTARNI UI - Testiranje

### 4.1 Tehnologije
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit (brzo za prototip) ili React (za production)
- **Za početak**: Streamlit (može se napraviti za 1 dan)

### 4.2 UI Flow

```
┌─────────────────────────────────────┐
│  GROOVE.AI - Conflict Detector      │
├─────────────────────────────────────┤
│                                     │
│  📄 Upload Proposal:                │
│  ┌─────────────────────────────┐   │
│  │ [Choose File] or [Paste Text]│  │
│  └─────────────────────────────┘   │
│                                     │
│  ⚙️  Processing Options:            │
│  ☑ Enable semantic analysis         │
│  ☑ Check hierarchical conflicts     │
│  ☑ Check temporal conflicts         │
│                                     │
│  [🔍 Analyze for Conflicts]         │
│                                     │
├─────────────────────────────────────┤
│  📊 Results:                        │
│                                     │
│  ⚠️  3 Critical Conflicts Found     │
│  ⚠️  5 High Priority Conflicts      │
│  ℹ️  12 Potential Issues            │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Conflict #1 (CRITICAL)      │   │
│  │ ─────────────────────────── │   │
│  │ Proposal (Article 15):      │   │
│  │ "Minimalna zarada 60,000"   │   │
│  │                             │   │
│  │ Conflicts with:             │   │
│  │ Zakon o radu (Article 111): │   │
│  │ "Minimalna zarada 40,000"   │   │
│  │                             │   │
│  │ Reason: Direct contradiction│   │
│  │ Severity: CRITICAL          │   │
│  │                             │   │
│  │ [View Details] [Ignore]     │   │
│  └─────────────────────────────┘   │
│                                     │
│  [📥 Export Report (PDF/JSON)]      │
└─────────────────────────────────────┘
```

### 4.3 Streamlit Implementacija

**Fajl**: `ui/conflict_detector_app.py`

```python
import streamlit as st
import requests
from pathlib import Path

st.title("🔍 GROOVE.AI - Legal Conflict Detector")

# File upload
uploaded_file = st.file_uploader(
    "Upload proposal (PDF/DOCX)", 
    type=['pdf', 'docx']
)

# Text paste
text_input = st.text_area(
    "Or paste proposal text here:", 
    height=200
)

# Options
col1, col2, col3 = st.columns(3)
with col1:
    semantic = st.checkbox("Semantic Analysis", value=True)
with col2:
    hierarchical = st.checkbox("Hierarchical Check", value=True)
with col3:
    temporal = st.checkbox("Temporal Check", value=True)

# Analyze button
if st.button("🔍 Analyze for Conflicts"):
    with st.spinner("Processing proposal..."):
        # Call backend API
        response = requests.post(
            "http://localhost:8000/api/detect-conflicts",
            files={'file': uploaded_file} if uploaded_file else None,
            data={'text': text_input if text_input else None}
        )
        
        conflicts = response.json()
        
        # Display results
        st.subheader("📊 Analysis Results")
        
        critical = [c for c in conflicts if c['severity'] == 'critical']
        high = [c for c in conflicts if c['severity'] == 'high']
        medium = [c for c in conflicts if c['severity'] == 'medium']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Critical", len(critical), delta=None)
        col2.metric("High", len(high), delta=None)
        col3.metric("Medium", len(medium), delta=None)
        
        # Display conflicts
        for i, conflict in enumerate(conflicts, 1):
            with st.expander(f"Conflict #{i} - {conflict['severity'].upper()}"):
                st.markdown(f"**Proposal Unit:**")
                st.code(conflict['proposal_unit']['text'])
                
                st.markdown(f"**Conflicts with:**")
                st.code(conflict['existing_unit']['text'])
                
                st.markdown(f"**Reason:** {conflict['conflict_reason']}")
                st.markdown(f"**Document:** {conflict['existing_unit']['document_title']}")
```

---

## 5. IMPLEMENTACIONI PLAN - Faze

### FAZA 1: Qdrant Setup & Batch Loader (2-3 dana)
1. ✅ Setup Qdrant (Docker ili cloud)
2. ✅ Kreiranje kolekcija
3. ✅ Implementacija batch loader modula
4. ✅ Testiranje na 10-20 dokumenata
5. ✅ Bulk load svih 230+ dokumenata

### FAZA 2: Proposal Processor (1 dan)
1. ✅ Reuse postojećeg pipeline-a
2. ✅ Dodavanje proposal-specific metadata
3. ✅ Testiranje na primeru predloga zakona

### FAZA 3: Conflict Detector - Basic (2-3 dana)
1. ✅ Implementacija semantic search
2. ✅ Detekcija direktnih konflikata
3. ✅ Scoring system
4. ✅ Testiranje na poznatim konfliktima

### FAZA 4: Rudimentarni UI (1-2 dana)
1. ✅ Streamlit aplikacija
2. ✅ File upload + text paste
3. ✅ Prikaz rezultata
4. ✅ Export u PDF/JSON

### FAZA 5: Advanced Conflict Detection (3-4 dana)
1. ✅ Hijerarhijski konflikti
2. ✅ Temporalni konflikti
3. ✅ Semantički konflikti
4. ✅ Fine-tuning scoring-a

### FAZA 6: UI Improvements (2-3 dana)
1. ✅ Vizualizacija konflikata
2. ✅ Filtering i sorting
3. ✅ Detaljni prikaz konteksta
4. ✅ Export opcije

---

## 6. TEHNIČKI STACK

### Backend
- **FastAPI**: REST API za conflict detection
- **Qdrant**: Vektorska baza
- **sentence-transformers**: Embeddings
- **SQLite**: Metadata i cache

### Frontend
- **Streamlit** (MVP): Brz prototip
- **React + TypeScript** (Production): Skalabilno rešenje

### Deployment
- **Docker**: Kontejnerizacija
- **Docker Compose**: Orchestration (FastAPI + Qdrant + UI)

---

## 7. TESTIRANJE

### Test Cases
1. **Direktan konflikt**: Različite vrednosti za istu obavezu
2. **Hijerarhijski konflikt**: Pravilnik vs Zakon
3. **Temporalni konflikt**: Preklapanje datuma
4. **Semantički konflikt**: Različite definicije
5. **False positive**: Slični tekstovi bez konflikta

### Test Data
- Koristiti postojeće zakone iz baze
- Kreirati veštačke predloge sa poznatim konfliktima
- Testirati na realnim predlozima zakona

---

## 8. METRIKE USPEHA

- **Precision**: % detektovanih konflikata koji su stvarni konflikti
- **Recall**: % stvarnih konflikata koji su detektovani
- **F1 Score**: Harmonijska sredina precision i recall
- **Target**: F1 > 0.85 za MVP

---

## 9. BUDUĆA PROŠIRENJA

1. **Sugestije za rešavanje konflikata**
2. **Automatsko generisanje amandmana**
3. **Vizualizacija pravne hijerarhije**
4. **Praćenje istorije izmena zakona**
5. **Multi-language support** (engleski, nemački)
6. **API za integraciju sa drugim sistemima**

---

## 10. RIZICI I MITIGACIJA

| Rizik | Verovatnoća | Impact | Mitigacija |
|-------|-------------|--------|------------|
| Loš quality embeddings-a | Medium | High | Testirati više modela, fine-tune |
| False positives | High | Medium | Implementirati confidence threshold |
| Performance sa velikim brojem dokumenata | Medium | High | Optimizovati Qdrant queries, caching |
| Ćirilica vs Latinica | Low | Medium | Normalizacija u pipeline-u |

---

**Autor**: Bob  
**Datum**: 2026-06-08  
**Verzija**: 1.0