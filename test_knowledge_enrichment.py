"""
Test script for Knowledge Enrichment Module (M10)
Tests ontology matching, reference resolution, and definition extraction
"""

import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8110"


def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_ontology_match():
    """Test ontology matching"""
    print("\n=== Testing Ontology Matching ===")
    
    request_data = {
        "text": "Pravno lice je organizacija koja ima pravnu sposobnost.",
        "entities": [
            {"text": "pravno lice", "type": "LEGAL_TERM"},
            {"text": "organizacija", "type": "ORG"}
        ],
        "auto_learn": True
    }
    
    response = requests.post(
        f"{BASE_URL}/ontology/match",
        json=request_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_reference_resolution():
    """Test reference resolution"""
    print("\n=== Testing Reference Resolution ===")
    
    request_data = {
        "text": "U skladu sa članom 5. Zakona o privrednim društvima i stavom 2. člana 10, pravno lice..."
    }
    
    response = requests.post(
        f"{BASE_URL}/references/resolve",
        json=request_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_definition_extraction():
    """Test definition extraction"""
    print("\n=== Testing Definition Extraction ===")
    
    request_data = {
        "text": "Pravno lice znači organizaciju koja ima pravnu sposobnost. Pod privrednim društvom se podrazumeva pravno lice koje obavlja privrednu delatnost."
    }
    
    response = requests.post(
        f"{BASE_URL}/definitions/extract",
        json=request_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_full_enrichment():
    """Test full enrichment"""
    print("\n=== Testing Full Enrichment ===")
    
    request_data = {
        "assertion_id": 1,
        "assertion_text": "U skladu sa članom 5. Zakona o privrednim društvima, pravno lice znači organizaciju koja ima pravnu sposobnost i poslovnu sposobnost.",
        "entities": [
            {"text": "pravno lice", "type": "LEGAL_TERM"},
            {"text": "organizacija", "type": "ORG"},
            {"text": "Zakon o privrednim društvima", "type": "LAW"}
        ],
        "metadata": {
            "document_id": "test_doc_1",
            "source": "test"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/enrich",
        json=request_data
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get("success"):
        enriched = result.get("enriched_assertion", {})
        print(f"\n✅ Enrichment successful!")
        print(f"   - Matched terms: {len(enriched.get('matched_terms', []))}")
        print(f"   - Legal references: {len(enriched.get('legal_references', []))}")
        print(f"   - Definitions: {len(enriched.get('term_definitions', []))}")
        print(f"   - Processing time: {result.get('processing_time_ms', 0):.2f}ms")
    
    return response.status_code == 200


def test_batch_enrichment():
    """Test batch enrichment"""
    print("\n=== Testing Batch Enrichment ===")
    
    request_data = {
        "assertions": [
            {
                "assertion_id": 2,
                "assertion_text": "Pravno lice je organizacija.",
                "entities": [{"text": "pravno lice", "type": "LEGAL_TERM"}]
            },
            {
                "assertion_id": 3,
                "assertion_text": "Član 10. Zakona propisuje obaveze.",
                "entities": [{"text": "Zakon", "type": "LAW"}]
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/enrich/batch",
        json=request_data
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get("success"):
        print(f"\n✅ Batch enrichment successful!")
        print(f"   - Total processed: {len(request_data['assertions'])}")
        print(f"   - Successful: {result.get('successful_count', 0)}")
        print(f"   - Failed: {result.get('failed_count', 0)}")
        print(f"   - Total time: {result.get('total_processing_time_ms', 0):.2f}ms")
    
    return response.status_code == 200


def test_stats():
    """Test statistics endpoint"""
    print("\n=== Testing Statistics Endpoint ===")
    
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def main():
    """Run all tests"""
    print("=" * 70)
    print("KNOWLEDGE ENRICHMENT MODULE (M10) - TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Health Check", test_health),
        ("Ontology Matching", test_ontology_match),
        ("Reference Resolution", test_reference_resolution),
        ("Definition Extraction", test_definition_extraction),
        ("Full Enrichment", test_full_enrichment),
        ("Batch Enrichment", test_batch_enrichment),
        ("Statistics", test_stats)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()

# Made with Bob
