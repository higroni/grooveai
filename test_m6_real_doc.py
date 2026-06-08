import requests
import json

print("Testing M6 with real document data...")

# Load the saved request
with open('m6_request_debug.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {len(data['legal_units'])} units")

# Send to M6
response = requests.post(
    'http://localhost:8106/api/extract/batch',
    json=data,
    timeout=300
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Success! {len(result.get('results', []))} results")
else:
    print(f"Error: {response.text[:200]}")

# Made with Bob
