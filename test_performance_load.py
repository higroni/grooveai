"""
Performance Load Test for GROOVE.AI Pipeline - Version 2
Tests complete M1→M10 pipeline with verbose output
Measures throughput, latency, and system stability
"""

import os
import sys
import io
import time
import json
import requests
import statistics
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
TEST_DIR = Path("D:/POSAO/OllamaProjects/GROOVE.AI/DOCUMENTS/DEV/perftest")
RESULTS_DIR = Path("performance_results")
RESULTS_DIR.mkdir(exist_ok=True)

# Module URLs
MODULES = {
    "M1": "http://localhost:8101",
    "M2": "http://localhost:8102",
    "M3": "http://localhost:8103",
    "M4": "http://localhost:8105",
    "M6": "http://localhost:8106",
    "M7": "http://localhost:8107",
    "M8": "http://localhost:8108",
    "M9": "http://localhost:8109",
    "M10": "http://localhost:8110",
}

# Test configuration
TIMEOUT = 300  # 5 minutes per document


def check_module_health() -> bool:
    """Check if all modules are healthy"""
    print("\n" + "="*80)
    print("CHECKING MODULE HEALTH")
    print("="*80)
    
    all_healthy = True
    for name, url in MODULES.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"[OK] {name} is healthy")
            else:
                print(f"[ERROR] {name} returned status {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"[ERROR] {name} is not responding: {e}")
            all_healthy = False
    
    if all_healthy:
        print(f"\n[SUCCESS] All {len(MODULES)} modules are healthy!")
    else:
        print("\n[ERROR] Some modules are not healthy!")
    
    return all_healthy


def process_document(pdf_path: Path, doc_num: int, total_docs: int) -> Dict[str, Any]:
    """Process a single document through the complete pipeline"""
    
    print(f"\n{'='*80}")
    print(f"[{doc_num}/{total_docs}] Processing: {pdf_path.name}")
    print(f"{'='*80}")
    
    result = {
        "document": pdf_path.name,
        "success": False,
        "error": None,
        "module_times": {},
        "data": {}
    }
    
    doc_start = time.time()
    
    try:
        # M1: File Reader
        print(f"  [M1] File Reader...", end=" ", flush=True)
        m1_start = time.time()
        response = requests.post(
            f"{MODULES['M1']}/api/read",
            json={"file_path": str(pdf_path.absolute())},
            timeout=TIMEOUT
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"M1 failed with status {response.status_code}: {response.text[:200]}")
        
        m1_data = response.json()
        raw_text = m1_data["output"]["text"]
        m1_time = time.time() - m1_start
        result["module_times"]["M1_file_reader"] = m1_time
        print(f"✓ {m1_time:.2f}s ({len(raw_text)} chars)")
        
        # M2: Text Normalizer
        print(f"  [M2] Text Normalizer...", end=" ", flush=True)
        m2_start = time.time()
        response = requests.post(
            f"{MODULES['M2']}/api/normalize",
            json={"text": raw_text},
            timeout=TIMEOUT
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"M2 failed with status {response.status_code}")
        
        m2_data = response.json()
        normalized_text = m2_data["output"]["normalized_text"]
        m2_time = time.time() - m2_start
        result["module_times"]["M2_normalizer"] = m2_time
        print(f"✓ {m2_time:.2f}s")
        
        # M3: Latinizer
        print(f"  [M3] Latinizer...", end=" ", flush=True)
        m3_start = time.time()
        response = requests.post(
            f"{MODULES['M3']}/api/latinize",
            json={"text": normalized_text},
            timeout=TIMEOUT
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"M3 failed with status {response.status_code}")
        
        m3_data = response.json()
        latinized_text = m3_data["latinized_text"]
        m3_time = time.time() - m3_start
        result["module_times"]["M3_latinizer"] = m3_time
        print(f"✓ {m3_time:.2f}s")
        
        # M4: Legal Parser
        print(f"  [M4] Legal Parser...", end=" ", flush=True)
        m4_start = time.time()
        response = requests.post(
            f"{MODULES['M4']}/api/parse",
            json={
                "text": latinized_text,
                "source_uri": str(pdf_path.absolute()),
                "filename": pdf_path.name
            },
            timeout=TIMEOUT
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"M4 failed with status {response.status_code}")
        
        m4_data = response.json()
        units = m4_data["output"]["legal_units"]
        m4_time = time.time() - m4_start
        result["module_times"]["M4_parser"] = m4_time
        print(f"✓ {m4_time:.2f}s ({len(units)} units)")
        
        # M6: Assertion Extractor (Batch)
        print(f"  [M6] Assertion Extractor (Batch)...", end=" ", flush=True)
        m6_start = time.time()
        
        # Transform M4 legal units to M6 expected format
        m6_units = []
        for unit in units:
            m6_units.append({
                "unit_id": unit.get("legal_unit_id"),
                "content": unit.get("content_text"),
                "unit_type": unit.get("unit_type"),
                "number": unit.get("number")
            })
        
        response = requests.post(
            f"{MODULES['M6']}/api/extract/batch",
            json={"legal_units": m6_units, "min_confidence": 0.5},
            timeout=TIMEOUT
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"M6 failed with status {response.status_code}")
        
        m6_data = response.json()
        
        # Extract assertions from M6 batch response
        assertions = []
        for res in m6_data.get('results', []):
            if res.get('status') == 'success' and res.get('output'):
                assertions.extend(res['output'].get('assertions', []))
        
        m6_time = time.time() - m6_start
        result["module_times"]["M6_assertions"] = m6_time
        result["data"]["assertions"] = len(assertions)
        print(f"✓ {m6_time:.2f}s ({len(assertions)} assertions)")
        
        # M7: Entity Recognizer (GPU + Batch)
        print(f"  [M7] Entity Recognizer (GPU + Batch)...", end=" ", flush=True)
        m7_start = time.time()
        response = requests.post(
            f"{MODULES['M7']}/api/recognize/batch",
            json={"assertions": assertions},
            timeout=TIMEOUT
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"M7 failed with status {response.status_code}")
        
        m7_data = response.json()
        total_entities = m7_data.get('metadata', {}).get('total_entities', 0)
        m7_time = time.time() - m7_start
        result["module_times"]["M7_entities"] = m7_time
        result["data"]["entities"] = total_entities
        
        # Reconstruct assertions with entities for M8
        assertions_with_entities = []
        for res in m7_data.get('results', []):
            if res.get('status') == 'success' and res.get('output'):
                original = next((a for a in assertions if a['assertion_id'] == res['assertion_id']), None)
                if original:
                    assertion_copy = original.copy()
                    assertion_copy['entities'] = res['output'].get('entities', [])
                    assertions_with_entities.append(assertion_copy)
        
        print(f"✓ {m7_time:.2f}s ({total_entities} entities)")
        
        # M8: Condition Extractor (Batch)
        print(f"  [M8] Condition Extractor (Batch)...", end=" ", flush=True)
        m8_start = time.time()
        response = requests.post(
            f"{MODULES['M8']}/api/extract/batch",
            json={"assertions": assertions_with_entities},
            timeout=TIMEOUT
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"M8 failed with status {response.status_code}")
        
        m8_data = response.json()
        total_conditions = m8_data.get('metadata', {}).get('total_conditions', 0)
        m8_time = time.time() - m8_start
        result["module_times"]["M8_conditions"] = m8_time
        result["data"]["conditions"] = total_conditions
        
        # Reconstruct assertions with conditions for M9
        assertions_with_conditions = []
        for res in m8_data.get('results', []):
            if res.get('status') == 'success' and res.get('output'):
                original = next((a for a in assertions_with_entities if a['assertion_id'] == res['assertion_id']), None)
                if original:
                    assertion_copy = original.copy()
                    assertion_copy['conditions'] = res['output'].get('conditions', [])
                    assertions_with_conditions.append(assertion_copy)
        
        print(f"✓ {m8_time:.2f}s ({total_conditions} conditions)")
        
        # M9: Assertion Classifier (Batch)
        print(f"  [M9] Assertion Classifier (Batch)...", end=" ", flush=True)
        m9_start = time.time()
        response = requests.post(
            f"{MODULES['M9']}/classify/batch",
            json={"assertions": assertions_with_conditions},
            timeout=TIMEOUT
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"M9 failed with status {response.status_code}")
        
        m9_data = response.json()
        successful_m9 = m9_data.get('successful', 0)
        m9_time = time.time() - m9_start
        result["module_times"]["M9_classifier"] = m9_time
        
        # Reconstruct assertions with classifications for M10
        classified_assertions = []
        for res in m9_data.get('results', []):
            if res.get('status') == 'success' and res.get('classification'):
                original = next((a for a in assertions_with_conditions if a['assertion_id'] == res['assertion_id']), None)
                if original:
                    assertion_copy = original.copy()
                    assertion_copy['classification'] = res['classification']
                    classified_assertions.append(assertion_copy)
        
        print(f"✓ {m9_time:.2f}s ({successful_m9} classified)")
        
        # M10: Knowledge Enrichment (GPU + Batch)
        print(f"  [M10] Knowledge Enrichment (GPU + Batch)...", end=" ", flush=True)
        m10_start = time.time()
        response = requests.post(
            f"{MODULES['M10']}/enrich/batch",
            json={"assertions": classified_assertions},
            timeout=TIMEOUT
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"M10 failed with status {response.status_code}")
        
        m10_data = response.json()
        successful_m10 = m10_data.get('successful', 0)
        m10_time = time.time() - m10_start
        result["module_times"]["M10_enrichment"] = m10_time
        result["data"]["enriched"] = successful_m10
        print(f"✓ {m10_time:.2f}s ({successful_m10} enriched)")
        
        # Success
        doc_time = time.time() - doc_start
        result["success"] = True
        result["total_time"] = doc_time
        
        print(f"\n✅ SUCCESS - Total time: {doc_time:.2f}s")
        print(f"📊 Data: {result['data']['assertions']} assertions, {result['data']['entities']} entities, "
              f"{result['data']['conditions']} conditions, {result['data']['enriched']} enriched")
        
        return result
        
    except Exception as e:
        doc_time = time.time() - doc_start
        result["error"] = str(e)
        result["total_time"] = doc_time
        
        print(f"\n❌ FAILED - {str(e)} (time: {doc_time:.2f}s)")
        
        return result


def run_test():
    """Run the performance test"""
    
    print("\n" + "="*80)
    print("GROOVE.AI PERFORMANCE LOAD TEST - V2")
    print("="*80)
    print(f"\nTest directory: {TEST_DIR}")
    print(f"Results directory: {RESULTS_DIR}")
    
    # Check module health
    if not check_module_health():
        print("\n[ERROR] Cannot proceed - some modules are not healthy!")
        return
    
    # Get PDF files
    pdf_files = sorted(TEST_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"\n[ERROR] No PDF files found in {TEST_DIR}")
        return
    
    print(f"\n[INFO] Found {len(pdf_files)} PDF documents")
    print(f"[INFO] Starting performance test...")
    
    # Process documents sequentially
    print("\n" + "="*80)
    print("PERFORMANCE LOAD TEST")
    print("="*80)
    
    results = []
    test_start = time.time()
    
    for i, pdf_path in enumerate(pdf_files, 1):
        result = process_document(pdf_path, i, len(pdf_files))
        results.append(result)
    
    test_time = time.time() - test_start
    
    # Calculate statistics
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    times = [r["total_time"] for r in results]
    
    print("\n" + "="*80)
    print("PERFORMANCE TEST SUMMARY")
    print("="*80)
    
    print(f"\n📊 Test Duration:")
    print(f"  Total time: {test_time/60:.2f} minutes ({test_time:.2f} seconds)")
    
    print(f"\n📄 Documents:")
    print(f"  Total: {len(results)}")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")
    print(f"  Success rate: {len(successful)/len(results)*100:.2f}%")
    
    if times:
        print(f"\n⚡ Throughput:")
        print(f"  {len(successful)/test_time:.2f} docs/second")
        print(f"  {len(successful)/test_time*60:.2f} docs/minute")
        
        print(f"\n⏱️  Latency:")
        print(f"  Average: {statistics.mean(times):.2f}s")
        print(f"  Min: {min(times):.2f}s")
        print(f"  Max: {max(times):.2f}s")
        print(f"  Median: {statistics.median(times):.2f}s")
        if len(times) > 1:
            print(f"  Std Dev: {statistics.stdev(times):.2f}s")
    
    if successful:
        # Module performance
        print(f"\n🔧 Module Performance:")
        module_names = list(successful[0]["module_times"].keys())
        for module in module_names:
            module_times = [r["module_times"][module] for r in successful]
            avg_time = statistics.mean(module_times)
            print(f"  {module}: {avg_time:.2f}s avg")
        
        # Data extracted
        total_assertions = sum(r["data"].get("assertions", 0) for r in successful)
        total_entities = sum(r["data"].get("entities", 0) for r in successful)
        total_conditions = sum(r["data"].get("conditions", 0) for r in successful)
        total_enriched = sum(r["data"].get("enriched", 0) for r in successful)
        
        print(f"\n📈 Data Extracted:")
        print(f"  Assertions: {total_assertions}")
        print(f"  Entities: {total_entities}")
        print(f"  Conditions: {total_conditions}")
        print(f"  Enriched: {total_enriched}")
    
    if failed:
        print(f"\n❌ Errors: {len(failed)}")
        print(f"  First errors:")
        for r in failed[:5]:
            print(f"    - {r['document']}: {r['error']}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = RESULTS_DIR / f"performance_test_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_time": test_time,
            "total_documents": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Results saved to: {results_file}")
    
    print("\n" + "="*80)
    print("[SUCCESS] Performance test completed!")
    print("="*80)


if __name__ == "__main__":
    run_test()

# Made with Bob
