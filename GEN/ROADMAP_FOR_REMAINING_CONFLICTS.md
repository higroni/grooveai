# Roadmap za Pokrivanje Preostalih Tipova Konflikata

## Datum: 2026-06-08

---

## TRENUTNO STANJE

- ✅ **Pokriveno**: 93/127 tipova (73%)
- 🔄 **Preostalo**: 34 tipa (27%)
  - 13 tipova potpuno nepokriveno (❌)
  - 21 tip delimično pokriven (⚠️)

---

## STRATEGIJA: 3-FAZNI PRISTUP

### FAZA 1: Brza Poboljšanja (2-3 nedelje) → +10 tipova

**Cilj**: Poboljšati postojeće module za delimično pokrivene tipove

**Investicija**: Minimalna (proširenje postojećeg koda)  
**Povraćaj**: 10 tipova → **83% ukupna pokrivenost**

### FAZA 2: Novi Specijalizovani Moduli (3-4 nedelje) → +8 tipova

**Cilj**: Dodati 2-3 nova modula za specifične domene

**Investicija**: Srednja (novi moduli)  
**Povraćaj**: 8 tipova → **89% ukupna pokrivenost**

### FAZA 3: Napredne Funkcionalnosti (4-6 nedelja) → +5 tipova

**Cilj**: Implementirati kompleksne analize

**Investicija**: Velika (AI/ML komponente)  
**Povraćaj**: 5 tipova → **93% ukupna pokrivenost**

---

## FAZA 1: BRZA POBOLJŠANJA (2-3 nedelje)

### 1.1 Proširenje Normative Extractor (+5 tipova)

**Trenutno**: 84% pokrivenost (13.5/16)  
**Cilj**: 100% pokrivenost (16/16)

#### Šta dodati:

```python
class NormativeExtractorEnhanced(NormativeExtractor):
    """Enhanced version with additional capabilities"""
    
    def extract_waivers(self, text: str) -> List[Waiver]:
        """
        Ekstraktuje odricanja od prava
        
        Patterns:
        - "odriče se prava na"
        - "ne može se odreći"
        - "odricanje je ništavo"
        """
        patterns = [
            r'odriče se\s+([^,.;!?]+?[,.;!?])',
            r'ne može se odreći\s+([^,.;!?]+?[,.;!?])',
            r'odricanje\s+([^,.;!?]+?)\s+je ništavo',
        ]
        # Implementation...
    
    def extract_transfers(self, text: str) -> List[Transfer]:
        """
        Ekstraktuje prenose prava/obaveza
        
        Patterns:
        - "prenosi se na"
        - "prelazi na"
        - "ne može se preneti"
        """
        patterns = [
            r'prenosi se na\s+([^,.;!?]+?[,.;!?])',
            r'prelazi na\s+([^,.;!?]+?[,.;!?])',
            r'ne može se preneti',
        ]
        # Implementation...
    
    def extract_assignments(self, text: str) -> List[Assignment]:
        """
        Ekstraktuje ustupanja
        
        Patterns:
        - "ustupa se"
        - "može ustupiti"
        - "ustupanje zahteva saglasnost"
        """
        patterns = [
            r'ustupa se\s+([^,.;!?]+?[,.;!?])',
            r'može ustupiti\s+([^,.;!?]+?[,.;!?])',
            r'ustupanje zahteva\s+([^,.;!?]+?[,.;!?])',
        ]
        # Implementation...
    
    def detect_ambiguity(self, obligation: Obligation) -> float:
        """
        Detektuje ambiguity score za obavezu
        
        Indicators:
        - Vague terms: "odgovarajući", "primeren", "razuman"
        - Multiple interpretations possible
        - Missing specifics
        """
        ambiguity_terms = [
            'odgovarajući', 'primeren', 'razuman', 'potreban',
            'dovoljan', 'adekvatan', 'prikladan'
        ]
        score = sum(1 for term in ambiguity_terms if term in obligation.context.lower())
        return min(1.0, score / 3)
    
    def detect_circular_definition(self, definitions: List[Definition]) -> List[CircularDef]:
        """
        Detektuje kružne definicije
        
        Example:
        - "Zaposleni je lice koje obavlja posao"
        - "Posao je ono što obavlja zaposleni"
        """
        circular = []
        for i, def1 in enumerate(definitions):
            for def2 in definitions[i+1:]:
                if def1.term.lower() in def2.definition.lower() and \
                   def2.term.lower() in def1.definition.lower():
                    circular.append(CircularDef(
                        term1=def1.term,
                        term2=def2.term,
                        definition1=def1.definition,
                        definition2=def2.definition
                    ))
        return circular
```

