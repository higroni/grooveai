"""
Simple test for Module 8: Condition Extractor
Tests condition extraction from sample assertions.
"""
import requests
import json
import sys
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_condition_extractor():
    """Test condition extraction with sample assertions."""
    
    base_url = "http://localhost:8108"
    
    # Test 1: Health check
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # Test 2: Extract conditions from assertion with modal and conditional
    print("\n" + "="*80)
    print("TEST 2: Extract Modal and Conditional")
    print("="*80)
    
    assertion_text = "Zaposleni mora da obavesti poslodavca ako planira da koristi godišnji odmor."
    
    request_data = {
        "assertion": {
            "assertion_id": "test-assert-1",
            "text": assertion_text,
            "confidence": 0.85
        },
        "language": "sr",
        "min_confidence": 0.5,
        "extract_conditions": True,
        "extract_exceptions": True,
        "extract_temporal": True,
        "extract_modal": True
    }
    
    print(f"\nAssertion: {assertion_text}")
    print(f"\nRequest:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    response = requests.post(f"{base_url}/api/extract", json=request_data)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nJob ID: {result['job_id']}")
        print(f"Assertion ID: {result['assertion_id']}")
        print(f"\nExtraction Results:")
        print(f"  Total conditions: {result['output']['total_conditions']}")
        print(f"  Total exceptions: {result['output']['total_exceptions']}")
        print(f"  Total temporal: {result['output']['total_temporal']}")
        print(f"  Total modal: {result['output']['total_modal']}")
        print(f"  Average confidence: {result['output']['average_confidence']}")
        print(f"  Processing time: {result['output']['processing_time_ms']}ms")
        
        print(f"\nExtracted Conditions ({len(result['output']['conditions'])}):")
        for i, cond in enumerate(result['output']['conditions'], 1):
            print(f"\n  {i}. Type: {cond['condition_type']}")
            print(f"     Trigger: {cond['trigger_word']}")
            print(f"     Text: {cond['text']}")
            print(f"     Position: {cond['start_char']}-{cond['end_char']}")
            print(f"     Confidence: {cond['confidence']}")
            print(f"     Context: {cond['context'][:100]}...")
    else:
        print(f"Error: {response.text}")
    
    # Test 3: Extract temporal conditions
    print("\n" + "="*80)
    print("TEST 3: Extract Temporal Conditions")
    print("="*80)
    
    assertion_text = "Zaposleni mora da podnese zahtev u roku od 30 dana pre planiranog korišćenja odmora."
    
    request_data = {
        "assertion": {
            "assertion_id": "test-assert-2",
            "text": assertion_text,
            "confidence": 0.9
        },
        "language": "sr",
        "min_confidence": 0.5
    }
    
    print(f"\nAssertion: {assertion_text}")
    
    response = requests.post(f"{base_url}/api/extract", json=request_data)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nExtraction Results:")
        print(f"  Total conditions: {result['output']['total_conditions']}")
        print(f"  Total temporal: {result['output']['total_temporal']}")
        print(f"  Total modal: {result['output']['total_modal']}")
        
        print(f"\nExtracted Conditions ({len(result['output']['conditions'])}):")
        for i, cond in enumerate(result['output']['conditions'], 1):
            print(f"\n  {i}. Type: {cond['condition_type']}")
            print(f"     Trigger: {cond['trigger_word']}")
            print(f"     Text: {cond['text']}")
            print(f"     Confidence: {cond['confidence']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 4: Extract exceptions
    print("\n" + "="*80)
    print("TEST 4: Extract Exceptions")
    print("="*80)
    
    assertion_text = "Svi zaposleni imaju pravo na godišnji odmor, osim onih koji su u probnom radu."
    
    request_data = {
        "assertion": {
            "assertion_id": "test-assert-3",
            "text": assertion_text,
            "confidence": 0.88
        },
        "language": "sr",
        "min_confidence": 0.5
    }
    
    print(f"\nAssertion: {assertion_text}")
    
    response = requests.post(f"{base_url}/api/extract", json=request_data)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nExtraction Results:")
        print(f"  Total conditions: {result['output']['total_conditions']}")
        print(f"  Total exceptions: {result['output']['total_exceptions']}")
        print(f"  Total modal: {result['output']['total_modal']}")
        
        print(f"\nExtracted Conditions ({len(result['output']['conditions'])}):")
        for i, cond in enumerate(result['output']['conditions'], 1):
            print(f"\n  {i}. Type: {cond['condition_type']}")
            print(f"     Trigger: {cond['trigger_word']}")
            print(f"     Text: {cond['text']}")
            print(f"     Confidence: {cond['confidence']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 5: Complex assertion with multiple condition types
    print("\n" + "="*80)
    print("TEST 5: Complex Assertion with Multiple Conditions")
    print("="*80)
    
    assertion_text = "Poslodavac mora da isplati platu u roku od 5 dana nakon isteka meseca, osim ako zaposleni nije dostavio potrebnu dokumentaciju."
    
    request_data = {
        "assertion": {
            "assertion_id": "test-assert-4",
            "text": assertion_text,
            "confidence": 0.92
        },
        "language": "sr",
        "min_confidence": 0.5
    }
    
    print(f"\nAssertion: {assertion_text}")
    
    response = requests.post(f"{base_url}/api/extract", json=request_data)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nExtraction Results:")
        print(f"  Total conditions: {result['output']['total_conditions']}")
        print(f"  Total exceptions: {result['output']['total_exceptions']}")
        print(f"  Total temporal: {result['output']['total_temporal']}")
        print(f"  Total modal: {result['output']['total_modal']}")
        print(f"  Average confidence: {result['output']['average_confidence']}")
        
        print(f"\nExtracted Conditions ({len(result['output']['conditions'])}):")
        for i, cond in enumerate(result['output']['conditions'], 1):
            print(f"\n  {i}. Type: {cond['condition_type']}")
            print(f"     Trigger: {cond['trigger_word']}")
            print(f"     Text: {cond['text']}")
            print(f"     Confidence: {cond['confidence']}")
        
        # Test retrieving job by ID
        print("\n" + "="*80)
        print("TEST 6: Retrieve Job by ID")
        print("="*80)
        
        job_id = result['job_id']
        print(f"\nRetrieving job: {job_id}")
        
        response = requests.get(f"{base_url}/api/jobs/{job_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            job_result = response.json()
            print(f"\nJob retrieved successfully")
            print(f"  Assertion ID: {job_result['assertion_id']}")
            print(f"  Total conditions: {job_result['output']['total_conditions']}")
            print(f"  Created at: {job_result['created_at']}")
        else:
            print(f"Error: {response.text}")
    else:
        print(f"Error: {response.text}")
    
    # Test 7: Verify database storage
    print("\n" + "="*80)
    print("TEST 7: Verify Database Storage")
    print("="*80)
    
    # Get conditions by assertion ID
    print(f"\nRetrieving all conditions for assertion: test-assert-4")
    
    response = requests.get(f"{base_url}/api/assertions/test-assert-4/conditions")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nDatabase verification:")
        print(f"  Assertion ID: {result['assertion_id']}")
        print(f"  Total conditions in DB: {result['total_conditions']}")
        
        # Verify all condition types are stored
        condition_types = {}
        for cond in result['conditions']:
            cond_type = cond['condition_type']
            condition_types[cond_type] = condition_types.get(cond_type, 0) + 1
        
        print(f"\n  Conditions by type:")
        for cond_type, count in condition_types.items():
            print(f"    - {cond_type}: {count}")
        
        # Verify specific fields are stored correctly
        print(f"\n  Sample condition from DB:")
        if result['conditions']:
            sample = result['conditions'][0]
            print(f"    ID: {sample['condition_id']}")
            print(f"    Type: {sample['condition_type']}")
            print(f"    Trigger: {sample['trigger_word']}")
            print(f"    Text: {sample['text'][:50]}...")
            print(f"    Position: {sample['start_char']}-{sample['end_char']}")
            print(f"    Confidence: {sample['confidence']}")
            
            # Verify all required fields exist
            required_fields = ['condition_id', 'condition_type', 'text', 'start_char',
                             'end_char', 'confidence', 'trigger_word', 'context']
            missing_fields = [f for f in required_fields if f not in sample]
            
            if missing_fields:
                print(f"\n  ⚠️  WARNING: Missing fields in DB: {missing_fields}")
            else:
                print(f"\n  ✅ All required fields present in DB")
    else:
        print(f"Error: {response.text}")
    
    # Test 8: Verify multiple jobs for same assertion
    print("\n" + "="*80)
    print("TEST 8: Multiple Jobs for Same Assertion")
    print("="*80)
    
    # Create another job for test-assert-1
    request_data = {
        "assertion": {
            "assertion_id": "test-assert-1",
            "text": "Zaposleni mora da obavesti poslodavca ako planira da koristi godišnji odmor.",
            "confidence": 0.85
        },
        "language": "sr",
        "min_confidence": 0.6  # Different threshold
    }
    
    print(f"\nCreating second job for assertion: test-assert-1")
    response = requests.post(f"{base_url}/api/extract", json=request_data)
    
    if response.status_code == 200:
        result = response.json()
        job_id_2 = result['job_id']
        print(f"Second job created: {job_id_2}")
        
        # Now retrieve all conditions for this assertion
        response = requests.get(f"{base_url}/api/assertions/test-assert-1/conditions")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nTotal conditions from all jobs: {result['total_conditions']}")
            print(f"Expected: 4 (2 from each job)")
            
            if result['total_conditions'] == 4:
                print("✅ Database correctly stores multiple jobs per assertion")
            else:
                print(f"⚠️  Expected 4 conditions, got {result['total_conditions']}")
    
    print("\n" + "="*80)
    print("All tests completed!")
    print("="*80)


if __name__ == "__main__":
    test_condition_extractor()

# Made with Bob
