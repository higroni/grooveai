"""
Full pipeline test: M1 → M2 → M3 → M4 → M6 → M7 → M8 → M9 → M10
Tests complete document processing with knowledge enrichment
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
from pathlib import Path

# Module endpoints
MODULES = {
    "M1": "http://localhost:8101",  # File Reader
    "M2": "http://localhost:8102",  # Text Normalizer
    "M3": "http://localhost:8103",  # Latinizer
    "M4": "http://localhost:8105",  # Legal Parser
    "M6": "http://localhost:8106",  # Assertion Extractor
    "M7": "http://localhost:8107",  # Entity Recognizer
    "M8": "http://localhost:8108",  # Condition Extractor
    "M9": "http://localhost:8109",  # Assertion Classifier
    "M10": "http://localhost:8110", # Knowledge Enrichment
}

def check_all_modules():
    """Check if all modules are running"""
    print("\n" + "="*80)
    print("CHECKING MODULE HEALTH")
    print("="*80)
    
    all_healthy = True
    for name, url in MODULES.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} is running on {url}")
            else:
                print(f"❌ {name} returned status {response.status_code}")
                all_healthy = False
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} is not running on {url}")
            all_healthy = False
        except Exception as e:
            print(f"❌ {name} error: {e}")
            all_healthy = False
    
    return all_healthy


def test_full_pipeline():
    """Test complete pipeline from file to enriched assertions"""
    print("\n" + "="*80)
    print("FULL PIPELINE TEST: M1 → M2 → M3 → M4 → M6 → M7 → M8 → M9 → M10")
    print("="*80)
    
    # Test text (Serbian legal text)
    test_text = """
    Član 105. Zakon o radu
    
    Poslodavac je dužan da zaposlenom isplati zaradu za obavljeni rad i vreme provedeno na radu.
    
    Zaposleni ima pravo na godišnji odmor u trajanju od najmanje 20 radnih dana.
    
    Ugovor o radu zaključuje se u pisanoj formi.
    """
    
    print(f"\n📄 Test Text:")
    print(f"{test_text[:200]}...")
    
    pipeline_start = time.time()
    
    try:
        # Skip M1 for now, use text directly
        print(f"\n🔄 M1: File Reader (skipped - using direct text)...")
        print(f"   ✅ Using test text: {len(test_text)} chars")
        
        # M2: Text Normalizer
        print(f"\n🔄 M2: Text Normalizer...")
        m2_data = {"text": test_text}
        m2_response = requests.post(f"{MODULES['M2']}/normalize", json=m2_data, timeout=30)
        m2_result = m2_response.json()
        normalized_text = m2_result["normalized_text"]
        print(f"   ✅ Normalized: {len(normalized_text)} chars")
        
        # M3: Latinizer
        print(f"\n🔄 M3: Latinizer...")
        m3_data = {"text": normalized_text}
        m3_response = requests.post(f"{MODULES['M3']}/latinize", json=m3_data, timeout=30)
        m3_result = m3_response.json()
        latin_text = m3_result["latinized_text"]
        print(f"   ✅ Latinized: {len(latin_text)} chars")
        
        # M4: Legal Parser
        print(f"\n🔄 M4: Legal Parser...")
        m4_data = {"text": latin_text}
        m4_response = requests.post(f"{MODULES['M4']}/parse", json=m4_data, timeout=30)
        m4_result = m4_response.json()
        legal_units = m4_result.get("legal_units", [])
        print(f"   ✅ Parsed: {len(legal_units)} legal units")
        
        # M6: Assertion Extractor
        print(f"\n🔄 M6: Assertion Extractor...")
        m6_data = {"legal_units": legal_units}
        m6_response = requests.post(f"{MODULES['M6']}/extract", json=m6_data, timeout=30)
        m6_result = m6_response.json()
        assertions = m6_result.get("assertions", [])
        print(f"   ✅ Extracted: {len(assertions)} assertions")
        
        # M7: Entity Recognizer
        print(f"\n🔄 M7: Entity Recognizer...")
        m7_data = {"assertions": assertions}
        m7_response = requests.post(f"{MODULES['M7']}/recognize", json=m7_data, timeout=60)
        m7_result = m7_response.json()
        assertions_with_entities = m7_result.get("assertions", [])
        total_entities = sum(len(a.get("entities", [])) for a in assertions_with_entities)
        print(f"   ✅ Recognized: {total_entities} entities in {len(assertions_with_entities)} assertions")
        
        # M8: Condition Extractor
        print(f"\n🔄 M8: Condition Extractor...")
        m8_data = {"assertions": assertions_with_entities}
        m8_response = requests.post(f"{MODULES['M8']}/extract", json=m8_data, timeout=30)
        m8_result = m8_response.json()
        assertions_with_conditions = m8_result.get("assertions", [])
        total_conditions = sum(len(a.get("conditions", [])) for a in assertions_with_conditions)
        print(f"   ✅ Extracted: {total_conditions} conditions")
        
        # M9: Assertion Classifier
        print(f"\n🔄 M9: Assertion Classifier...")
        m9_data = {"assertions": assertions_with_conditions}
        m9_response = requests.post(f"{MODULES['M9']}/classify", json=m9_data, timeout=30)
        m9_result = m9_response.json()
        classified_assertions = m9_result.get("assertions", [])
        print(f"   ✅ Classified: {len(classified_assertions)} assertions")
        
        # M10: Knowledge Enrichment
        print(f"\n🔄 M10: Knowledge Enrichment...")
        enriched_assertions = []
        for assertion in classified_assertions:
            m10_data = {
                "assertion_id": assertion.get("id", 0),
                "assertion_text": assertion.get("text", ""),
                "entities": assertion.get("entities", []),
                "use_classla": True
            }
            m10_response = requests.post(f"{MODULES['M10']}/enrich", json=m10_data, timeout=30)
            m10_result = m10_response.json()
            
            if m10_result.get("success"):
                enriched = m10_result.get("enriched_assertion", {})
                enriched_assertions.append(enriched)
        
        print(f"   ✅ Enriched: {len(enriched_assertions)} assertions")
        
        # Display results
        pipeline_time = (time.time() - pipeline_start) * 1000
        
        print(f"\n" + "="*80)
        print("PIPELINE RESULTS")
        print("="*80)
        print(f"⏱️  Total pipeline time: {pipeline_time:.2f}ms")
        print(f"📊 Processing stages:")
        print(f"   M1: File Reader → {len(m1_result.get('content', ''))} chars")
        print(f"   M2: Text Normalizer → {len(normalized_text)} chars")
        print(f"   M3: Latinizer → {len(latin_text)} chars")
        print(f"   M4: Legal Parser → {len(legal_units)} units")
        print(f"   M6: Assertion Extractor → {len(assertions)} assertions")
        print(f"   M7: Entity Recognizer → {total_entities} entities")
        print(f"   M8: Condition Extractor → {total_conditions} conditions")
        print(f"   M9: Assertion Classifier → {len(classified_assertions)} classified")
        print(f"   M10: Knowledge Enrichment → {len(enriched_assertions)} enriched")
        
        # Display sample enriched assertion
        if enriched_assertions:
            print(f"\n📝 Sample Enriched Assertion:")
            sample = enriched_assertions[0]
            print(f"   Text: {sample.get('assertion_text', '')[:100]}...")
            print(f"   Matched Terms: {len(sample.get('matched_terms', []))}")
            print(f"   Legal References: {len(sample.get('legal_references', []))}")
            print(f"   Definitions: {len(sample.get('term_definitions', []))}")
            
            # Show matched terms
            if sample.get('matched_terms'):
                print(f"\n   🏷️  Matched Terms:")
                for term in sample.get('matched_terms', [])[:3]:
                    term_name = term.get('term', 'N/A')
                    category = term.get('category', 'N/A')
                    score = term.get('score', 0.0)
                    print(f"      - {term_name} ({category}) - Score: {score:.2f}")
            
            # Show references
            if sample.get('legal_references'):
                print(f"\n   ⚖️  Legal References:")
                for ref in sample.get('legal_references', [])[:3]:
                    law = ref.get('law_name', 'N/A')
                    article = ref.get('article_number', 'N/A')
                    print(f"      - {law}, Član {article}")
            
            # Show definitions
            if sample.get('term_definitions'):
                print(f"\n   📖 Definitions:")
                for defn in sample.get('term_definitions', [])[:2]:
                    term = defn.get('term', 'N/A')
                    definition = defn.get('definition', 'N/A')[:80]
                    print(f"      - {term}: {definition}...")
        
        print(f"\n✅ Full pipeline test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("GROOVE.AI FULL PIPELINE TEST WITH MODULE 10")
    print("="*80)
    
    # Check all modules
    if not check_all_modules():
        print("\n⚠️  Not all modules are running!")
        print("   Start them with: .\\restart_all_modules.bat")
        exit(1)
    
    # Run pipeline test
    success = test_full_pipeline()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed!")

# Made with Bob
