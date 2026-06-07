"""
Test script for Module 10 (Knowledge Enrichment) with CLASSLA NER integration
"""
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import json
import time

# Module 10 endpoint
M10_URL = "http://localhost:8110"

def test_enrichment_with_classla():
    """Test enrichment with CLASSLA NER enabled"""
    print("\n" + "="*80)
    print("Testing Module 10 Knowledge Enrichment with CLASSLA NER")
    print("="*80)
    
    # Test assertion with entities from M7
    test_data = {
        "assertion_id": 1,
        "assertion_text": "Poslodavac je dužan da zaposlenom isplati zaradu u skladu sa članom 105. Zakona o radu.",
        "entities": [
            {
                "text": "Poslodavac",
                "type": "PERSON",
                "start": 0,
                "end": 10
            },
            {
                "text": "Zakon o radu",
                "type": "LAW",
                "start": 82,
                "end": 94
            }
        ],
        "use_classla": True  # Enable CLASSLA NER in M10
    }
    
    print(f"\n📝 Test Assertion:")
    print(f"   Text: {test_data['assertion_text']}")
    print(f"   Entities from M7: {len(test_data['entities'])}")
    print(f"   CLASSLA enabled: {test_data['use_classla']}")
    
    try:
        # Send enrichment request
        print(f"\n🔄 Sending enrichment request to {M10_URL}/enrich...")
        start_time = time.time()
        
        response = requests.post(
            f"{M10_URL}/enrich",
            json=test_data,
            timeout=30
        )
        
        elapsed = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Enrichment successful!")
            print(f"   Processing time: {elapsed:.2f}ms")
            
            if result.get("success"):
                enriched = result.get("enriched_assertion", {})
                
                # Display matched terms
                matched_terms = enriched.get("matched_terms", [])
                print(f"\n📚 Matched Ontology Terms: {len(matched_terms)}")
                for i, term in enumerate(matched_terms, 1):
                    term_name = term.get('term', 'N/A')
                    category = term.get('category', 'N/A')
                    score = term.get('score', 0.0)
                    source = term.get('source', 'N/A')
                    print(f"   {i}. {term_name} ({category})")
                    print(f"      Score: {score:.2f}, Source: {source}")
                
                # Display legal references
                references = enriched.get("legal_references", [])
                print(f"\n⚖️  Legal References: {len(references)}")
                for i, ref in enumerate(references, 1):
                    print(f"   {i}. {ref.get('law_name')} - Član {ref.get('article_number')}")
                    print(f"      Confidence: {ref.get('confidence'):.2f}")
                
                # Display definitions
                definitions = enriched.get("term_definitions", [])
                print(f"\n📖 Term Definitions: {len(definitions)}")
                for i, defn in enumerate(definitions, 1):
                    print(f"   {i}. {defn.get('term')}")
                    print(f"      Definition: {defn.get('definition')[:80]}...")
                    print(f"      Pattern: {defn.get('definition_pattern')}")
                
                print(f"\n⏱️  Total processing time: {enriched.get('processing_time_ms', 0):.2f}ms")
                
                return True
            else:
                print(f"\n❌ Enrichment failed: {result.get('error')}")
                return False
        else:
            print(f"\n❌ HTTP Error {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Module 10 is not running on {M10_URL}")
        print("   Start it with: python -m modules.knowledge_enrichment.main")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_enrichment_without_classla():
    """Test enrichment with CLASSLA NER disabled (M7 entities only)"""
    print("\n" + "="*80)
    print("Testing Module 10 without CLASSLA NER (M7 entities only)")
    print("="*80)
    
    test_data = {
        "assertion_id": 2,
        "assertion_text": "Zaposleni ima pravo na godišnji odmor u trajanju od najmanje 20 radnih dana.",
        "entities": [
            {
                "text": "Zaposleni",
                "type": "PERSON",
                "start": 0,
                "end": 9
            }
        ],
        "use_classla": False  # Disable CLASSLA NER in M10
    }
    
    print(f"\n📝 Test Assertion:")
    print(f"   Text: {test_data['assertion_text']}")
    print(f"   Entities from M7: {len(test_data['entities'])}")
    print(f"   CLASSLA enabled: {test_data['use_classla']}")
    
    try:
        response = requests.post(
            f"{M10_URL}/enrich",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                enriched = result.get("enriched_assertion", {})
                matched_terms = enriched.get("matched_terms", [])
                
                print(f"\n✅ Enrichment successful (without CLASSLA)!")
                print(f"   Matched terms: {len(matched_terms)}")
                print(f"   Processing time: {enriched.get('processing_time_ms', 0):.2f}ms")
                
                return True
            else:
                print(f"\n❌ Enrichment failed: {result.get('error')}")
                return False
        else:
            print(f"\n❌ HTTP Error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def check_module_health():
    """Check if Module 10 is running"""
    print("\n" + "="*80)
    print("Checking Module 10 Health")
    print("="*80)
    
    try:
        response = requests.get(f"{M10_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"\n✅ Module 10 is running")
            print(f"   Status: {health.get('status')}")
            print(f"   Service: {health.get('service')}")
            return True
        else:
            print(f"\n❌ Module 10 returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Module 10 is not running on {M10_URL}")
        print("   Start it with: python -m modules.knowledge_enrichment.main")
        return False
    except Exception as e:
        print(f"\n❌ Error checking health: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("MODULE 10 KNOWLEDGE ENRICHMENT TEST WITH CLASSLA")
    print("="*80)
    
    # Check if module is running
    if not check_module_health():
        print("\n⚠️  Please start Module 10 first!")
        exit(1)
    
    # Run tests
    test1_passed = test_enrichment_with_classla()
    test2_passed = test_enrichment_without_classla()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Test 1 (with CLASSLA): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (without CLASSLA): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed!")

# Made with Bob