**Pokriveni tipovi**:
- ✅ Waiver Conflict (trenutno ⚠️)
- ✅ Transfer Conflict (trenutno ⚠️)
- ✅ Assignment Conflict (trenutno ⚠️)
- ✅ Ambiguous Obligation (trenutno ⚠️)
- ✅ Circular Definition (trenutno ⚠️)

**Vreme**: 1 nedelja  
**Kompleksnost**: Niska

---

### 1.2 Proširenje Procedural Extractor (+3 tipa)

**Trenutno**: 79% pokrivenost (11/14)  
**Cilj**: 100% pokrivenost (14/14)

#### Šta dodati:

```python
class ProceduralExtractorEnhanced(ProceduralExtractor):
    """Enhanced version with approval and documentation tracking"""
    
    def extract_approval_authorities(self, text: str) -> List[ApprovalAuthority]:
        """
        Ekstraktuje ko odobrava šta
        
        Patterns:
        - "odobrava direktor"
        - "uz saglasnost ministra"
        - "zahteva odobrenje"
        """
        patterns = [
            r'odobrava\s+([^,.;!?]+?[,.;!?])',
            r'uz saglasnost\s+([^,.;!?]+?[,.;!?])',
            r'zahteva odobrenje\s+([^,.;!?]+?[,.;!?])',
        ]
        # Implementation...
    
    def extract_documentation_requirements(self, text: str) -> List[DocRequirement]:
        """
        Ekstraktuje zahteve za dokumentaciju
        
        Patterns:
        - "prilaže se dokaz"
        - "dostavlja se potvrda"
        - "uz zahtev se prilaže"
        """
        patterns = [
            r'prilaže se\s+([^,.;!?]+?[,.;!?])',
            r'dostavlja se\s+([^,.;!?]+?[,.;!?])',
            r'uz zahtev se prilaže\s+([^,.;!?]+?[,.;!?])',
        ]
        # Implementation...
    
    def extract_form_requirements(self, text: str) -> List[FormRequirement]:
        """
        Ekstraktuje zahteve za formu
        
        Patterns:
        - "u pisanoj formi"
        - "elektronski"
        - "overeno"
        """
        patterns = [
            r'u pisanoj formi',
            r'elektronski',
            r'overeno',
            r'na propisanom obrascu',
        ]
        # Implementation...
```

**Pokriveni tipovi**:
- ✅ Approval Authority Conflict (trenutno ⚠️)
- ✅ Documentation Conflict (trenutno ⚠️)
- ✅ Form Requirement Conflict (trenutno ⚠️)

**Vreme**: 3-4 dana  
**Kompleksnost**: Niska

---

### 1.3 Proširenje Conditional Logic Extractor (+2 tipa)

**Trenutno**: 82% pokrivenost (9/11)  
**Cilj**: 100% pokrivenost (11/11)

#### Šta dodati:

