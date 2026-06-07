"""
Simple test for Module 7: Entity Recognizer

Tests entity recognition with sample Serbian legal text.
"""

import requests
import json

# Module URL
ENTITY_RECOGNIZER_URL = "http://localhost:8107"

def test_entity_recognizer():
    """Test entity recognition with sample assertion."""
    
    print("\n" + "="*80)
    print("MODULE 7: ENTITY RECOGNIZER - SIMPLE TEST")
    print("="*80)
    
    # Test 1: Health check
    print("\n[TEST 1] Health Check")
    print("-" * 80)
    try:
        response = requests.get(f"{ENTITY_RECOGNIZER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Module is healthy")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"[ERROR] Health check failed: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Cannot connect to module: {e}")
        print("Make sure the module is running: python -m modules.entity_recognizer.main")
        return
    
    # Test 2: Recognize entities in sample assertion
    print("\n[TEST 2] Entity Recognition")
    print("-" * 80)
    
    sample_assertion = {
        "assertion_id": "test-assert-001",
        "text": "Poslodavac je dužan da u roku od 30 dana isplati 50000 RSD zaposlenom prema članu 23 stav 2 Zakona o radu (Sl. glasnik RS, br. 24/2005).",
        "confidence": 0.85
    }
    
    print(f"Assertion text: {sample_assertion['text']}")
    print(f"\nSending recognition request...")
    
    try:
        response = requests.post(
            f"{ENTITY_RECOGNIZER_URL}/api/recognize",
            json={
                "assertion": sample_assertion,
                "language": "sr",
                "min_confidence": 0.5
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Recognition successful")
            print(f"\nJob ID: {result['job_id']}")
            print(f"Total entities found: {result['stats']['total_entities']}")
            print(f"Average confidence: {result['stats']['avg_confidence']}")
            print(f"\nEntities by type:")
            for entity_type, count in result['stats']['entities_by_type'].items():
                print(f"  - {entity_type}: {count}")
            
            print(f"\nDetailed entities:")
            for i, entity in enumerate(result['entities'], 1):
                print(f"\n  Entity {i}:")
                print(f"    Type: {entity['entity_type']}")
                print(f"    Text: '{entity['text']}'")
                print(f"    Position: {entity['start_char']}-{entity['end_char']}")
                print(f"    Confidence: {entity['confidence']:.2f}")
            
            # Test 3: Retrieve job by ID
            print("\n[TEST 3] Retrieve Job by ID")
            print("-" * 80)
            job_id = result['job_id']
            
            response2 = requests.get(f"{ENTITY_RECOGNIZER_URL}/api/jobs/{job_id}", timeout=5)
            if response2.status_code == 200:
                job_data = response2.json()
                print(f"[OK] Job retrieved successfully")
                print(f"Job ID: {job_data['job_id']}")
                print(f"Assertion ID: {job_data['assertion_id']}")
                print(f"Total entities: {job_data['total_entities']}")
            else:
                print(f"[ERROR] Failed to retrieve job: {response2.status_code}")
            
            # Test 4: Get entities by assertion ID
            print("\n[TEST 4] Get Entities by Assertion ID")
            print("-" * 80)
            assertion_id = sample_assertion['assertion_id']
            
            response3 = requests.get(
                f"{ENTITY_RECOGNIZER_URL}/api/assertions/{assertion_id}/entities",
                timeout=5
            )
            if response3.status_code == 200:
                entities_data = response3.json()
                print(f"[OK] Entities retrieved by assertion ID")
                print(f"Assertion ID: {entities_data['assertion_id']}")
                print(f"Total entities: {entities_data['total_entities']}")
            else:
                print(f"[ERROR] Failed to retrieve entities: {response3.status_code}")
            
        else:
            print(f"[ERROR] Recognition failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
    
    # Test 5: Test with specific entity types
    print("\n[TEST 5] Recognition with Specific Entity Types")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{ENTITY_RECOGNIZER_URL}/api/recognize",
            json={
                "assertion": {
                    "assertion_id": "test-assert-002",
                    "text": "Ministarstvo finansija donosi odluku u Beogradu dana 15. januar 2024. godine sa 25% povećanjem."
                },
                "language": "sr",
                "min_confidence": 0.5,
                "entity_types": ["ORGANIZATION", "LOCATION", "DATE", "PERCENTAGE"]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Recognition with filters successful")
            print(f"Total entities found: {result['stats']['total_entities']}")
            print(f"\nEntities:")
            for entity in result['entities']:
                print(f"  - {entity['entity_type']}: '{entity['text']}' (confidence: {entity['confidence']:.2f})")
        else:
            print(f"[ERROR] Recognition failed: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
    
    # Test 6: List all jobs
    print("\n[TEST 6] List All Jobs")
    print("-" * 80)
    
    try:
        response = requests.get(f"{ENTITY_RECOGNIZER_URL}/api/jobs?limit=10", timeout=5)
        if response.status_code == 200:
            jobs_data = response.json()
            print(f"[OK] Jobs listed successfully")
            print(f"Total jobs: {jobs_data['total']}")
            print(f"Showing: {len(jobs_data['jobs'])} jobs")
            for job in jobs_data['jobs'][:3]:
                print(f"  - Job {job['job_id'][:8]}...: {job['total_entities']} entities, confidence: {job['avg_confidence']:.2f}")
        else:
            print(f"[ERROR] Failed to list jobs: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_entity_recognizer()

# Made with Bob
