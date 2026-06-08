"""
Test M6 with large batch to debug 500 error
"""

import requests
import json

# Create test data with 311 units
units = []
for i in range(311):
    units.append({
        "unit_id": f"unit_{i}",
        "content": f"Zaposleni je dužan da obavlja poslove u skladu sa ugovorom. Ovo je jedinica broj {i}.",
        "unit_type": "article",
        "number": str(i+1)
    })

print(f"Testing M6 with {len(units)} units...")

try:
    response = requests.post(
        "http://localhost:8106/api/extract/batch",
        json={"legal_units": units, "min_confidence": 0.5},
        timeout=300
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Results: {len(data.get('results', []))} units processed")
        print(f"Metadata: {json.dumps(data.get('metadata', {}), indent=2)}")
    else:
        print(f"Error response:")
        print(response.text[:500])
        
except Exception as e:
    print(f"Exception: {e}")

# Made with Bob