```python
class ConditionalLogicExtractorEnhanced(ConditionalLogicExtractor):
    """Enhanced version with circular and impossible condition detection"""
    
    def detect_circular_conditions(self, rules: List[ConditionalRule]) -> List[CircularCondition]:
        """
        Detektuje kružne uslove
        
        Example:
        - "Ako A, tada B"
        - "Ako B, tada A"
        """
        circular = []
        for i, rule1 in enumerate(rules):
            for rule2 in rules[i+1:]:
                # Check if rule1's consequence is rule2's condition
                # and vice versa
                if self._is_circular(rule1, rule2):
                    circular.append(CircularCondition(
                        rule1=rule1,
                        rule2=rule2
                    ))
        return circular
    
    def detect_impossible_conditions(self, rule: ConditionalRule) -> bool:
        """
        Detektuje nemoguce uslove
        
        Examples:
        - "Ako je zaposleni mlađi od 18 i stariji od 65"
        - "Ako je radni dan subota ili nedelja"
        """
        # Check for contradictory conditions
        conditions_text = ' '.join([c.condition_text for c in rule.conditions])
        
        # Age contradictions
        if 'mlađi' in conditions_text and 'stariji' in conditions_text:
            ages = re.findall(r'(\d+)\s+godina', conditions_text)
            if len(ages) >= 2 and int(ages[0]) > int(ages[1]):
                return True
        
        # Day contradictions
        if 'radni dan' in conditions_text and ('subota' in conditions_text or 'nedelja' in conditions_text):
            return True
        
        return False
```

**Pokriveni tipovi**:
- ✅ Circular Condition (trenutno ⚠️)
- ✅ Impossible Condition (trenutno ⚠️)

**Vreme**: 2-3 dana  
**Kompleksnost**: Srednja

---

## FAZA 2: NOVI SPECIJALIZOVANI MODULI (3-4 nedelje)

### 2.1 Sanctions Analyzer Module (+3 tipa)

**Novi modul**: `modules/sanctions_analyzer/`

**Cilj**: Detaljno ekstraktovanje sankcija i pravnih posledica

```python
class SanctionsAnalyzer:
    """Analyzes sanctions, penalties, and enforcement mechanisms"""
    
    def extract_enforcement_mechanisms(self, text: str) -> List[EnforcementMechanism]:
        """
        Ekstraktuje mehanizme izvršenja
        
        Patterns:
        - "izvršava se prinudno"
        - "inspekcija vrši nadzor"
        - "sud donosi rešenje o izvršenju"
        """
        pass
    
    def extract_mitigation_factors(self, text: str) -> List[MitigationFactor]:
        """
        Ekstraktuje olakšavajuće okolnosti
        
        Patterns:
        - "kazna se može ublažiti"
        - "olakšavajuća okolnost"
        - "može se osloboditi od kazne"
        """
        pass
    
    def extract_aggravation_factors(self, text: str) -> List[AggravationFactor]:
        """
        Ekstraktuje otežavajuće okolnosti
        
        Patterns:
        - "kazna se pooštrava"
        - "otežavajuća okolnost"
        - "ponovljeni prekršaj"
        """
        pass
```

**Pokriveni tipovi**:
- ✅ Enforcement Conflict (trenutno ❌)
- ✅ Mitigation Conflict (trenutno ❌)
- ✅ Aggravation Conflict (trenutno ❌)

**Vreme**: 1-2 nedelje  
**Kompleksnost**: Srednja

---

### 2.2 Financial Instruments Analyzer (+2 tipa)

**Novi modul**: `modules/financial_analyzer/`

**Cilj**: Ekstraktovanje finansijskih instrumenata i garancija

```python
class FinancialInstrumentsAnalyzer:
    """Analyzes financial instruments, guarantees, and securities"""
    
    def extract_guarantees(self, text: str) -> List[Guarantee]:
        """
        Ekstraktuje garancije
        
        Patterns:
        - "garantuje se"
        - "jemstvo"
        - "bankarska garancija"
        """
        pass
    
    def extract_securities(self, text: str) -> List[Security]:
        """
        Ekstraktuje hartije od vrednosti i obezbeđenja
        
        Patterns:
        - "založno pravo"
        - "hipoteka"
        - "obezbeđenje"
        """
        pass
    
    def extract_indemnifications(self, text: str) -> List[Indemnification]:
        """
        Ekstraktuje odštete i naknade
        
        Patterns:
        - "naknada štete"
        - "odšteta"
        - "obeštetiti"
        """
        pass
```

