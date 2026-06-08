"""
Debug what test script sends to M6
"""

import requests
import json
from pathlib import Path

# Simulate what test script does
pdf_path = Path("D:/POSAO/OllamaProjects/GROOVE.AI/DOCUMENTS/DEV/onedoc/radni_odnosi_0001_000001.pdf")

print("Step 1: M1 - File Reader")
response = requests.post(
    "http://localhost:8101/api/read",
    json={"file_path": str(pdf_path.absolute())},
    timeout=300
)
m1_data = response.json()
text = m1_data["output"]["text"]
print(f"  Text length: {len(text)} chars")

print("\nStep 2: M2 - Normalizer")
response = requests.post(
    "http://localhost:8102/api/normalize",
    json={"text": text},
    timeout=300
)
m2_data = response.json()
normalized_text = m2_data["output"]["normalized_text"]
print(f"  Normalized length: {len(normalized_text)} chars")

print("\nStep 3: M3 - Latinizer")
response = requests.post(
    "http://localhost:8103/api/latinize",
    json={"text": normalized_text},
    timeout=300
)
m3_data = response.json()
latinized_text = m3_data["latinized_text"]
print(f"  Latinized length: {len(latinized_text)} chars")

print("\nStep 4: M4 - Parser")
response = requests.post(
    "http://localhost:8105/api/parse",
    json={
        "text": latinized_text,
        "source_uri": str(pdf_path),
        "filename": pdf_path.name
    },
    timeout=300
)
m4_data = response.json()
units = m4_data["output"]["legal_units"]
print(f"  Units: {len(units)}")

# Transform to M6 format
m6_units = []
for unit in units:
    m6_units.append({
        "unit_id": unit.get("legal_unit_id"),
        "content": unit.get("content_text"),
        "unit_type": unit.get("unit_type"),
        "number": unit.get("number")
    })

print(f"\nStep 5: M6 - Assertion Extractor")
print(f"  Sending {len(m6_units)} units to M6...")

# Check first unit
print(f"\n  First unit sample:")
print(f"    unit_id: {m6_units[0]['unit_id']}")
print(f"    content length: {len(m6_units[0]['content'])} chars")
print(f"    content preview: {m6_units[0]['content'][:100]}...")

# Save request to file for inspection
with open("m6_request_debug.json", "w", encoding="utf-8") as f:
    json.dump({"legal_units": m6_units[:3], "min_confidence": 0.5}, f, indent=2, ensure_ascii=False)
print(f"\n  Saved first 3 units to m6_request_debug.json")

try:
    response = requests.post(
        "http://localhost:8106/api/extract/batch",
        json={"legal_units": m6_units, "min_confidence": 0.5},
        timeout=300
    )
    
    print(f"\n  M6 Response:")
    print(f"    Status code: {response.status_code}")
    
    if response.status_code == 200:
        m6_data = response.json()
        print(f"    Success! {len(m6_data.get('results', []))} results")
        print(f"    Metadata: {json.dumps(m6_data.get('metadata', {}), indent=2)}")
    else:
        print(f"    Error: {response.text[:500]}")
        
except Exception as e:
    print(f"\n  Exception: {e}")

# Made with Bob
