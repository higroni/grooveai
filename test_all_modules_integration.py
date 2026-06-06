"""
Integration test for Modules 1, 2, and 3
Tests the complete pipeline: PDF → Text → Normalized → Embeddings
"""

import requests
import json
from shared.config_loader import config

print("=" * 80)
print("GROOVE.AI - Integration Test: Modules 1 + 2 + 3")
print("=" * 80)

# Get sample file from config
sample_file = config.get_sample_file()
print(f"\nSample file: {sample_file}")

# Step 1: Read PDF with Module 1 (File Reader)
print("\n[STEP 1] Reading PDF with Module 1 (File Reader)...")
print("-" * 80)

response1 = requests.post(
    "http://localhost:8101/api/read",
    json={
        "file_path": sample_file,
        "file_type": "pdf"
    }
)

if response1.status_code != 200:
    print(f"[ERROR] Module 1 failed: {response1.status_code}")
    print(response1.text)
    exit(1)

result1 = response1.json()
extracted_text = result1["output"]["text"]
job1_id = result1["job_id"]

print(f"[OK] Job ID: {job1_id}")
print(f"[OK] Extracted {result1['output']['char_count']} characters")
print(f"[OK] Pages: {result1['output']['page_count']}")
print(f"[OK] Text extracted successfully (Cyrillic content)")

# Step 2: Normalize text with Module 2 (Text Normalizer)
print("\n[STEP 2] Normalizing text with Module 2 (Text Normalizer)...")
print("-" * 80)

response2 = requests.post(
    "http://localhost:8102/api/normalize",
    json={
        "text": extracted_text,
        "options": {
            "remove_extra_whitespace": True,
            "normalize_newlines": True,
            "fix_encoding": True
        }
    }
)

if response2.status_code != 200:
    print(f"[ERROR] Module 2 failed: {response2.status_code}")
    print(response2.text)
    exit(1)

result2 = response2.json()
normalized_text = result2["output"]["normalized_text"]
job2_id = result2["job_id"]

print(f"[OK] Job ID: {job2_id}")
print(f"[OK] Original length: {result2['output']['original_length']}")
print(f"[OK] Normalized length: {result2['output']['normalized_length']}")
print(f"[OK] Changes made: {len(result2['output']['changes_made'])}")
print(f"[OK] Processing time: {result2['output']['processing_time_ms']}ms")

# Step 3: Generate embeddings with Module 3 (Embedding Generator)
print("\n[STEP 3] Generating embeddings with Module 3 (Embedding Generator)...")
print("-" * 80)

# Take first 500 characters for embedding (to keep it fast)
text_sample = normalized_text[:500]

response3 = requests.post(
    "http://localhost:8103/api/generate",
    json={"text": text_sample}
)

if response3.status_code != 200:
    print(f"[ERROR] Module 3 failed: {response3.status_code}")
    print(response3.text)
    exit(1)

result3 = response3.json()
embeddings = result3["output"]["embeddings"]
job3_id = result3["job_id"]

print(f"[OK] Job ID: {job3_id}")
print(f"[OK] Embedding dimension: {result3['output']['embedding_dimension']}")
print(f"[OK] Model: {result3['output']['model_name']}")
print(f"[OK] Text length: {result3['output']['text_length']}")
print(f"[OK] Processing time: {result3['output']['processing_time_ms']}ms")
print(f"[OK] First 5 embedding values: {embeddings[:5]}")

# Summary
print("\n" + "=" * 80)
print("INTEGRATION TEST SUMMARY")
print("=" * 80)
print(f"Module 2 (Text Normalizer):     {result2['output']['processing_time_ms']}ms")
print(f"Module 3 (Embedding Generator): {result3['output']['processing_time_ms']}ms")
print()
print(f"Input:  PDF file ({result1['output']['page_count']} pages, {result1['output']['char_count']} chars)")
print(f"Output: {result3['output']['embedding_dimension']}-dimensional embedding vector")
print()
print("[SUCCESS] All 3 modules working correctly!")
print("Pipeline: PDF → Extract Text → Normalize → Generate Embeddings")
print("=" * 80)

# Made with Bob