**Pokriveni tipovi**:
- ✅ Guarantee Conflict (trenutno ❌)
- ✅ Security Conflict (trenutno ❌)
- ⚠️ Indemnification Conflict (trenutno ❌) - delimično, jer je kompleksan

**Vreme**: 1-2 nedelje  
**Kompleksnost**: Srednja-Visoka

---

### 2.3 Proširenje Existing Modules (+3 tipa)

#### Legal Hierarchy Enhancement

```python
def extract_jurisdiction_details(self, text: str) -> JurisdictionInfo:
    """
    Ekstraktuje detalje o nadležnosti
    
    Patterns:
    - "nadležan je"
    - "u nadležnosti"
    - "teritorijalna nadležnost"
    """
    pass

def extract_competence_details(self, text: str) -> CompetenceInfo:
    """
    Ekstraktuje detalje o kompetenciji
    
    Patterns:
    - "u okviru svojih ovlašćenja"
    - "nadležnost za"
    - "kompetencija"
    """
    pass
```

**Pokriveni tipovi**:
- ✅ Jurisdiction Conflict (trenutno ⚠️)
- ✅ Competence Conflict (trenutno ⚠️)
- ✅ Parallel Authority (trenutno ⚠️)

**Vreme**: 3-5 dana  
**Kompleksnost**: Niska-Srednja

---

## FAZA 3: NAPREDNE FUNKCIONALNOSTI (4-6 nedelja)

### 3.1 Legal Interpretation Module (+2 tipa)

**Novi modul**: `modules/legal_interpretation/`

**Tehnologija**: Hybrid (Rule-based + LLM)

```python
class LegalInterpretationAnalyzer:
    """Analyzes legal interpretations and precedents"""
    
    def __init__(self):
        self.llm = OpenAI(model="gpt-4")  # ili lokalni model
        self.precedent_db = PrecedentDatabase()
    
    def extract_interpretations(self, text: str) -> List[Interpretation]:
        """
        Ekstraktuje pravna tumačenja
        
        Uses LLM to understand:
        - "tumači se kao"
        - "u smislu ovog člana"
        - "pod tim se podrazumeva"
        """
        prompt = f"""
        Analiziraj sledeći pravni tekst i ekstraktuj sva tumačenja:
        
        {text}
        
        Vrati JSON sa:
        - term: pojam koji se tumači
        - interpretation: tumačenje
        - scope: opseg primene
        - confidence: sigurnost (0-1)
        """
        response = self.llm.complete(prompt)
        return self._parse_interpretations(response)
    
    def find_precedents(self, text: str) -> List[Precedent]:
        """
        Pronalazi relevantne presedane
        
        Uses vector similarity search in precedent database
        """
        embedding = self.get_embedding(text)
        similar = self.precedent_db.search(embedding, top_k=10)
        return similar
```

**Pokriveni tipovi**:
- ✅ Conflicting Interpretation (trenutno ❌)
- ✅ Precedent Conflict (trenutno ❌)

**Vreme**: 2-3 nedelje  
**Kompleksnost**: Visoka  
**Napomena**: Zahteva LLM API ili lokalni model

---

### 3.2 Multi-language Support (+1 tip)

**Proširenje**: Svi postojeći moduli

