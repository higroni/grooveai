# Analiza Parsinga i Pretprocesiranja za Detekciju Konflikata

## Datum: 2026-06-08
## Autor: Bob (AI Assistant)

---

## 1. EXECUTIVE SUMMARY

Nakon analize trenutnih JSON export-a i specifikacije 127 tipova konflikata, identifikovao sam **kritične nedostatke** u trenutnom procesu parsinga koji će značajno otežati ili onemogućiti detekciju većine tipova konflikata.

**Ključni problem**: Trenutni parser ekstraktuje samo **strukturne elemente** (članove, stavove, tačke) ali **ne ekstraktuje semantički sadržaj** potreban za detekciju konflikata.

---

## 2. TRENUTNO STANJE - ŠTA IMAMO

### 2.1 Uspešno Ekstrahovani Podaci

✅ **Strukturni elementi**:
- Članovi (Član 1, Član 2, itd.)
- Stavovi (stav 1, stav 2)
- Tačke (tačka 1, tačka 2)
- Hijerarhija (parent-child odnosi)

✅ **Osnovni entiteti**:
- LEGAL_REF (reference na članove)
- DATE (datumi)
- DURATION (trajanja)
- MONEY (novčani iznosi)
- LOCATION (lokacije)
- PERSON (osobe)
- ORGANIZATION (organizacije)

✅ **Metadata**:
- Naslov dokumenta
- Službeni glasnik
- Tip dokumenta
- Jezik

### 2.2 Primer Trenutnog Output-a

```json
{
  "legal_units": [
    {
      "unit_id": "art_1",
      "unit_type": "article",
      "number": "1",
      "title": "Predmet",
      "content": "Prava, obaveze i odgovornosti iz radnog odnosa...",
      "parent_id": null,
      "level": 1
    }
  ],
  "document_entities": [
    {
      "entity_type": "LEGAL_REF",
      "text": "člana 112",
      "confidence": 0.8
    }
  ]
}
```

---

## 3. ŠTA NAM NEDOSTAJE - KRITIČNI GAPOVI

### 3.1 Normativni Sadržaj (Category 1: 16 tipova)

**Problem**: Ne ekstraktujemo **normativne iskaze** potrebne za detekciju konflikata.

#### Šta nam treba:

1. **Obaveze (Obligations)**
   ```python
   {
     "type": "obligation",
     "subject": "Poslodavac",
     "action": "isplati",
     "object": "naknadu",
     "modality": "dužan je",
     "condition": "u roku od 15 dana",
     "temporal": {"deadline": "15 dana"}
   }
   ```

2. **Zabrane (Prohibitions)**
   ```python
   {
     "type": "prohibition",
     "subject": "Poslodavac",
     "action": "zapošljavanje",
     "object": "lica mlađih od 18 godina",
     "modality": "zabranjeno je"
   }
   ```

3. **Dozvole (Permissions)**
   ```python
   {
     "type": "permission",
     "subject": "Zaposleni",
     "action": "rad",
     "object": "noćni rad",
     "modality": "može",
     "condition": "uz pisanu saglasnost"
   }
   ```

4. **Definicije (Definitions)**
   ```python
   {
     "type": "definition",
     "term": "Zaposleni",
     "definition": "fizičko lice koje je u radnom odnosu",
     "scope": "u smislu ovog zakona"
   }
   ```

**Primeri konflikata koje NE MOŽEMO detektovati**:
- ❌ Contradictory Obligation (različiti rokovi za istu obavezu)
- ❌ Contradictory Prohibition (nacrt zabranjuje ono što korpus dozvoljava)
- ❌ Conflicting Definition (različite definicije istog pojma)
- ❌ Overlapping Scope (isti predmet regulisan različitim pravilima)

### 3.2 Temporalni Elementi (Category 2: 15 tipova)

**Problem**: Ekstraktujemo DATE i DURATION ali **ne povezujemo ih sa normativnim iskazima**.

#### Šta nam treba:

