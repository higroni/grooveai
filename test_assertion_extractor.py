"""
Quick test for Module 6: Assertion Extractor
"""

import requests
import json

# Module URL
BASE_URL = "http://localhost:8106"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_extract_assertions():
    """Test assertion extraction."""
    print("Testing assertion extraction...")
    
    # Test with sample legal text
    request_data = {
        "legal_unit": {
            "unit_id": "article-1",
            "content": "Poslodavac je dužan da zaposlenom isplati zaradu. Zaposleni ima pravo na odmor. Zabranjeno je diskriminisati zaposlene.",
            "unit_type": "article",
            "number": "1"
        },
        "language": "sr",
        "min_confidence": 0.5
    }
    
    response = requests.post(f"{BASE_URL}/api/extract", json=request_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Extraction successful")
        print(f"Job ID: {result['job_id']}")
        print(f"Total assertions: {result['output']['stats']['total_assertions']}")
        print(f"Total sentences: {result['output']['stats']['total_sentences']}")
        print(f"Avg confidence: {result['output']['stats']['avg_confidence']}")
        print(f"Processing time: {result['metadata']['processing_time_ms']:.2f}ms")
        print()
        
        print("Extracted assertions:")
        for i, assertion in enumerate(result['output']['assertions'], 1):
            print(f"  {i}. {assertion['text']}")
            print(f"     Confidence: {assertion['confidence']:.2f}")
            print()
        
        # Save full response
        with open('assertion_test_response.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("[OK] Full response saved to assertion_test_response.json")
        
        return result['job_id']
    else:
        print(f"[ERROR] Extraction failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_get_job(job_id):
    """Test getting job details."""
    if not job_id:
        print("[SKIP] No job ID to test")
        return
    
    print(f"\nTesting get job endpoint...")
    response = requests.get(f"{BASE_URL}/api/job/{job_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Job retrieved")
        print(f"Legal unit ID: {result['legal_unit_id']}")
        print(f"Total assertions: {result['total_assertions']}")
        print(f"Processing time: {result['processing_time_ms']:.2f}ms")
    else:
        print(f"[ERROR] Failed to get job: {response.status_code}")

def test_high_confidence():
    """Test getting high-confidence assertions."""
    print("\nTesting high-confidence assertions endpoint...")
    response = requests.get(f"{BASE_URL}/api/assertions/high-confidence?min_confidence=0.7&limit=10")
    
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Retrieved {result['total']} high-confidence assertions")
        
        if result['assertions']:
            print("\nTop assertions:")
            for i, assertion in enumerate(result['assertions'][:3], 1):
                print(f"  {i}. {assertion['text'][:60]}...")
                print(f"     Confidence: {assertion['confidence']:.2f}")
    else:
        print(f"[ERROR] Failed to get assertions: {response.status_code}")

if __name__ == "__main__":
    print("=" * 80)
    print("MODULE 6: ASSERTION EXTRACTOR - QUICK TEST")
    print("=" * 80)
    print()
    
    try:
        # Test health
        test_health()
        
        # Test extraction
        job_id = test_extract_assertions()
        
        # Test get job
        test_get_job(job_id)
        
        # Test high confidence
        test_high_confidence()
        
        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to module. Is it running on port 8106?")
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
