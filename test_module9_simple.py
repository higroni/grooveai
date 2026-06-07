"""
Simple test for Module 9: Assertion Classifier
Tests classification of assertions into types.
"""

import sys
import requests
import json
from typing import Dict, Any

# Set console encoding to UTF-8 for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_health_check() -> bool:
    """Test if the module is running."""
    print_section("Testing Health Check")
    
    try:
        response = requests.get("http://localhost:8109/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Module is healthy")
            print(f"  Status: {data.get('status')}")
            print(f"  Total classifications: {data.get('total_classifications', 0)}")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Could not connect to module: {e}")
        print("\nMake sure Module 9 is running on port 8109:")
        print("  python -m modules.assertion_classifier.main")
        return False


def test_classify_obligation():
    """Test classification of obligation assertion."""
    print_section("Test 1: Obligation Classification")
    
    request_data = {
        "assertion": {
            "assertion_id": "test_obligation_001",
            "text": "Poslodavac mora da obezbedi bezbedne uslove rada",
            "confidence": 0.9
        },
        "language": "sr",
        "min_confidence": 0.5
    }
    
    print(f"Input: {request_data['assertion']['text']}")
    
    response = requests.post(
        "http://localhost:8109/classify",
        json=request_data,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        classification = result['output']['classification']
        
        print(f"\n✓ Classification successful")
        print(f"  Type: {classification['assertion_type']}")
        print(f"  Confidence: {classification['confidence']}")
        print(f"  Matched patterns: {', '.join(classification['matched_patterns'])}")
        print(f"  Reasoning: {classification['reasoning']}")
        print(f"  Processing time: {result['metadata']['processing_time_ms']}ms")
        
        # Verify it's classified as obligation
        if classification['assertion_type'] == 'obligation':
            print(f"\n✓ Correctly classified as OBLIGATION")
        else:
            print(f"\n✗ Expected 'obligation', got '{classification['assertion_type']}'")
    else:
        print(f"✗ Request failed with status {response.status_code}")
        print(f"  Response: {response.text}")


def test_classify_prohibition():
    """Test classification of prohibition assertion."""
    print_section("Test 2: Prohibition Classification")
    
    request_data = {
        "assertion": {
            "assertion_id": "test_prohibition_001",
            "text": "Zaposleni ne sme da koristi službene resurse u privatne svrhe",
            "confidence": 0.85
        },
        "language": "sr",
        "min_confidence": 0.5
    }
    
    print(f"Input: {request_data['assertion']['text']}")
    
    response = requests.post(
        "http://localhost:8109/classify",
        json=request_data,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        classification = result['output']['classification']
        
        print(f"\n✓ Classification successful")
        print(f"  Type: {classification['assertion_type']}")
        print(f"  Confidence: {classification['confidence']}")
        print(f"  Matched patterns: {', '.join(classification['matched_patterns'])}")
        
        if classification['assertion_type'] == 'prohibition':
            print(f"\n✓ Correctly classified as PROHIBITION")
        else:
            print(f"\n✗ Expected 'prohibition', got '{classification['assertion_type']}'")
    else:
        print(f"✗ Request failed with status {response.status_code}")


def test_classify_permission():
    """Test classification of permission assertion."""
    print_section("Test 3: Permission Classification")
    
    request_data = {
        "assertion": {
            "assertion_id": "test_permission_001",
            "text": "Radnik može da zatraži godišnji odmor u skladu sa zakonom",
            "confidence": 0.88
        },
        "language": "sr",
        "min_confidence": 0.5
    }
    
    print(f"Input: {request_data['assertion']['text']}")
    
    response = requests.post(
        "http://localhost:8109/classify",
        json=request_data,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        classification = result['output']['classification']
        
        print(f"\n✓ Classification successful")
        print(f"  Type: {classification['assertion_type']}")
        print(f"  Confidence: {classification['confidence']}")
        print(f"  Matched patterns: {', '.join(classification['matched_patterns'])}")
        
        if classification['assertion_type'] == 'permission':
            print(f"\n✓ Correctly classified as PERMISSION")
        else:
            print(f"\n✗ Expected 'permission', got '{classification['assertion_type']}'")
    else:
        print(f"✗ Request failed with status {response.status_code}")


def test_classify_deadline():
    """Test classification of deadline assertion."""
    print_section("Test 4: Deadline Classification")
    
    request_data = {
        "assertion": {
            "assertion_id": "test_deadline_001",
            "text": "Zahtev se podnosi u roku od 30 dana od dana prijema obaveštenja",
            "confidence": 0.92
        },
        "language": "sr",
        "min_confidence": 0.5
    }
    
    print(f"Input: {request_data['assertion']['text']}")
    
    response = requests.post(
        "http://localhost:8109/classify",
        json=request_data,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        classification = result['output']['classification']
        
        print(f"\n✓ Classification successful")
        print(f"  Type: {classification['assertion_type']}")
        print(f"  Confidence: {classification['confidence']}")
        print(f"  Matched patterns: {', '.join(classification['matched_patterns'])}")
        
        if classification['assertion_type'] == 'deadline':
            print(f"\n✓ Correctly classified as DEADLINE")
        else:
            print(f"\n✗ Expected 'deadline', got '{classification['assertion_type']}'")
    else:
        print(f"✗ Request failed with status {response.status_code}")


def test_classify_definition():
    """Test classification of definition assertion."""
    print_section("Test 5: Definition Classification")
    
    request_data = {
        "assertion": {
            "assertion_id": "test_definition_001",
            "text": "Radni odnos jeste odnos između poslodavca i zaposlenog zasnovan na ugovoru o radu",
            "confidence": 0.87
        },
        "language": "sr",
        "min_confidence": 0.5
    }
    
    print(f"Input: {request_data['assertion']['text']}")
    
    response = requests.post(
        "http://localhost:8109/classify",
        json=request_data,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        classification = result['output']['classification']
        
        print(f"\n✓ Classification successful")
        print(f"  Type: {classification['assertion_type']}")
        print(f"  Confidence: {classification['confidence']}")
        print(f"  Matched patterns: {', '.join(classification['matched_patterns'])}")
        
        if classification['assertion_type'] == 'definition':
            print(f"\n✓ Correctly classified as DEFINITION")
        else:
            print(f"\n✗ Expected 'definition', got '{classification['assertion_type']}'")
    else:
        print(f"✗ Request failed with status {response.status_code}")


def test_get_patterns():
    """Test getting available patterns."""
    print_section("Test 6: Get Available Patterns")
    
    response = requests.get("http://localhost:8109/patterns?language=sr", timeout=5)
    
    if response.status_code == 200:
        patterns = response.json()
        
        print(f"✓ Retrieved patterns for all types:")
        for assertion_type, info in patterns.items():
            print(f"\n  {assertion_type.upper()}:")
            print(f"    Count: {info['count']}")
            print(f"    Avg confidence: {info['avg_confidence']}")
            print(f"    Patterns: {', '.join(info['patterns'][:5])}...")
    else:
        print(f"✗ Request failed with status {response.status_code}")


def test_get_stats():
    """Test getting classification statistics."""
    print_section("Test 7: Get Statistics")
    
    response = requests.get("http://localhost:8109/stats?days=7", timeout=5)
    
    if response.status_code == 200:
        stats = response.json()
        
        print(f"✓ Retrieved statistics:")
        print(f"  Total classifications: {stats['total_classifications']}")
        print(f"\n  Type distribution:")
        for type_name, count in stats['type_distribution'].items():
            print(f"    {type_name}: {count}")
    else:
        print(f"✗ Request failed with status {response.status_code}")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  MODULE 9: ASSERTION CLASSIFIER - SIMPLE TEST")
    print("=" * 80)
    
    # Check if module is running
    if not test_health_check():
        return
    
    # Run classification tests
    test_classify_obligation()
    test_classify_prohibition()
    test_classify_permission()
    test_classify_deadline()
    test_classify_definition()
    
    # Test utility endpoints
    test_get_patterns()
    test_get_stats()
    
    print_section("Test Summary")
    print("All tests completed!")
    print("\nNext steps:")
    print("1. Check database: data/databases/assertion_classifier.db")
    print("2. View API docs: http://localhost:8109/docs")
    print("3. Run full pipeline integration test")


if __name__ == "__main__":
    main()

# Made with Bob