```python
{
  "temporal_element": {
    "type": "deadline",
    "value": "15 dana",
    "reference_point": "od dana dostavljanja",
    "applies_to": "obligation_id_123",
    "is_mandatory": true,
    "can_be_extended": false
  }
}
```

**Primeri konflikata koje NE MOŽEMO detektovati**:
- ❌ Deadline Conflict (različiti rokovi za istu radnju)
- ❌ Grace Period Conflict (različiti periodi prilagođavanja)
- ❌ Notice Period Conflict (različiti otkazni rokovi)

### 3.3 Hijerarhijski Kontekst (Category 3: 18 tipova)

**Problem**: Ne ekstraktujemo **pravnu snagu** i **hijerarhiju propisa**.

#### Šta nam treba:

```python
{
  "legal_hierarchy": {
    "document_level": "law",  # zakon, pravilnik, uredba, odluka
    "issuing_authority": "Vlada Republike Srbije",
    "legal_basis": ["član 112 Zakona o radu"],
    "can_override": ["pravilnik", "odluka"],
    "cannot_override": ["zakon", "ustav"]
  }
}
```

**Primeri konflikata koje NE MOŽEMO detektovati**:
- ❌ Primary Law Conflict (pravilnik u suprotnosti sa zakonom)
- ❌ Constitutional Violation (kršenje ustavnog prava)
- ❌ Superior Regulation Conflict (suprotnost sa višim propisom)

### 3.4 Kvantitativni Standardi (Category 4)

**Problem**: Ekstraktujemo MONEY i DURATION ali **ne povezujemo ih sa standardima**.

#### Šta nam treba:

```python
{
  "standard": {
    "type": "minimum_wage",
    "value": 371.00,
    "unit": "dinara",
    "per": "radni čas",
    "applies_to": "svi zaposleni",
    "effective_from": "2026-01-01",
    "comparison_operator": "najmanje"  # najmanje, najviše, tačno
  }
}
```

**Primeri konflikata koje NE MOŽEMO detektovati**:
- ❌ Conflicting Standard (različiti standardi za iste uslove)
- ❌ Incompatible Limitation (nekompatibilna ograničenja)

### 3.5 Proceduralni Zahtevi (Category 5)

**Problem**: Ne ekstraktujemo **korake procedure** i **redosled radnji**.

#### Šta nam treba:

```python
{
  "procedure": {
    "name": "Postupak za otkaz ugovora",
    "steps": [
      {
        "order": 1,
        "action": "pisano upozorenje",
        "actor": "poslodavac",
        "deadline": "8 dana",
        "mandatory": true
      },
      {
        "order": 2,
        "action": "izjašnjenje zaposlenog",
        "actor": "zaposleni",
        "deadline": "8 dana",
        "mandatory": true
      }
    ]
  }
}
```

### 3.6 Uslovi i Izuzeci (Category 6)

**Problem**: Ne ekstraktujemo **IF-THEN logiku** i **izuzetke**.

#### Šta nam treba:

```python
{
  "conditional": {
    "if_condition": "zaposleni ima manje od 18 godina",
    "then_consequence": "ne može raditi noću",
    "unless_exception": "u oblasti kulture i umetnosti",
    "exception_conditions": ["uz saglasnost roditelja"]
  }
}
```

### 3.7 Prava i Obaveze Subjekata (Category 7)

**Problem**: Ne ekstraktujemo **ko ima koje pravo/obavezu**.

#### Šta nam treba:

```python
{
  "right": {
    "holder": "Zaposleni",
    "type": "pravo na godišnji odmor",
    "minimum": "20 radnih dana",
    "conditions": ["nakon mesec dana rada"],
    "cannot_be_waived": true
  }
}
```

### 3.8 Sankcije i Posledice (Category 8)

**Problem**: Ne ekstraktujemo **kazne** i **pravne posledice**.

#### Šta nam treba:

```python
{
  "sanction": {
    "violation": "neisplata zarade",
    "sanction_type": "novčana kazna",
    "amount_min": 800000,
    "amount_max": 2000000,
    "currency": "RSD",
    "applies_to": "pravno lice"
  }
}
```

