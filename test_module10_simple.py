"""
Simple test for Module 10: Embedding Generator
Tests the new hybrid embedding strategy with metadata support.
"""

import sys
import io
import requests
import json

# Fix Windows console encoding for Serbian characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Module 10 URL
MODULE_10_URL = "http://localhost:8110"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{MODULE_10_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_single_embedding_with_metadata():
    """Test single embedding generation with metadata."""
    print("\n" + "="*60)
    print("TEST 2: Single Embedding with Metadata")
    print("="*60)
    
    request_data = {
        "text": "Poslodavac je dužan da zaposlenom isplaćuje platu.",
        "metadata": {
            "source": "zakon_o_radu.pdf",
            "article": "Član 104"
        },
        "embedding_type": "document"
    }
    
    print(f"\nRequest: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{MODULE_10_URL}/api/generate",
            json=request_data,
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Job ID: {result['job_id']}")
            print(f"Model: {result['output']['model_name']}")
            print(f"Embedding Dimension: {result['output']['embedding_dimension']}")
            print(f"Processing Time: {result['output']['processing_time_ms']}ms")
            print(f"Metadata: {json.dumps(result['output'].get('metadata'), indent=2, ensure_ascii=False)}")
            print(f"First 5 embedding values: {result['output']['embeddings'][:5]}")
            return True
        else:
            print(f"ERROR: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_assertion_embeddings():
    """Test assertion embedding generation (primary use case)."""
    print("\n" + "="*60)
    print("TEST 3: Assertion Embeddings (Primary Use Case)")
    print("="*60)
    
    assertions = [
        {
            "assertion_id": "assert_001",
            "text": "Poslodavac je dužan da zaposlenom isplaćuje platu.",
            "assertion_type": "obligation",
            "confidence": 0.95,
            "entities": [
                {"type": "LEGAL_REF", "text": "Član 104", "start": 0, "end": 8}
            ],
            "conditions": [
                {"type": "condition", "text": "ako je zaposlen", "start": 10, "end": 25}
            ],
            "article_number": "Član 104",
            "source_document": "zakon_o_radu.pdf"
        },
        {
            "assertion_id": "assert_002",
            "text": "Zaposleni ima pravo na godišnji odmor.",
            "assertion_type": "permission",
            "confidence": 0.90,
            "entities": [],
            "conditions": [],
            "article_number": "Član 68",
            "source_document": "zakon_o_radu.pdf"
        }
    ]
    
    request_data = {"assertions": assertions}
    
    print(f"\nRequest: {len(assertions)} assertions")
    for i, assertion in enumerate(assertions, 1):
        print(f"  {i}. {assertion['text'][:50]}... ({assertion['assertion_type']})")
    
    try:
        response = requests.post(
            f"{MODULE_10_URL}/api/generate/assertions",
            json=request_data,
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Job ID: {result['job_id']}")
            print(f"Model: {result['output']['model_name']}")
            print(f"Embedding Dimension: {result['output']['embedding_dimension']}")
            print(f"Assertion Count: {result['output']['assertion_count']}")
            print(f"Total Processing Time: {result['output']['total_processing_time_ms']}ms")
            print(f"Avg Time per Assertion: {result['output']['avg_time_per_text_ms']}ms")
            
            print("\nMetadata for each assertion:")
            for i, metadata in enumerate(result['output']['metadata_list'], 1):
                print(f"  {i}. Type: {metadata['assertion_type']}, "
                      f"Confidence: {metadata['confidence']}, "
                      f"Entities: {metadata['entity_count']}, "
                      f"Conditions: {metadata['condition_count']}")
            
            return True
        else:
            print(f"ERROR: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_batch_embeddings_with_metadata():
    """Test batch embedding generation with metadata list."""
    print("\n" + "="*60)
    print("TEST 4: Batch Embeddings with Metadata List")
    print("="*60)
    
    request_data = {
        "texts": [
            "Član 1: Opšte odredbe",
            "Član 2: Definicije pojmova",
            "Član 3: Primena zakona"
        ],
        "batch_size": 32,
        "metadata_list": [
            {"article": "Član 1", "section": "Opšte odredbe"},
            {"article": "Član 2", "section": "Definicije"},
            {"article": "Član 3", "section": "Primena"}
        ],
        "embedding_type": "document"
    }
    
    print(f"\nRequest: {len(request_data['texts'])} texts with metadata")
    
    try:
        response = requests.post(
            f"{MODULE_10_URL}/api/generate/batch",
            json=request_data,
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Job ID: {result['job_id']}")
            print(f"Model: {result['output']['model_name']}")
            print(f"Text Count: {result['output']['text_count']}")
            print(f"Total Processing Time: {result['output']['total_processing_time_ms']}ms")
            print(f"Avg Time per Text: {result['output']['avg_time_per_text_ms']}ms")
            print(f"Metadata List Length: {len(result['output'].get('metadata_list', []))}")
            return True
        else:
            print(f"ERROR: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MODULE 10: EMBEDDING GENERATOR - SIMPLE TEST")
    print("="*60)
    print("\nTesting hybrid embedding strategy with metadata support...")
    
    results = {
        "Health Check": test_health(),
        "Single Embedding with Metadata": test_single_embedding_with_metadata(),
        "Assertion Embeddings": test_assertion_embeddings(),
        "Batch Embeddings with Metadata": test_batch_embeddings_with_metadata()
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()

# Made with Bob