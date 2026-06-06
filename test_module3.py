"""
Quick test for Module 3 (Embedding Generator)
"""

import requests
import json

# Test Module 3
print("Testing Module 3 (Embedding Generator)...")
print("=" * 60)

# Test 1: Generate single embedding
print("\n1. Testing single embedding generation...")
response = requests.post(
    "http://localhost:8103/api/generate",
    json={"text": "Zakon o radu regulise prava i obaveze zaposlenih."}
)

if response.status_code == 200:
    result = response.json()
    print(f"   [OK] Job ID: {result['job_id']}")
    print(f"   [OK] Embedding dimension: {result['output']['embedding_dimension']}")
    print(f"   [OK] Processing time: {result['output']['processing_time_ms']}ms")
    print(f"   [OK] First 5 values: {result['output']['embeddings'][:5]}")
else:
    print(f"   [ERROR] Status: {response.status_code}")
    print(f"   [ERROR] Response: {response.text}")

# Test 2: Get model info
print("\n2. Testing model info...")
response = requests.get("http://localhost:8103/model/info")

if response.status_code == 200:
    info = response.json()
    print(f"   [OK] Model: {info['model_name']}")
    print(f"   [OK] Dimension: {info['embedding_dimension']}")
    print(f"   [OK] Device: {info['device']}")
    print(f"   [OK] Batch size: {info['batch_size']}")
else:
    print(f"   [ERROR] Status: {response.status_code}")

# Test 3: Batch embeddings
print("\n3. Testing batch embedding generation...")
texts = [
    "Clan 1: Opste odredbe",
    "Clan 2: Definicije pojmova",
    "Clan 3: Primena zakona"
]

response = requests.post(
    "http://localhost:8103/api/generate/batch",
    json={"texts": texts, "batch_size": 32}
)

if response.status_code == 200:
    result = response.json()
    print(f"   [OK] Job ID: {result['job_id']}")
    print(f"   [OK] Text count: {result['output']['text_count']}")
    print(f"   [OK] Total time: {result['output']['total_processing_time_ms']}ms")
    print(f"   [OK] Avg time per text: {result['output']['avg_time_per_text_ms']}ms")
else:
    print(f"   [ERROR] Status: {response.status_code}")
    print(f"   [ERROR] Response: {response.text}")

print("\n" + "=" * 60)
print("Module 3 testing complete!")

# Made with Bob