---

## 4. KONKRETNI PRIMERI - ZAŠTO NE MOŽEMO DETEKTOVATI KONFLIKTE

### Primer 1: Contradictory Obligation

**Dokument A** (radni_odnosi_0001):
```
"Poslodavac je dužan da isplati zaradu u roku od 30 dana"
```

**Dokument B** (radni_odnosi_0002):
```
"Poslodavac je dužan da isplati zaradu u roku od 15 dana"
```

**Trenutni output**:
```json
{
  "document_A": {
    "entities": [
      {"type": "DURATION", "text": "30 dana"}
    ]
  },
  "document_B": {
    "entities": [
      {"type": "DURATION", "text": "15 dana"}
    ]
  }
}
```

**Problem**: Imamo trajanja, ali ne znamo:
- ❌ Da se oba odnose na ISTU obavezu (isplata zarade)
- ❌ Da je subjekt isti (poslodavac)
- ❌ Da je akcija ista (isplata)
- ❌ Da su rokovi različiti (konflikt!)

**Šta nam treba**:
```json
{
  "document_A": {
    "obligations": [{
      "subject": "Poslodavac",
      "action": "isplati",
      "object": "zaradu",
      "deadline": {"value": 30, "unit": "dana"}
    }]
  },
  "document_B": {
    "obligations": [{
      "subject": "Poslodavac",
      "action": "isplati",
      "object": "zaradu",
      "deadline": {"value": 15, "unit": "dana"}
    }]
  }
}
```

### Primer 2: Primary Law Conflict

**Zakon o radu**:
```
"Otkazni rok ne može biti kraći od 15 dana"
```

**Pravilnik**:
```
"Otkazni rok je 7 dana"
```

**Trenutni output**:
```json
{
  "zakon": {
    "document_type": "law",
    "entities": [{"type": "DURATION", "text": "15 dana"}]
  },
  "pravilnik": {
    "document_type": "law",  // ❌ Nema razliku između zakona i pravilnika!
    "entities": [{"type": "DURATION", "text": "7 dana"}]
  }
}
```

**Problem**:
- ❌ Ne znamo da je pravilnik NIŽI propis od zakona
- ❌ Ne znamo da pravilnik NE SME biti u suprotnosti sa zakonom
- ❌ Ne znamo da se oba odnose na ISTI koncept (otkazni rok)

---

## 5. PREPORUKE ZA POBOLJŠANJE

### 5.1 PRIORITET 1: Normativna Ekstrakcija (KRITIČNO)

**Implementirati NLP modul za ekstrakciju normativnih iskaza**:

```python
class NormativeExtractor:
    """Ekstraktuje obaveze, zabrane, dozvole, definicije"""
    
    def extract_obligations(self, text: str) -> List[Obligation]:
        """
        Detektuje:
        - "dužan je", "mora", "obavezan je"
        - Subjekt + akcija + objekat
        - Uslovi i rokovi
        """
        pass
    
    def extract_prohibitions(self, text: str) -> List[Prohibition]:
        """
        Detektuje:
        - "zabranjeno je", "ne može", "ne sme"
        - Subjekt + akcija + objekat
        """
        pass
    
    def extract_permissions(self, text: str) -> List[Permission]:
        """
        Detektuje:
        - "može", "ima pravo", "dozvoljeno je"
        - Subjekt + akcija + objekat + uslovi
        """
        pass
    
    def extract_definitions(self, text: str) -> List[Definition]:
        """
        Detektuje:
        - "u smislu ovog zakona", "smatra se"
        - Term + definicija + scope
        """
        pass
```

**Tehnologije**:
- spaCy dependency parsing
- Pattern matching sa regex
- Rule-based extraction
- (Opciono) Fine-tuned BERT model za srpski pravni jezik

### 5.2 PRIORITET 2: Temporalna Analiza

**Povezati temporalne elemente sa normativnim iskazima**:

