"""
Performance Load Test for GROOVE.AI Pipeline
Tests complete M1→M10 pipeline with 235 documents from perftest folder
Measures throughput, latency, resource usage, and system stability
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
from typing import List, Dict, Any, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
TEST_DIR = Path("D:/POSAO/OllamaProjects/GROOVE.AI/DOCUMENTS/DEV/onedoc")
RESULTS_DIR = Path("performance_results")
RESULTS_DIR.mkdir(exist_ok=True)

# Module URLs - Base URLs only
BASE_URL = "http://localhost"
MODULES = {
    "M1": f"{BASE_URL}:8101",  # File Reader
    "M2": f"{BASE_URL}:8102",  # Text Normalizer
    "M3": f"{BASE_URL}:8103",  # Latinizer
    "M4": f"{BASE_URL}:8105",  # Legal Parser
    "M6": f"{BASE_URL}:8106",  # Assertion Extractor
    "M7": f"{BASE_URL}:8107",  # Entity Recognizer
    "M8": f"{BASE_URL}:8108",  # Condition Extractor
    "M9": f"{BASE_URL}:8109",  # Assertion Classifier
    "M10": f"{BASE_URL}:8110", # Knowledge Enrichment
}

# Test configuration
MAX_WORKERS = 4  # Parallel processing threads
BATCH_SIZE = 10  # Documents per batch
TIMEOUT = 300    # 5 minutes per document


class PerformanceMetrics:
    """Track performance metrics"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.document_times = []
        self.module_times = {module: [] for module in MODULES.keys()}
        self.errors = []
        self.successful_docs = 0
        self.failed_docs = 0
        self.total_assertions = 0
        self.total_entities = 0
        self.total_conditions = 0
        self.enriched_assertions = 0
    
    def start(self):
        """Start timing"""
        self.start_time = time.time()
    
    def end(self):
        """End timing"""
        self.end_time = time.time()
    
    def add_document_time(self, doc_time: float):
        """Add document processing time"""
        self.document_times.append(doc_time)
    
    def add_module_time(self, module: str, module_time: float):
        """Add module processing time"""
        if module in self.module_times:
            self.module_times[module].append(module_time)
    
    def add_error(self, error: Dict[str, Any]):
        """Add error"""
        self.errors.append(error)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        total_time = self.end_time - self.start_time if self.end_time else 0
        
        summary = {
            "test_info": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
                "total_duration_seconds": round(total_time, 2),
                "total_duration_minutes": round(total_time / 60, 2),
            },
            "documents": {
                "total": self.successful_docs + self.failed_docs,
                "successful": self.successful_docs,
                "failed": self.failed_docs,
                "success_rate": round(self.successful_docs / (self.successful_docs + self.failed_docs) * 100, 2) if (self.successful_docs + self.failed_docs) > 0 else 0,
            },
            "throughput": {
                "documents_per_second": round(self.successful_docs / total_time, 2) if total_time > 0 else 0,
                "documents_per_minute": round(self.successful_docs / total_time * 60, 2) if total_time > 0 else 0,
                "documents_per_hour": round(self.successful_docs / total_time * 3600, 2) if total_time > 0 else 0,
            },
            "latency": {
                "avg_document_time_seconds": round(statistics.mean(self.document_times), 2) if self.document_times else 0,
                "min_document_time_seconds": round(min(self.document_times), 2) if self.document_times else 0,
                "max_document_time_seconds": round(max(self.document_times), 2) if self.document_times else 0,
                "median_document_time_seconds": round(statistics.median(self.document_times), 2) if self.document_times else 0,
                "stdev_document_time_seconds": round(statistics.stdev(self.document_times), 2) if len(self.document_times) > 1 else 0,
            },
            "module_performance": {},
            "data_extracted": {
                "total_assertions": self.total_assertions,
                "total_entities": self.total_entities,
                "total_conditions": self.total_conditions,
                "enriched_assertions": self.enriched_assertions,
            },
            "errors": {
                "count": len(self.errors),
                "details": self.errors[:10]  # First 10 errors
            }
        }
        
        # Add module-specific metrics
        for module, times in self.module_times.items():
            if times:
                summary["module_performance"][module] = {
                    "avg_time_seconds": round(statistics.mean(times), 2),
                    "min_time_seconds": round(min(times), 2),
                    "max_time_seconds": round(max(times), 2),
                    "total_calls": len(times),
                }
        
        return summary


