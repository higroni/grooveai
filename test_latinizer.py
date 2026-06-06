"""Test script for Latinizer module."""

import requests
import json

BASE_URL = "http://localhost:8103"

def test_health():
    """Test health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200

def test_latinize():
    """Test latinization endpoint."""
    print("\n=== Testing Latinization ===")
    
    test_cases = [
        {
            "name": "Cyrillic text",
            "text": "Закон о раду регулише права и обавезе запослених."
        },
        {
            "name": "Mixed Cyrillic/Latin",
            "text": "Члан 1: General provisions"
        },
        {
            "name": "Already Latin",
            "text": "Zakon o radu"
        }
    ]
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Input length: {len(test['text'])} chars")
        
        response = requests.post(
            f"{BASE_URL}/api/latinize",
            json={"text": test["text"]}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"Job ID: {data['job_id']}")
            print(f"Output length: {data['output_length']}")
            print(f"Cyrillic chars converted: {data['cyrillic_chars_converted']}")
            print(f"Processing time: {data['processing_time_ms']}ms")
            print(f"Latinized text: {data['latinized_text']}")
        else:
            print(f"Error: {response.text}")
    
    return True

def test_get_jobs():
    """Test get jobs endpoint."""
    print("\n=== Testing Get Jobs ===")
    response = requests.get(f"{BASE_URL}/api/jobs?limit=5")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        jobs = response.json()
        print(f"Found {len(jobs)} jobs")
        for job in jobs:
            print(f"  Job {job['job_id']}: {job['cyrillic_chars_converted']} chars converted")
    
    return response.status_code == 200

def test_stats():
    """Test stats endpoint."""
    print("\n=== Testing Stats ===")
    response = requests.get(f"{BASE_URL}/api/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

if __name__ == "__main__":
    print("Testing Latinizer Module API")
    print("=" * 50)
    
    try:
        test_health()
        test_latinize()
        test_get_jobs()
        test_stats()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
