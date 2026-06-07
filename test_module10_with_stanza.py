"""
Test Module 10 (Knowledge Enrichment) with Stanza NER integration
"""
import requests
import json

# Test data - Serbian legal text
test_assertion = {
    "assertion_id": 1,
    "assertion_text": "Pravno lice je organizacija koja ima svojstvo pravnog subjekta. Ministarstvo pravde donosi odluku o registraciji. Prema članu 5. Zakona o privrednim društvima, društvo se osniva ugovorom.",
    "entities": [
        {"text": "pravno lice", "type": "LEGAL_TERM", "confidence": 0.9},
        {"text": "pravnog subjekta", "type": "LEGAL_TERM", "confidence": 0.85}
    ],
    "use_stanza": True  # Enable Stanza NER
}

print("=" * 80)
print("Testing Module 10 (Knowledge Enrichment) with Stanza NER")
print("=" * 80)

# Test enrichment endpoint
print("\n1. Testing /enrich endpoint with Stanza enabled...")
try:
    response = requests.post(
        "http://localhost:8110/enrich",
        json=test_assertion,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n[SUCCESS] Status: {response.status_code}")
        print(f"Success: {result.get('success')}")
        
        if result.get('enriched_assertion'):
            enriched = result['enriched_assertion']
            print(f"\nMatched Terms: {len(enriched.get('matched_terms', []))}")
            for term in enriched.get('matched_terms', [])[:5]:
                print(f"  - {term.get('entity_text')}: {term.get('canonical_form')} ({term.get('source')})")
            
            print(f"\nLegal References: {len(enriched.get('legal_references', []))}")
            for ref in enriched.get('legal_references', [])[:3]:
                print(f"  - {ref.get('raw_reference')}")
            
            print(f"\nDefinitions: {len(enriched.get('term_definitions', []))}")
            for defn in enriched.get('term_definitions', [])[:3]:
                print(f"  - {defn.get('term')}: {defn.get('definition')[:50]}...")
            
            print(f"\nProcessing Time: {enriched.get('processing_time_ms', 0):.2f}ms")
    else:
        print(f"\n[ERROR] Status: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n[ERROR] Cannot connect to Module 10 on port 8110")
    print("Make sure the module is running: python -m modules.knowledge_enrichment.main")
except Exception as e:
    print(f"\n[ERROR] {e}")

# Test without Stanza
print("\n\n2. Testing /enrich endpoint WITHOUT Stanza...")
test_assertion_no_stanza = test_assertion.copy()
test_assertion_no_stanza["use_stanza"] = False

try:
    response = requests.post(
        "http://localhost:8110/enrich",
        json=test_assertion_no_stanza,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n[SUCCESS] Status: {response.status_code}")
        if result.get('enriched_assertion'):
            enriched = result['enriched_assertion']
            print(f"Matched Terms (M7 only): {len(enriched.get('matched_terms', []))}")
            print(f"Processing Time: {enriched.get('processing_time_ms', 0):.2f}ms")
    else:
        print(f"\n[ERROR] Status: {response.status_code}")
        
except Exception as e:
    print(f"\n[ERROR] {e}")

# Test health endpoint
print("\n\n3. Testing /health endpoint...")
try:
    response = requests.get("http://localhost:8110/health", timeout=5)
    if response.status_code == 200:
        print(f"[SUCCESS] {response.json()}")
    else:
        print(f"[ERROR] Status: {response.status_code}")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "=" * 80)
print("Test Complete")
print("=" * 80)

# Made with Bob
