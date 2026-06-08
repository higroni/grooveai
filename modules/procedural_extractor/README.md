# Procedural Extractor Module

## Overview

This module extracts procedural information including steps, sequences, actors, and dependencies from legal text.

## Features

- **Step Extraction**: Identifies procedural steps with actions, actors, and deadlines
- **Sequence Detection**: Recognizes ordered, parallel, and conditional sequences
- **Actor Identification**: Extracts participants and their roles
- **Dependency Mapping**: Identifies prerequisites and relationships between steps

## Usage

```python
from modules.procedural_extractor import extract_procedural

text = """
Postupak za izdavanje dozvole:

1) Podnosilac podnosi zahtev nadležnom organu u roku od 30 dana.
2) Organ vrši proveru dokumentacije u roku od 15 dana.
3) Nakon provere, organ donosi rešenje u roku od 8 dana.

Poslodavac je dužan da obavesti zaposlenog o odluci.
"""

result = extract_procedural(text)

print(f"Steps: {len(result['content']['steps'])}")
print(f"Actors: {len(result['content']['actors'])}")
print(f"Sequences: {len(result['content']['sequences'])}")
```

## Output Format

```json
{
  "content": {
    "steps": [
      {
        "step_number": 1,
        "action": "Podnosilac podnosi zahtev nadležnom organu",
        "actor": "Podnosilac",
        "deadline": "u roku od 30 dana",
        "context": "1) Podnosilac podnosi zahtev nadležnom organu u roku od 30 dana.",
        "line_number": 3
      },
      {
        "step_number": 2,
        "action": "Organ vrši proveru dokumentacije",
        "actor": "Organ",
        "deadline": "u roku od 15 dana",
        "context": "2) Organ vrši proveru dokumentacije u roku od 15 dana.",
        "line_number": 4
      }
    ],
    "sequences": [
      {
        "sequence_type": "ordered",
        "steps": [...],
        "description": "Ordered procedural sequence"
      }
    ],
    "actors": [
      {
        "name": "Podnosilac",
        "role": null,
        "responsibilities": ["podnosi zahtev"],
        "context": "Podnosilac podnosi zahtev...",
        "line_number": 3
      },
      {
        "name": "Organ",
        "role": null,
        "responsibilities": ["vrši proveru", "donosi rešenje"],
        "context": "Organ vrši proveru...",
        "line_number": 4
      }
    ],
    "dependencies": [
      {
        "step_from": "unknown",
        "step_to": "unknown",
        "dependency_type": "follows",
        "context": "Nakon provere, organ donosi rešenje"
      }
    ]
  },
  "processing_time": 0.005,
  "total_elements": 8
}
```

## Pattern Detection

### Steps

**Numbered Steps:**
- "1) Action..."
- "korak 1: Action..."
- "faza 1: Action..."

**Action Verbs:**
- podnosi/podnese (submits)
- dostavlja/dostavi (delivers)
- izdaje/izda (issues)
- donosi/donese (makes decision)
- obaveštava/obavesti (notifies)
- sastavlja/sastavi (compiles)
- vrši/izvrši (performs)
- sprovodi/sprovede (implements)

### Actors

- poslodavac (employer)
- zaposleni (employee)
- radnik (worker)
- ministar (minister)
- direktor (director)
- inspektor (inspector)
- organ (authority)
- komisija (commission)
- sud (court)

### Sequences

**Sequence Indicators:**
- prvo (first)
- drugo (second)
- treće (third)
- zatim (then)
- nakon toga (after that)
- potom (afterwards)
- na kraju (finally)

### Dependencies

**Dependency Types:**
- "pre nego što" (before) → prerequisite
- "nakon što" (after) → follows
- "po izvršenju" (upon completion) → follows
- "po prijemu" (upon receipt) → follows

### Deadlines

- "u roku od X dana/meseci/godina"
- "najkasnije X dana/meseci/godina"
- "u X dana/meseci/godina"

## Conflict Detection Support

This module supports conflict detection by:

1. **Procedural Conflicts**: Different procedures for same action
2. **Deadline Conflicts**: Inconsistent time constraints
3. **Actor Conflicts**: Wrong actor assigned to action
4. **Sequence Violations**: Steps performed out of order
5. **Dependency Violations**: Prerequisites not met

## Performance

- Processing time: ~5ms per document
- Memory usage: Minimal (compiled regex patterns cached)
- Scalability: Can process thousands of documents efficiently

## Dependencies

- Python 3.8+
- pydantic
- No external NLP libraries required (pure regex)

## Integration

This module integrates with:
- **Normative Extractor**: Links procedures to obligations
- **Temporal Linker**: Associates deadlines with steps
- **Quantitative Extractor**: Links numeric constraints to procedures
- **Conflict Detector**: Identifies procedural conflicts