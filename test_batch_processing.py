"""
Integration test for batch processing endpoints across all modules.
Tests M6, M7, M8, M9, and M10 batch endpoints.
"""

import requests
import time
from typing import Dict, Any


# Module endpoints (actual ports from config.yaml)
ENDPOINTS = {
    "M6": "http://localhost:8106/api/extract/batch",
    "M7": "http://localhost:8107/api/recognize/batch",
    "M8": "http://localhost:8108/api/extract/batch",
    "M9": "http://localhost:8109/classify/batch",
    "M10": "http://localhost:8110/enrich/batch"
}


def test_m6_batch_assertion_extraction():
    """Test M6: Batch assertion extraction"""
    print("\n=== Testing M6: Assertion Extractor (Batch) ===")
    
    payload = {
        "legal_units": [
            {
                "unit_id": "test_unit_1",
                "text": "Poslodavac mora obezbediti bezbedne uslove rada.",
                "unit_type": "article"
            },
            {
                "unit_id": "test_unit_2",
                "text": "Zaposleni ima pravo na godišnji odmor.",
                "unit_type": "paragraph"
            }
        ]
    }
    
    try:
        response = requests.post(ENDPOINTS["M6"], json=payload, timeout=30)
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        print(f"Total units: {result.get('total_units')}")
        print(f"Successful: {result.get('successful')}")
        print(f"Failed: {result.get('failed')}")
        
        if 'metadata' in result and 'timing' in result['metadata']:
            timing = result['metadata']['timing']
            print(f"Total time: {timing.get('total_ms')}ms")
            print(f"Throughput: {timing.get('throughput_units_per_sec')} units/sec")
        
        return result.get('status') == 'success'
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_m7_batch_entity_recognition():
    """Test M7: Batch entity recognition with NER"""
    print("\n=== Testing M7: Entity Recognizer (Batch) ===")
    
    payload = {
        "assertions": [
            {
                "assertion_id": "test_a1",
                "text": "Ministarstvo pravde donosi odluku."
            },
            {
                "assertion_id": "test_a2",
                "text": "Vlada Republike Srbije odobrava zakon."
            }
        ],
        "use_ner": True,
        "language": "sr"
    }
    
    try:
        response = requests.post(ENDPOINTS["M7"], json=payload, timeout=60)
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        print(f"Total assertions: {result.get('total_assertions')}")
        print(f"Successful: {result.get('successful')}")
        print(f"Failed: {result.get('failed')}")
        
        if 'metadata' in result and 'timing' in result['metadata']:
            timing = result['metadata']['timing']
            print(f"Total time: {timing.get('total_ms')}ms")
            print(f"NER init time: {timing.get('ner_init_ms')}ms")
            print(f"NER overhead: {timing.get('ner_overhead_percent')}%")
        
        return result.get('status') in ['success', 'partial']
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_m8_batch_condition_extraction():
    """Test M8: Batch condition extraction"""
    print("\n=== Testing M8: Condition Extractor (Batch) ===")
    
    payload = {
        "assertions": [
            {
                "assertion_id": "test_a1",
                "text": "Ako zaposleni ima više od 5 godina staža, ima pravo na bonus."
            },
            {
                "assertion_id": "test_a2",
                "text": "U slučaju bolesti, zaposleni mora dostaviti lekarsko uverenje."
            }
        ],
        "language": "sr"
    }
    
    try:
        response = requests.post(ENDPOINTS["M8"], json=payload, timeout=30)
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        print(f"Total assertions: {result.get('total_assertions')}")
        print(f"Successful: {result.get('successful')}")
        print(f"Failed: {result.get('failed')}")
        
        if 'metadata' in result and 'timing' in result['metadata']:
            timing = result['metadata']['timing']
            print(f"Total time: {timing.get('total_ms')}ms")
            print(f"Throughput: {timing.get('throughput_assertions_per_sec')} assertions/sec")
        
        return result.get('status') in ['success', 'partial']
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_m9_batch_classification():
    """Test M9: Batch assertion classification"""
    print("\n=== Testing M9: Assertion Classifier (Batch) ===")
    
    payload = {
        "assertions": [
            {
                "assertion_id": "test_a1",
                "text": "Poslodavac mora obezbediti bezbedne uslove rada.",
                "confidence": 0.9
            },
            {
                "assertion_id": "test_a2",
                "text": "Zaposleni ne sme koristiti službena sredstva u privatne svrhe.",
                "confidence": 0.85
            }
        ],
        "language": "sr",
        "min_confidence": 0.5
    }
    
    try:
        response = requests.post(ENDPOINTS["M9"], json=payload, timeout=30)
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        print(f"Total assertions: {result.get('total_assertions')}")
        print(f"Successful: {result.get('successful')}")
        print(f"Failed: {result.get('failed')}")
        
        if 'metadata' in result and 'timing' in result['metadata']:
            timing = result['metadata']['timing']
            print(f"Total time: {timing.get('total_ms')}ms")
            print(f"Throughput: {timing.get('throughput_assertions_per_sec')} assertions/sec")
        
        if 'metadata' in result and 'classification_stats' in result['metadata']:
            type_dist = result['metadata']['classification_stats'].get('type_distribution', {})
            print(f"Type distribution: {type_dist}")
        
        return result.get('status') in ['success', 'partial']
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_m10_batch_enrichment():
    """Test M10: Batch knowledge enrichment"""
    print("\n=== Testing M10: Knowledge Enrichment (Batch) ===")
    
    payload = {
        "assertions": [
            {
                "assertion_id": 1,
                "assertion_text": "Ministarstvo pravde donosi odluku.",
                "entities": [],
                "use_classla": False
            },
            {
                "assertion_id": 2,
                "assertion_text": "Prema članu 5. Zakona o radu, zaposleni ima pravo na odmor.",
                "entities": [],
                "use_classla": False
            }
        ]
    }
    
    try:
        response = requests.post(ENDPOINTS["M10"], json=payload, timeout=60)
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        print(f"Total assertions: {result.get('total_assertions')}")
        print(f"Successful: {result.get('successful')}")
        print(f"Failed: {result.get('failed')}")
        
        if 'metadata' in result and 'timing' in result['metadata']:
            timing = result['metadata']['timing']
            print(f"Total time: {timing.get('total_ms')}ms")
            print(f"Throughput: {timing.get('throughput_assertions_per_sec')} assertions/sec")
        
        return result.get('status') in ['success', 'partial']
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    """Run all batch processing tests"""
    print("=" * 60)
    print("BATCH PROCESSING INTEGRATION TESTS")
    print("=" * 60)
    
    results = {}
    
    # Test each module
    results['M6'] = test_m6_batch_assertion_extraction()
    time.sleep(1)
    
    results['M7'] = test_m7_batch_entity_recognition()
    time.sleep(1)
    
    results['M8'] = test_m8_batch_condition_extraction()
    time.sleep(1)
    
    results['M9'] = test_m9_batch_classification()
    time.sleep(1)
    
    results['M10'] = test_m10_batch_enrichment()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for module, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{module}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All batch processing tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())

# Made with Bob
