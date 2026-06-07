"""
Test GPU Acceleration for M7 and M10
Tests both Entity Recognizer and Knowledge Enrichment with GPU-enabled CLASSLA
"""

import requests
import json
import time
import sys
import io
from typing import Dict, Any

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test configuration
M7_URL = "http://localhost:8107"
M10_URL = "http://localhost:8110"

# Sample legal text for testing
SAMPLE_TEXT = """
Član 1.
Poslodavac je dužan da zaposlenom isplati zaradu za obavljeni rad i vreme provedeno na radu.

Član 2.
Zaposleni ima pravo na godišnji odmor u trajanju od najmanje 20 radnih dana.

Član 3.
Radni odnos se zasniva na osnovu ugovora o radu koji zaključuju poslodavac i zaposleni.
"""

def test_m7_entity_recognition():
    """Test M7 Entity Recognizer with GPU acceleration"""
    print("\n" + "="*70)
    print("Testing M7 Entity Recognizer (GPU-enabled CLASSLA)")
    print("="*70)
    
    # Prepare request with correct format
    payload = {
        "assertion": {
            "assertion_id": "test_gpu_m7",
            "text": SAMPLE_TEXT,
            "confidence": 0.85
        },
        "language": "sr",
        "min_confidence": 0.5
    }
    
    # Measure time
    start_time = time.time()
    
    # Send request
    response = requests.post(f"{M7_URL}/api/recognize", json=payload)
    
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
    
    if response.status_code == 200:
        result = response.json()
        entities = result.get('entities', [])
        
        print(f"\n[OK] M7 Entity Recognition completed")
        print(f"Time: {elapsed_time:.2f}ms")
        print(f"Entities found: {len(entities)}")
        print(f"Average confidence: {result.get('stats', {}).get('avg_confidence', 0):.2f}")
        
        # Show sample entities
        if entities:
            print("\nSample entities:")
            for entity in entities[:3]:
                print(f"  - {entity['text']} ({entity['entity_type']}) - confidence: {entity.get('confidence', 'N/A'):.2f}")
        
        return True, elapsed_time, len(entities)
    else:
        print(f"\n[ERROR] M7 request failed: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text[:200])
        return False, 0, 0


def test_m10_knowledge_enrichment():
    """Test M10 Knowledge Enrichment with GPU acceleration"""
    print("\n" + "="*70)
    print("Testing M10 Knowledge Enrichment (GPU-enabled CLASSLA)")
    print("="*70)
    
    # First, we need entities from M7
    m7_payload = {
        "assertion": {
            "assertion_id": "test_gpu_m10",
            "text": SAMPLE_TEXT,
            "confidence": 0.85
        },
        "language": "sr",
        "min_confidence": 0.5
    }
    
    m7_response = requests.post(f"{M7_URL}/api/recognize", json=m7_payload)
    
    if m7_response.status_code != 200:
        print(f"[ERROR] Failed to get entities from M7")
        return False, 0, 0
    
    entities = m7_response.json().get('entities', [])
    
    # Prepare M10 request
    payload = {
        "assertion_id": "test_gpu_assertion",
        "text": SAMPLE_TEXT,
        "entities": entities,
        "use_classla": True  # Enable CLASSLA in M10
    }
    
    # Measure time
    start_time = time.time()
    
    # Send request
    response = requests.post(f"{M10_URL}/enrich", json=payload)
    
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
    
    if response.status_code == 200:
        result = response.json()
        enriched_entities = result.get('enriched_entities', [])
        
        print(f"\n[OK] M10 Knowledge Enrichment completed")
        print(f"Time: {elapsed_time:.2f}ms")
        print(f"Enriched entities: {len(enriched_entities)}")
        
        # Show sample enriched entities
        if enriched_entities:
            print("\nSample enriched entities:")
            for entity in enriched_entities[:3]:
                print(f"  - {entity['text']} ({entity['type']})")
                if entity.get('ontology_matches'):
                    print(f"    Ontology matches: {len(entity['ontology_matches'])}")
        
        return True, elapsed_time, len(enriched_entities)
    else:
        print(f"\n[ERROR] M10 request failed: {response.status_code}")
        print(response.text)
        return False, 0, 0


def check_gpu_status():
    """Check if GPU is available and being used"""
    print("\n" + "="*70)
    print("GPU Status Check")
    print("="*70)
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"\n[OK] GPU Available: {gpu_name}")
            print(f"     Memory: {gpu_memory:.2f} GB")
            print(f"     CUDA Version: {torch.version.cuda}")
            return True
        else:
            print("\n[WARN] No GPU detected - Running on CPU")
            return False
    except ImportError:
        print("\n[WARN] PyTorch not available - Cannot detect GPU")
        return False


def main():
    """Run all GPU acceleration tests"""
    print("\n" + "="*70)
    print("GPU ACCELERATION TEST - M7 & M10")
    print("="*70)
    
    # Check GPU status
    gpu_available = check_gpu_status()
    
    # Test M7
    m7_success, m7_time, m7_entities = test_m7_entity_recognition()
    
    # Test M10
    m10_success, m10_time, m10_entities = test_m10_knowledge_enrichment()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"\nGPU Available: {'Yes' if gpu_available else 'No'}")
    print(f"\nM7 Entity Recognizer:")
    print(f"  Status: {'PASS' if m7_success else 'FAIL'}")
    print(f"  Time: {m7_time:.2f}ms")
    print(f"  Entities: {m7_entities}")
    
    print(f"\nM10 Knowledge Enrichment:")
    print(f"  Status: {'PASS' if m10_success else 'FAIL'}")
    print(f"  Time: {m10_time:.2f}ms")
    print(f"  Enriched Entities: {m10_entities}")
    
    print(f"\nTotal Processing Time: {m7_time + m10_time:.2f}ms")
    
    if m7_success and m10_success:
        print("\n[SUCCESS] All GPU acceleration tests passed!")
        return 0
    else:
        print("\n[FAILURE] Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())

# Made with Bob
