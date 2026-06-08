"""
Performance Load Test for GROOVE.AI Pipeline - Version 3
Enhanced with memory management, checkpointing, and retry logic
Tests complete M1→M10 pipeline with verbose output
"""

import os
import sys
import io
import time
import json
import requests
import gc
import psutil
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
MAX_RETRIES = 2  # Retry failed requests
CLEANUP_INTERVAL = 10  # Deep cleanup every N documents
CHECKPOINT_INTERVAL = 5  # Save checkpoint every N documents

# Create persistent session
session = requests.Session()


def log_memory_usage(stage: str):
    """Log current memory usage"""
    process = psutil.Process()
    mem_info = process.memory_info()
    mem_mb = mem_info.rss / (1024 * 1024)
    
    # GPU memory if available
    gpu_mem = "N/A"
    try:
        import torch
        if torch.cuda.is_available():
            gpu_mem = f"{torch.cuda.memory_allocated() / (1024**2):.0f}MB"
    except:
        pass
    
    print(f"  💾 Memory [{stage}]: RAM={mem_mb:.0f}MB, GPU={gpu_mem}")


def cleanup_resources():
    """Clean up resources between documents"""
    print("  🧹 Cleaning up resources...")
    
    # Clear caches via API
    for module_name, url in MODULES.items():
        if module_name in ["M6", "M7", "M8", "M9", "M10"]:
            try:
                session.post(f"{url}/cache/clear", timeout=5)
            except:
                pass
    
    # Force garbage collection
    gc.collect()
    
    # Clear GPU memory if available
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    except:
        pass