def check_modules_health() -> Tuple[bool, List[str]]:
    """Check if all modules are healthy"""
    print("\n" + "="*80)
    print("CHECKING MODULE HEALTH")
    print("="*80)
    
    healthy_modules = []
    unhealthy_modules = []
    
    for module_name, url in MODULES.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"[OK] {module_name} is healthy")
                healthy_modules.append(module_name)
            else:
                print(f"[ERROR] {module_name} returned status {response.status_code}")
                unhealthy_modules.append(module_name)
        except Exception as e:
            print(f"[ERROR] {module_name} is not responding: {e}")
            unhealthy_modules.append(module_name)
    
    all_healthy = len(unhealthy_modules) == 0
    
    if all_healthy:
        print(f"\n[SUCCESS] All {len(healthy_modules)} modules are healthy!")
    else:
        print(f"\n[WARNING] {len(unhealthy_modules)} modules are unhealthy: {unhealthy_modules}")
    
    return all_healthy, unhealthy_modules


def process_single_document(pdf_path: Path, metrics: PerformanceMetrics, doc_num: int, total_docs: int) -> Dict[str, Any]:
    """Process a single document through the pipeline"""
    doc_start = time.time()
    result = {
        "document": pdf_path.name,
        "success": False,
        "error": None,
        "module_times": {},
        "data": {}
    }
    
    print(f"\n{'='*80}")
    print(f"[{doc_num}/{total_docs}] Processing: {pdf_path.name}")
    print(f"{'='*80}")
    
    try:
        # M1: File Reader
        m1_start = time.time()
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path.name, f, 'application/pdf')}
            response = requests.post(f"{MODULES['M1']}/api/read", files=files, timeout=TIMEOUT)
        
        if response.status_code != 200:
            raise Exception(f"M1 failed: {response.status_code}")
        
        m1_result = response.json()
        result["module_times"]["M1"] = time.time() - m1_start
        metrics.add_module_time("M1", result["module_times"]["M1"])
        
        # M2: Text Normalizer
        m2_start = time.time()
        response = requests.post(
            f"{MODULES['M2']}/api/normalize",
            json={"text": m1_result["text"], "document_id": m1_result["document_id"]},
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"M2 failed: {response.status_code}")
        
        m2_result = response.json()
        result["module_times"]["M2"] = time.time() - m2_start
        metrics.add_module_time("M2", result["module_times"]["M2"])
        
        # M3: Latinizer
        m3_start = time.time()
        response = requests.post(
            f"{MODULES['M3']}/api/latinize",
            json={"text": m2_result["normalized_text"], "document_id": m2_result["document_id"]},
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"M3 failed: {response.status_code}")
        
        m3_result = response.json()
        result["module_times"]["M3"] = time.time() - m3_start
        metrics.add_module_time("M3", result["module_times"]["M3"])
        
        # M4: Legal Parser
        m4_start = time.time()
        response = requests.post(
            f"{MODULES['M4']}/api/parse",
            json={"text": m3_result["latinized_text"], "document_id": m3_result["document_id"]},
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"M4 failed: {response.status_code}")
        
        m4_result = response.json()
        result["module_times"]["M4"] = time.time() - m4_start
        metrics.add_module_time("M4", result["module_times"]["M4"])
        
        # M6: Assertion Extractor (batch)
        m6_start = time.time()
        response = requests.post(
            f"{MODULES['M6']}/api/extract/batch",
            json={
                "document_id": m4_result["document_id"],
                "sample_units": m4_result["sample_units"]
            },
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"M6 failed: {response.status_code}")
        
        m6_result = response.json()
        result["module_times"]["M6"] = time.time() - m6_start
        metrics.add_module_time("M6", result["module_times"]["M6"])
        metrics.total_assertions += len(m6_result.get("assertions", []))
        result["data"]["assertions"] = len(m6_result.get("assertions", []))
        
        # M7: Entity Recognizer (batch)
        m7_start = time.time()
        response = requests.post(
            f"{MODULES['M7']}/api/recognize/batch",
            json={"assertions": m6_result["assertions"]},
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"M7 failed: {response.status_code}")
        
        m7_result = response.json()
        result["module_times"]["M7"] = time.time() - m7_start
        metrics.add_module_time("M7", result["module_times"]["M7"])
        
        total_entities = sum(len(r.get("entities", [])) for r in m7_result.get("results", []))
        metrics.total_entities += total_entities
        result["data"]["entities"] = total_entities
        
        # M8: Condition Extractor (batch)
        m8_start = time.time()
        response = requests.post(
            f"{MODULES['M8']}/api/extract/batch",
            json={"assertions": m6_result["assertions"]},
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"M8 failed: {response.status_code}")
        
        m8_result = response.json()
        result["module_times"]["M8"] = time.time() - m8_start
        metrics.add_module_time("M8", result["module_times"]["M8"])
        
        total_conditions = sum(len(r.get("conditions", [])) for r in m8_result.get("results", []))
        metrics.total_conditions += total_conditions
        result["data"]["conditions"] = total_conditions
        
        # M9: Assertion Classifier (batch)
        m9_start = time.time()
        response = requests.post(
            f"{MODULES['M9']}/api/classify/batch",
            json={"assertions": m6_result["assertions"]},
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"M9 failed: {response.status_code}")
        
        m9_result = response.json()
        result["module_times"]["M9"] = time.time() - m9_start
        metrics.add_module_time("M9", result["module_times"]["M9"])
        
        # M10: Knowledge Enrichment (batch)
        m10_start = time.time()
        enrichment_requests = []
        for i, assertion in enumerate(m6_result["assertions"]):
            entities = m7_result["results"][i].get("entities", []) if i < len(m7_result["results"]) else []
            enrichment_requests.append({
                "assertion_id": assertion["assertion_id"],
                "text": assertion["text"],
                "entities": entities
            })
        
        response = requests.post(
            f"{MODULES['M10']}/api/enrich/batch",
            json={"requests": enrichment_requests},
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"M10 failed: {response.status_code}")
        
        m10_result = response.json()
        result["module_times"]["M10"] = time.time() - m10_start
        metrics.add_module_time("M10", result["module_times"]["M10"])
        
        enriched_count = len(m10_result.get("results", []))
        metrics.enriched_assertions += enriched_count
        result["data"]["enriched"] = enriched_count
        
        # Success!
        result["success"] = True
        metrics.successful_docs += 1
        
    except Exception as e:
        result["error"] = str(e)
        metrics.failed_docs += 1
        metrics.add_error({
            "document": pdf_path.name,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
    
    doc_time = time.time() - doc_start
    result["total_time"] = doc_time
    metrics.add_document_time(doc_time)
    
    return result


def run_performance_test(max_documents: Optional[int] = None) -> PerformanceMetrics:
    """Run performance test on all documents"""
    print("\n" + "="*80)
    print("PERFORMANCE LOAD TEST")
    print("="*80)
    
    # Get all PDF files
    pdf_files = list(TEST_DIR.glob("*.pdf"))
    
    if max_documents:
        pdf_files = pdf_files[:max_documents]
    
    print(f"\nFound {len(pdf_files)} PDF documents")
    print(f"Test directory: {TEST_DIR}")
    
    metrics = PerformanceMetrics()
    metrics.start()
    
    # Process documents sequentially for better output
    for i, pdf in enumerate(pdf_files, 1):
        try:
            result = process_single_document(pdf, metrics, i, len(pdf_files))
        except Exception as e:
            print(f"\n  ❌ EXCEPTION: {e}")
            metrics.failed_docs += 1
    
    metrics.end()
    
    return metrics


def save_results(metrics: PerformanceMetrics):
    """Save test results to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = RESULTS_DIR / f"performance_test_{timestamp}.json"
    
    summary = metrics.get_summary()
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Results saved to: {results_file}")
    
    return results_file


def print_summary(metrics: PerformanceMetrics):
    """Print test summary"""
    summary = metrics.get_summary()
    
    print("\n" + "="*80)
    print("PERFORMANCE TEST SUMMARY")
    print("="*80)
    
    print(f"\n📊 Test Duration:")
    print(f"  Total time: {summary['test_info']['total_duration_minutes']:.2f} minutes ({summary['test_info']['total_duration_seconds']:.2f} seconds)")
    
    print(f"\n📄 Documents:")
    print(f"  Total: {summary['documents']['total']}")
    print(f"  Successful: {summary['documents']['successful']}")
    print(f"  Failed: {summary['documents']['failed']}")
    print(f"  Success rate: {summary['documents']['success_rate']:.2f}%")
    
    print(f"\n⚡ Throughput:")
    print(f"  {summary['throughput']['documents_per_second']:.2f} docs/second")
    print(f"  {summary['throughput']['documents_per_minute']:.2f} docs/minute")
    print(f"  {summary['throughput']['documents_per_hour']:.2f} docs/hour")
    
    print(f"\n⏱️  Latency:")
    print(f"  Average: {summary['latency']['avg_document_time_seconds']:.2f}s")
    print(f"  Min: {summary['latency']['min_document_time_seconds']:.2f}s")
    print(f"  Max: {summary['latency']['max_document_time_seconds']:.2f}s")
    print(f"  Median: {summary['latency']['median_document_time_seconds']:.2f}s")
    print(f"  Std Dev: {summary['latency']['stdev_document_time_seconds']:.2f}s")
    
    print(f"\n🔧 Module Performance:")
    for module, perf in summary['module_performance'].items():
        print(f"  {module}: avg={perf['avg_time_seconds']:.2f}s, min={perf['min_time_seconds']:.2f}s, max={perf['max_time_seconds']:.2f}s")
    
    print(f"\n📈 Data Extracted:")
    print(f"  Assertions: {summary['data_extracted']['total_assertions']}")
    print(f"  Entities: {summary['data_extracted']['total_entities']}")
    print(f"  Conditions: {summary['data_extracted']['total_conditions']}")
    print(f"  Enriched: {summary['data_extracted']['enriched_assertions']}")
    
    if summary['errors']['count'] > 0:
        print(f"\n❌ Errors: {summary['errors']['count']}")
        print("  First errors:")
        for error in summary['errors']['details'][:5]:
            print(f"    - {error['document']}: {error['error']}")


def main():
    """Main test function"""
    print("\n" + "="*80)
    print("GROOVE.AI PERFORMANCE LOAD TEST")
    print("="*80)
    print(f"\nTest directory: {TEST_DIR}")
    print(f"Results directory: {RESULTS_DIR}")
    
    # Check module health
    all_healthy, unhealthy = check_modules_health()
    
    if not all_healthy:
        print(f"\n[ERROR] Cannot proceed - {len(unhealthy)} modules are unhealthy")
        print("Please start all modules and try again")
        return 1
    
    # Run performance test
    print("\n[INFO] Starting performance test...")
    metrics = run_performance_test()
    
    # Print summary
    print_summary(metrics)
    
    # Save results
    results_file = save_results(metrics)
    
    print("\n" + "="*80)
    print("[SUCCESS] Performance test completed!")
    print("="*80)
    
    return 0


if __name__ == "__main__":
    exit(main())

# Made with Bob