```python
class MultiLanguageExtractor:
    """Supports multiple languages and detects translation conflicts"""
    
    def __init__(self):
        self.translators = {
            'sr': SerbianExtractor(),
            'en': EnglishExtractor(),
            'fr': FrenchExtractor()
        }
    
    def extract_multilingual(self, texts: Dict[str, str]) -> MultilingualResult:
        """
        Ekstraktuje iz više jezika i poredi
        
        Args:
            texts: {'sr': 'tekst na srpskom', 'en': 'text in English'}
        
        Returns:
            Comparison of extractions with conflict detection
        """
        results = {}
        for lang, text in texts.items():
            results[lang] = self.translators[lang].extract(text)
        
        conflicts = self._compare_results(results)
        return MultilingualResult(results=results, conflicts=conflicts)
```

**Pokriveni tipovi**:
- ✅ Translation Conflict (trenutno ❌)
- ⚠️ Language Conflict (trenutno ❌) - delimično

**Vreme**: 2-3 nedelje  
**Kompleksnost**: Visoka

---

### 3.3 Judicial Review Analyzer (+1 tip)

**Novi modul**: `modules/judicial_review/`

**Tehnologija**: Hybrid (Database + LLM)

```python
class JudicialReviewAnalyzer:
    """Analyzes judicial review decisions and constitutional court rulings"""
    
    def __init__(self):
        self.court_db = CourtDecisionDatabase()
        self.llm = OpenAI(model="gpt-4")
    
    def find_judicial_reviews(self, document_id: str) -> List[JudicialReview]:
        """
        Pronalazi sudske odluke o ustavnosti/zakonitosti
        
        Searches court database for:
        - Constitutional court decisions
        - Supreme court rulings
        - Administrative court decisions
        """
        return self.court_db.search_by_document(document_id)
    
    def analyze_constitutionality(self, text: str) -> ConstitutionalityAnalysis:
        """
        Analizira ustavnost odredbe
        
        Uses LLM to assess:
        - Potential constitutional violations
        - Relevant constitutional provisions
        - Similar cases
        """
        pass
```

**Pokriveni tipovi**:
- ✅ Judicial Review Conflict (trenutno ❌)

**Vreme**: 1-2 nedelje  
**Kompleksnost**: Visoka  
**Napomena**: Zahteva pristup bazi sudskih odluka

---

## IMPLEMENTACIONI PLAN

### Timeline

| Faza | Trajanje | Tipovi | Kumulativno | % |
|------|----------|--------|-------------|---|
| Trenutno | - | 93 | 93 | 73% |
| Faza 1 | 2-3 nedelje | +10 | 103 | 81% |
| Faza 2 | 3-4 nedelje | +8 | 111 | 87% |
| Faza 3 | 4-6 nedelja | +5 | 116 | 91% |
| **UKUPNO** | **9-13 nedelja** | **+23** | **116** | **91%** |

### Resursi

**Faza 1** (Brza poboljšanja):
- 1 developer
- Bez dodatnih troškova
- Koristi postojeću infrastrukturu

**Faza 2** (Novi moduli):
- 1-2 developers
- Minimalni troškovi
- Koristi postojeću infrastrukturu

**Faza 3** (Napredne funkcionalnosti):
- 2 developers
- LLM API troškovi (~$100-500/mesec)
- Pristup bazama sudskih odluka
- Opciono: GPU za lokalni LLM

### Prioritizacija

#### Must-Have (Faza 1)
- ✅ Brza implementacija
- ✅ Visok ROI
- ✅ Niska kompleksnost
- ✅ Bez dodatnih troškova

#### Should-Have (Faza 2)
- ✅ Srednja implementacija
- ✅ Dobar ROI
- ⚠️ Srednja kompleksnost
- ⚠️ Minimalni troškovi

#### Nice-to-Have (Faza 3)
- ⚠️ Duga implementacija
- ⚠️ Srednji ROI
- ❌ Visoka kompleksnost
- ❌ Značajni troškovi

---

## ALTERNATIVNI PRISTUP: LLM-First

### Koncept

Umesto rule-based pristupa, koristiti LLM za sve preostale tipove:

```python
class LLMConflictDetector:
    """Uses LLM to detect all remaining conflict types"""
    
    def __init__(self):
        self.llm = OpenAI(model="gpt-4")
    
    def detect_all_conflicts(self, doc1: str, doc2: str) -> List[Conflict]:
        """
        Koristi LLM za detekciju svih konflikata
        
        Prompt engineering:
        - Daj LLM-u listu svih 127 tipova
        - Traži da analizira oba dokumenta
        - Vrati strukturirane rezultate
        """
        prompt = f"""
        Analiziraj sledeća dva pravna dokumenta i detektuj sve konflikte.
        
        Tipovi konflikata: {CONFLICT_TYPES}
        
        Dokument 1:
        {doc1}
        
        Dokument 2:
        {doc2}
        
        Vrati JSON sa svim detektovanim konfliktima.
        """
        response = self.llm.complete(prompt)
        return self._parse_conflicts(response)
```

### Prednosti
- ✅ Brza implementacija (1-2 nedelje)
- ✅ Pokriva SVE tipove konflikata
- ✅ Bolja generalizacija
- ✅ Lakše održavanje

### Nedostaci
- ❌ Visoki troškovi ($1000-5000/mesec za 8000 dokumenata)
- ❌ Sporije izvršavanje (5-10s po paru dokumenata)
- ❌ Zavisnost od eksternog servisa
- ❌ Manja kontrola nad kvalitetom

### Hibridni Pristup (PREPORUČENO)

```python
class HybridConflictDetector:
    """Combines rule-based and LLM approaches"""
    
    def __init__(self):
        self.rule_based = RuleBasedDetector()  # Naši moduli
        self.llm_based = LLMConflictDetector()
    
    def detect_conflicts(self, doc1: str, doc2: str) -> List[Conflict]:
        # Prvo rule-based (brzo, jeftino, 91% tipova)
        rule_conflicts = self.rule_based.detect(doc1, doc2)
        
        # Ako je confidence nizak ili ima nepoznate tipove
        if self._needs_llm_verification(rule_conflicts):
            llm_conflicts = self.llm_based.detect(doc1, doc2)
            return self._merge_results(rule_conflicts, llm_conflicts)
        
        return rule_conflicts
```

**Optimalna strategija**:
- Rule-based za 91% tipova (Faza 1-3)
- LLM za preostalih 9% (11 tipova)
- Troškovi: ~$100-200/mesec
- Pokrivenost: 100%

---

## ZAKLJUČAK

### Preporuka: Fazni Pristup

1. **Odmah**: Implementirati Fazu 1 (2-3 nedelje, +10 tipova → 81%)
2. **Kratkoročno**: Implementirati Fazu 2 (3-4 nedelje, +8 tipova → 87%)
3. **Dugoročno**: Evaluirati potrebu za Fazom 3 ili LLM pristupom

### Realistična Meta

**91% pokrivenost (116/127 tipova)** je odličan rezultat koji pokriva sve praktične slučajeve.

Preostalih 11 tipova (9%) su edge cases koji se retko javljaju:
- Judicial Review Conflict
- Pari Passu Conflict
- Formatting Conflict
- Language Conflict
- Translation Conflict
- itd.

### ROI Analiza

| Pristup | Vreme | Troškovi | Pokrivenost | ROI |
|---------|-------|----------|-------------|-----|
| Trenutno | - | $0 | 73% | - |
| Faza 1 | 2-3 ned | $0 | 81% | Odličan |
| Faza 1+2 | 5-7 ned | $0 | 87% | Vrlo dobar |
| Faza 1+2+3 | 9-13 ned | $1000-2000 | 91% | Dobar |
| LLM-only | 1-2 ned | $5000/god | 95% | Loš |
| Hybrid | 9-13 ned | $1500/god | 100% | Odličan |

**Preporuka**: Implementirati Fazu 1 i 2, zatim evaluirati potrebu za Fazom 3 ili hibridnim pristupom.