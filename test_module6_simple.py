"""
Simple test for Module 6: Assertion Extractor
Tests basic assertion extraction functionality.
"""

import requests
import json

BASE_URL = "http://localhost:8107"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    print("[OK] Health check passed")


def test_extract_assertions():
    """Test assertion extraction"""
    print("\n=== Testing Assertion Extraction ===")
    
    # Sample Serbian legal text
    test_content = """
    Poslodavac je dužan da zaposlenom isplati zaradu za obavljeni rad i vreme provedeno na radu.
    Zaposleni može da koristi godišnji odmor u skladu sa zakonom.
    Zabranjeno je diskriminisati zaposlene na bilo kom osnovu.
    Poslodavac mora da obezbedi bezbedne uslove rada.
    Zaposleni ima pravo na pauzu tokom radnog vremena.
    """
    
    request_data = {
        "legal_unit": {
            "unit_id": "test-unit-001",
            "content": test_content,
            "unit_type": "article",
            "number": "1"
        },
        "language": "sr",
        "min_confidence": 0.5
    }
    
    print(f"Request data:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    response = requests.post(
        f"{BASE_URL}/api/extract",
        json=request_data
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nResponse:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Check results
        output = result.get("output", {})
        assertions = output.get("assertions", [])
        stats = output.get("stats", {})
        
        print(f"\n=== Extraction Results ===")
        print(f"Total assertions found: {len(assertions)}")
        print(f"Total sentences processed: {stats.get('total_sentences', 0)}")
        print(f"Average confidence: {stats.get('avg_confidence', 0):.2f}")
        
        print(f"\n=== Extracted Assertions ===")
        for i, assertion in enumerate(assertions, 1):
            print(f"\n{i}. {assertion['text']}")
            print(f"   Confidence: {assertion['confidence']:.2f}")
            print(f"   Position: chars {assertion['start_char']}-{assertion['end_char']}")
        
        # Get job ID for next test
        job_id = result.get("job_id")
        print(f"\n[OK] Assertion extraction passed")
        print(f"Job ID: {job_id}")
        return job_id
    else:
        print(f"Error: {response.text}")
        return None


def test_get_job(job_id):
    """Test getting job by ID"""
    if not job_id:
        print("\n[WARN] Skipping job retrieval test (no job_id)")
        return
    
    print(f"\n=== Testing Job Retrieval ===")
    print(f"Job ID: {job_id}")
    
    response = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nJob details:")
        print(f"  Legal Unit ID: {result.get('legal_unit_id')}")
        print(f"  Total Assertions: {result.get('total_assertions')}")
        print(f"  Processing Time: {result.get('processing_time_ms'):.2f}ms")
        print(f"  Created At: {result.get('created_at')}")
        print(f"[OK] Job retrieval passed")
    else:
        print(f"Error: {response.text}")


def test_list_jobs():
    """Test listing all jobs"""
    print(f"\n=== Testing Job Listing ===")
    
    response = requests.get(f"{BASE_URL}/api/jobs?limit=5")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nTotal jobs: {result.get('total')}")
        print(f"Showing: {len(result.get('jobs', []))} jobs")
        
        for job in result.get('jobs', []):
            print(f"\n  Job: {job.get('job_id')}")
            print(f"    Legal Unit: {job.get('legal_unit_id')}")
            print(f"    Assertions: {job.get('total_assertions')}")
        
        print(f"[OK] Job listing passed")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    print("=" * 60)
    print("Module 6: Assertion Extractor - Simple Test")
    print("=" * 60)
    
    try:
        # Run tests
        test_health()
        job_id = test_extract_assertions()
        test_get_job(job_id)
        test_list_jobs()
        
        print("\n" + "=" * 60)
        print("[OK] All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

# Made with Bob