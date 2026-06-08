# Conditional Logic Extractor Module

## Overview

This module extracts conditional logic structures (IF-THEN-UNLESS) from legal text, including conditions, consequences, and exceptions.

## Features

- **Condition Extraction**: IF, WHEN, PROVIDED THAT clauses
- **Consequence Extraction**: THEN, MUST, SHALL, MAY clauses
- **Exception Extraction**: UNLESS, EXCEPT, EXCLUDING clauses
- **Rule Extraction**: Complete IF-THEN-UNLESS structures
- **Nested Logic**: Complex and nested conditional statements

## Usage

```python
from modules.conditional_logic_extractor import extract_conditional_logic

text = """
Član 1.

Ako zaposleni ima više od 5 godina staža, tada ima pravo na dodatak.

Ukoliko poslodavac ne ispuni obavezu, mora platiti kaznu.

Zaposleni može koristiti godišnji odmor, osim ako postoje vanredne okolnosti.
"""

result = extract_conditional_logic(text)

print(f"Conditions: {len(result['content']['conditions'])}")
print(f"Consequences: {len(result['content']['consequences'])}")
print(f"Exceptions: {len(result['content']['exceptions'])}")
print(f"Rules: {len(result['content']['rules'])}")
```

## Output Format

```json
{
  "content": {
    "conditions": [
      {
        "condition_text": "zaposleni ima više od 5 godina staža",
        "condition_type": "if",
        "context": "Ako zaposleni ima više od 5 godina staža,",
        "line_number": 3
      }
    ],
    "consequences": [
      {
        "consequence_text": "ima pravo na dodatak.",
        "consequence_type": "then",
        "context": "tada ima pravo na dodatak.",
        "line_number": 3
      },
      {
        "consequence_text": "platiti kaznu.",
        "consequence_type": "must",
        "context": "mora platiti kaznu.",
        "line_number": 5
      }
    ],
    "exceptions": [
      {
        "exception_text": "postoje vanredne okolnosti.",
        "exception_type": "unless",
        "context": "osim ako postoje vanredne okolnosti.",
        "line_number": 7
      }
    ],
    "rules": [
      {
        "conditions": [...],
        "consequences": [...],
        "exceptions": [],
        "rule_text": "Ako zaposleni ima više od 5 godina staža, tada ima pravo na dodatak.",
        "rule_type": "simple",
        "line_number": 3
      }
    ]
  },
  "processing_time": 0.004,
  "total_elements": 7
}
```

## Pattern Detection

### Conditions (IF, WHEN)

- **ako** (if)
- **ukoliko** (if)
- **kada** (when)
- **u slučaju** (in case)
- **u slučaju da** (in case that)
- **pod uslovom da** (provided that)

### Consequences (THEN, MUST, MAY)

- **tada** (then)
- **onda** (then)
- **mora** (must)
- **dužan je** (is obliged to)
- **obavezan je** (is required to)
- **može** (may)
- **ima pravo** (has the right to)

### Exceptions (UNLESS, EXCEPT)

- **osim** (except)
- **izuzev** (except)
- **sem** (except)
- **osim ako** (unless)
- **izuzev ako** (except if)
- **sem ako** (except if)
- **osim u slučaju** (except in case)

### Rule Types

**Simple Rules:**
```
IF condition THEN consequence
```

**Complex Rules:**
```
IF condition1 AND condition2 THEN consequence
```

**Nested Rules:**
```
IF condition1, AND IF condition2, THEN consequence
```

**Rules with Exceptions:**
```
IF condition THEN consequence UNLESS exception
```

## Conflict Detection Support

This module supports conflict detection by:

1. **Conditional Conflicts**: Different consequences for same condition
2. **Exception Conflicts**: Contradictory exceptions
3. **Logic Violations**: Impossible or contradictory conditions
4. **Nested Logic Conflicts**: Inconsistent nested conditions
5. **Consequence Conflicts**: Multiple conflicting consequences

## Examples

### Simple Conditional
```
Ako zaposleni ima više od 10 godina staža, ima pravo na dodatak.
```
- Condition: "zaposleni ima više od 10 godina staža"
- Consequence: "ima pravo na dodatak"

### Conditional with Exception
```
Zaposleni može koristiti godišnji odmor, osim ako postoje vanredne okolnosti.
```
- Consequence: "može koristiti godišnji odmor"
- Exception: "postoje vanredne okolnosti"

### Nested Conditional
```
Ako zaposleni ima više od 5 godina staža, a ako je ispunio sve obaveze, tada ima pravo na bonus.
```
- Condition 1: "zaposleni ima više od 5 godina staža"
- Condition 2: "ispunio sve obaveze"
- Consequence: "ima pravo na bonus"

## Performance

- Processing time: ~4ms per document
- Memory usage: Minimal (compiled regex patterns cached)
- Scalability: Can process thousands of documents efficiently

## Dependencies

- Python 3.8+
- pydantic
- No external NLP libraries required (pure regex)

## Integration

This module integrates with:
- **Normative Extractor**: Links conditions to obligations/permissions
- **Quantitative Extractor**: Associates numeric values with conditions
- **Temporal Linker**: Links time constraints to conditional logic
- **Conflict Detector**: Identifies logical conflicts and contradictions