def make_request_with_retry(url: str, json_data: Dict, max_retries: int = MAX_RETRIES, timeout: int = TIMEOUT) -> requests.Response:
    """Make HTTP request with retry logic"""
    for attempt in range(max_retries + 1):
        try:
            response = session.post(url, json=json_data, timeout=timeout)
            return response
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"\n    ⏱️ Timeout, retrying in {wait_time}s... (attempt {attempt + 2}/{max_retries + 1})")
                time.sleep(wait_time)
            else:
                raise
        except requests.exceptions.ConnectionError:
            if attempt < max_retries:
                print(f"\n    🔌 Connection error, retrying... (attempt {attempt + 2}/{max_retries + 1})")
                time.sleep(2)
            else:
                raise
    
    raise Exception("Max retries exceeded")


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
    log_memory_usage("start")
    
    try:
        # M1: File Reader
        print(f"  [M1] File Reader...", end=" ", flush=True)
        m1_start = time.time()
        response = make_request_with_retry(
            f"{MODULES['M1']}/api/read",
            {"file_path": str(pdf_path.absolute())}
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"M1 failed with status {response.status_code}: {response.text[:200]}")
        
        m1_data = response.json()
        text = m1_data["output"]["text"]
        m1_time = time.time() - m1_start
        result["module_times"]["M1_file_reader"] = m1_time
        print(f"✓ {m1_time:.2f}s ({len(text)} chars)")
        
        # M2: Text Normalizer
        print(f"  [M2] Text Normalizer...", end=" ", flush=True)
        m2_start = time.time()
        response = make_request_with_retry(
            f"{MODULES['M2']}/api/normalize",
            {"text": text}
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
        response = make_request_with_retry(
            f"{MODULES['M3']}/api/latinize",
            {"text": normalized_text}
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
        response = make_request_with_retry(
            f"{MODULES['M4']}/api/parse",
            {
                "text": latinized_text,
                "source_uri": str(pdf_path),
                "filename": pdf_path.name
            }
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"M4 failed with status {response.status_code}")
        
        m4_data = response.json()
        units = m4_data["output"]["legal_units"]
        m4_time = time.time() - m4_start
        result["module_times"]["M4_parser"] = m4_time
        print(f"✓ {m4_time:.2f}s ({len(units)} units)")
        
        # Transform M4 units to M6 format
        m6_units = []
        for unit in units:
            m6_units.append({
                "unit_id": unit.get("legal_unit_id"),
                "content": unit.get("content_text"),
                "unit_type": unit.get("unit_type"),
                "number": unit.get("number")
            })
        
        # M6: Assertion Extractor (Batch)
        print(f"  [M6] Assertion Extractor (Batch)...", end=" ", flush=True)
        m6_start = time.time()
        response = make_request_with_retry(
            f"{MODULES['M6']}/api/extract/batch",
            {
                "legal_units": m6_units,
                "min_confidence": 0.5
            }
        )
        
        if response.status_code not in [200, 201]:
            error_detail = response.text[:1000] if response.text else "No error details"
            raise Exception(f"M6 failed with status {response.status_code}: {error_detail}")
        
        m6_data = response.json()
        
        # Extract assertions from batch results
        # M6 returns: {"results": [{"legal_unit_id": "...", "status": "success", "output": {"assertions": [...]}}]}
        assertions = []
        for res in m6_data.get('results', []):
            if res.get('status') == 'success' and res.get('output'):
                assertions.extend(res['output'].get('assertions', []))
        
        m6_time = time.time() - m6_start
        result["module_times"]["M6_assertions"] = m6_time
        result["data"]["assertions"] = len(assertions)
        print(f"✓ {m6_time:.2f}s ({len(assertions)} assertions)")
        
        if not assertions:
            print("  ⚠️ No assertions found, skipping remaining modules")
            result["success"] = True
            result["total_time"] = time.time() - doc_start
            return result
        
        log_memory_usage("after M6")
        
        # M7: Entity Recognizer (GPU + Batch)
        print(f"  [M7] Entity Recognizer (GPU + Batch)...", end=" ", flush=True)
        m7_start = time.time()
        response = make_request_with_retry(
            f"{MODULES['M7']}/api/recognize/batch",
            {"assertions": assertions}
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
        log_memory_usage("after M7")
        
        # M8: Condition Extractor (Batch)
        print(f"  [M8] Condition Extractor (Batch)...", end=" ", flush=True)
        m8_start = time.time()
        response = make_request_with_retry(
            f"{MODULES['M8']}/api/extract/batch",
            {"assertions": assertions_with_entities}
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
        response = make_request_with_retry(
            f"{MODULES['M9']}/classify/batch",
            {"assertions": assertions_with_conditions}
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
        response = make_request_with_retry(
            f"{MODULES['M10']}/enrich/batch",
            {"assertions": classified_assertions}
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"M10 failed with status {response.status_code}")
        
        m10_data = response.json()
        successful_m10 = m10_data.get('successful', 0)
        m10_time = time.time() - m10_start
        result["module_times"]["M10_enrichment"] = m10_time
        result["data"]["enriched"] = successful_m10
        print(f"✓ {m10_time:.2f}s ({successful_m10} enriched)")
        
        log_memory_usage("after M10")
        
        # Success
        doc_time = time.time() - doc_start
        result["success"] = True
        result["total_time"] = doc_time
        
        print(f"\n✅ SUCCESS - Total time: {doc_time:.2f}s")
        print(f"📊 Data: {result['data'].get('assertions', 0)} assertions, {result['data'].get('entities', 0)} entities, "
              f"{result['data'].get('conditions', 0)} conditions, {result['data'].get('enriched', 0)} enriched")
        
        return result
        
    except Exception as e:
        doc_time = time.time() - doc_start
        result["error"] = str(e)
        result["total_time"] = doc_time
        
        print(f"\n❌ FAILED - {str(e)} (time: {doc_time:.2f}s)")
        
        return result


def save_checkpoint(results: List[Dict], checkpoint_file: Path):
    """Save progress checkpoint"""
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump({"results": results}, f, indent=2, ensure_ascii=False)


def load_checkpoint(checkpoint_file: Path) -> Optional[List[Dict]]:
    """Load progress checkpoint"""
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("results", [])
    return None


def run_test():
    """Run the performance test with checkpointing and resource management"""
    
    print("\n" + "="*80)
    print("GROOVE.AI PERFORMANCE LOAD TEST - V3 (Enhanced)")
    print("="*80)
    print(f"\nTest directory: {TEST_DIR}")
    print(f"Results directory: {RESULTS_DIR}")
    print(f"Cleanup interval: Every {CLEANUP_INTERVAL} documents")
    print(f"Checkpoint interval: Every {CHECKPOINT_INTERVAL} documents")
    
    # Check module health
    if not check_module_health():
        print("\n[ERROR] Cannot proceed - some modules are not healthy!")
        return
    
    # Get PDF files
    pdf_files = sorted(TEST_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"\n[ERROR] No PDF files found in {TEST_DIR}")
        return
    
    print(f"\n📄 Found {len(pdf_files)} PDF files to process")
    
    # Try to resume from checkpoint
    checkpoint_file = RESULTS_DIR / "checkpoint.json"
    results = load_checkpoint(checkpoint_file)
    
    if results:
        start_idx = len(results)
        print(f"\n📂 Resuming from checkpoint: {start_idx} documents already completed")
    else:
        results = []
        start_idx = 0
    
    # Process documents
    test_start = time.time()
    
    for idx in range(start_idx, len(pdf_files)):
        pdf_path = pdf_files[idx]
        doc_num = idx + 1
        
        # Process document
        result = process_document(pdf_path, doc_num, len(pdf_files))
        results.append(result)
        
        # Cleanup after each document
        cleanup_resources()
        
        # Deep cleanup every N documents
        if doc_num % CLEANUP_INTERVAL == 0:
            print(f"\n🧹 Deep cleanup after {doc_num} documents...")
            time.sleep(2)  # Allow cleanup to complete
            log_memory_usage("after deep cleanup")
        
        # Save checkpoint every N documents
        if doc_num % CHECKPOINT_INTERVAL == 0:
            save_checkpoint(results, checkpoint_file)
            print(f"💾 Checkpoint saved ({doc_num} documents)")
    
    # Calculate final statistics
    test_time = time.time() - test_start
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}")
    print(f"Total time: {test_time:.2f}s ({test_time/60:.2f} minutes)")
    print(f"Documents processed: {len(results)}")
    print(f"Successful: {successful} ({successful/len(results)*100:.1f}%)")
    print(f"Failed: {failed} ({failed/len(results)*100:.1f}%)")
    print(f"Average time per document: {test_time/len(results):.2f}s")
    
    # Save final results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = RESULTS_DIR / f"performance_test_{timestamp}.json"
    
    final_results = {
        "test_time": test_time,
        "total_documents": len(results),
        "successful": successful,
        "failed": failed,
        "results": results
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Results saved to: {results_file}")
    
    # Remove checkpoint file
    if checkpoint_file.exists():
        checkpoint_file.unlink()
        print("🗑️ Checkpoint file removed")


if __name__ == "__main__":
    try:
        run_test()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        print("💾 Progress has been saved in checkpoint file")
        print("Run the script again to resume from where you left off")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