```python
class TemporalLinker:
    """Povezuje datume/trajanja sa obavezama/zabranama"""
    
    def link_deadlines(
        self,
        obligations: List[Obligation],
        temporal_entities: List[Entity]
    ) -> List[Obligation]:
        """Dodaje deadline informacije obavezama"""
        pass
    
    def extract_effective_dates(self, text: str) -> List[EffectiveDate]:
        """Ekstraktuje datume stupanja na snagu"""
        pass
```

### 5.3 PRIORITET 3: Hijerarhijska Klasifikacija

**Dodati pravnu snagu dokumentima**:

```python
class LegalHierarchyClassifier:
    """Klasifikuje dokumente po pravnoj snazi"""
    
    HIERARCHY = {
        "ustav": 1,
        "zakon": 2,
        "uredba": 3,
        "pravilnik": 4,
        "odluka": 5,
        "naređenje": 6
    }
    
    def classify_document(self, text: str, metadata: dict) -> str:
        """
        Detektuje tip dokumenta:
        - Iz naslova ("ZAKON o radu")
        - Iz osnova ("Na osnovu člana X Zakona...")
        - Iz izdavaoca ("Vlada donosi UREDBU...")
        """
        pass
    
    def extract_legal_basis(self, text: str) -> List[str]:
        """Ekstraktuje pravni osnov ("Na osnovu člana...")"""
        pass
```

### 5.4 PRIORITET 4: Kvantitativna Ekstrakcija

**Povezati brojeve sa standardima**:

```python
class QuantitativeExtractor:
    """Ekstraktuje kvantitativne standarde"""
    
    def extract_standards(self, text: str) -> List[Standard]:
        """
        Detektuje:
        - "najmanje X", "najviše Y", "tačno Z"
        - Jedinice mere
        - Šta se meri
        """
        pass
    
    def extract_thresholds(self, text: str) -> List[Threshold]:
        """Ekstraktuje pragove i limite"""
        pass
```

### 5.5 PRIORITET 5: Proceduralna Ekstrakcija

**Ekstraktovati korake procedura**:

```python
class ProceduralExtractor:
    """Ekstraktuje procedure i korake"""
    
    def extract_procedures(self, text: str) -> List[Procedure]:
        """
        Detektuje:
        - Redosled koraka
        - Aktere
        - Rokove za svaki korak
        - Obaveznost koraka
        """
        pass
```

### 5.6 PRIORITET 6: Uslovnu Logiku

**Ekstraktovati IF-THEN-UNLESS strukture**:

```python
class ConditionalExtractor:
    """Ekstraktuje uslove i izuzetke"""
    
    def extract_conditionals(self, text: str) -> List[Conditional]:
        """
        Detektuje:
        - "ako", "ukoliko", "u slučaju"
        - "osim ako", "izuzev", "sem"
        - Uslove i posledice
        """
        pass
```

---

## 6. IMPLEMENTACIONI PLAN

### Faza 1: Normativna Ekstrakcija (2-3 nedelje)
1. Implementirati `NormativeExtractor`
2. Testirati na 100 dokumenata
3. Postići >80% accuracy

### Faza 2: Temporalna i Hijerarhijska (1-2 nedelje)
1. Implementirati `TemporalLinker`
2. Implementirati `LegalHierarchyClassifier`
3. Integracija sa postojećim parserom

### Faza 3: Kvantitativna i Proceduralna (1-2 nedelje)
1. Implementirati `QuantitativeExtractor`
2. Implementirati `ProceduralExtractor`
3. Testiranje na realnim dokumentima

### Faza 4: Uslovna Logika (1 nedelja)
1. Implementirati `ConditionalExtractor`
2. Integracija svih komponenti

### Faza 5: Validacija (1 nedelja)
1. End-to-end testiranje
2. Evaluacija na test setu
3. Fine-tuning

**Ukupno vreme**: 6-9 nedelja

---

## 7. ALTERNATIVNI PRISTUP: LLM-Based Extraction

### Prednosti:
- ✅ Brža implementacija (1-2 nedelje)
- ✅ Bolja generalizacija
- ✅ Lakše održavanje

### Nedostaci:
- ❌ Veći troškovi (API calls)
- ❌ Sporije izvršavanje
- ❌ Zavisnost od eksternog servisa

### Hibridni Pristup (PREPORUČENO):
1. **Rule-based** za strukturne elemente (trenutno rešenje)
2. **LLM-based** za semantičku ekstrakciju (novi modul)
3. **Kombinacija** za najbolje rezultate

```python
class HybridExtractor:
    """Kombinuje rule-based i LLM pristup"""
    
    def __init__(self):
        self.rule_based = NormativeExtractor()
        self.llm_based = LLMExtractor(model="gpt-4")
    
    def extract(self, text: str) -> Dict:
        # Prvo rule-based (brzo, jeftino)
        rules_result = self.rule_based.extract(text)
        
        # Ako confidence < 0.8, koristi LLM
        if rules_result.confidence < 0.8:
            llm_result = self.llm_based.extract(text)
            return llm_result
        
        return rules_result
```

---

## 8. IMPACT ANALIZA

### Bez Poboljšanja:
- ❌ Možemo detektovati: **~10-15%** konflikata (samo strukturne)
- ❌ Ne možemo detektovati: **~85-90%** konflikata (semantičke)

### Sa Poboljšanjima:
- ✅ Možemo detektovati: **~70-80%** konflikata
- ⚠️ Potrebna dodatna validacija: **~20-30%**

### ROI:
- **Investicija**: 6-9 nedelja razvoja
- **Povraćaj**: 6x više detektovanih konflikata
- **Vrednost**: Kritično za uspeh projekta

---

## 9. ZAKLJUČAK

**Trenutno stanje**: Imamo solidnu osnovu za strukturno parsiranje, ali **kritično nam nedostaje semantička ekstrakcija**.

**Ključna preporuka**: **Implementirati normativnu ekstrakciju kao PRIORITET 1** pre nego što krenemo sa importom u Qdrant. Bez toga, Qdrant će imati samo "prazne školjke" - strukturu bez semantike.

**Sledeći koraci**:
1. ✅ Završiti batch processing (trenutno)
2. 🔴 Implementirati normativnu ekstrakciju (KRITIČNO)
3. 🟡 Dodati temporalnu i hijerarhijsku analizu
4. 🟢 Import u Qdrant sa bogatim podacima

**Alternativa**: Ako nemamo resurse za punu implementaciju, možemo krenuti sa **LLM-based pristupom** koji će dati brže rezultate, ali sa većim troškovima.

---

## 10. DODATAK: Primer Idealnog Output-a

```json
{
  "document": {
    "name": "Zakon o radu",
    "legal_level": "zakon",
    "hierarchy_rank": 2,
    "issuing_authority": "Narodna skupština",
    "legal_basis": []
  },
  "legal_units": [
    {
      "unit_id": "art_110",
      "content": "Zarada se isplaćuje u rokovima utvrđenim opštim aktom i ugovorom o radu, najmanje jedanput mesečno, a najkasnije do kraja tekućeg meseca za prethodni mesec.",
      "normative_content": {
        "obligations": [
          {
            "subject": "Poslodavac",
            "action": "isplati",
            "object": "zaradu",
            "modality": "dužan je",
            "frequency": "najmanje jedanput mesečno",
            "deadline": {
              "type": "absolute",
              "value": "do kraja tekućeg meseca",
              "reference": "za prethodni mesec"
            },
            "legal_basis": "opšti akt i ugovor o radu"
          }
        ],
        "standards": [
          {
            "type": "minimum_frequency",
            "value": "jedanput",
            "unit": "mesečno",
            "comparison": "najmanje"
          }
        ]
      },
      "temporal_elements": [
        {
          "type": "deadline",
          "value": "do kraja tekućeg meseca",
          "is_mandatory": true,
          "applies_to": "obligation_isplata_zarade"
        }
      ]
    }
  ]
}
```

Ovakav output omogućava preciznu detekciju svih 127 tipova konflikata!