"""
Complete Batch Pipeline Test
Tests the entire pipeline with batch processing endpoints for optimal performance.
Supports command-line arguments for filename and verbose output.
"""

import requests
import json
import time
import argparse
from pathlib import Path

# Module endpoints
ENDPOINTS = {
    'M1': 'http://localhost:8101',  # File Reader
    'M2': 'http://localhost:8102',  # Text Normalizer
    'M3': 'http://localhost:8103',  # Latinizer
    'M4': 'http://localhost:8105',  # Legal Parser
    'M6': 'http://localhost:8106',  # Assertion Extractor
    'M7': 'http://localhost:8107',  # Entity Recognizer
    'M8': 'http://localhost:8108',  # Condition Extractor
    'M9': 'http://localhost:8109',  # Assertion Classifier
    'M10': 'http://localhost:8110', # Knowledge Enrichment
}

def print_verbose_output(phase_name, result):
    """Print verbose output with Unicode error handling"""
    print(f"\n{'='*80}")
    print(f"{phase_name} - Complete Output:")
    print('='*80)
    try:
        output = json.dumps(result, indent=2, ensure_ascii=False)
        print(output)
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        output = json.dumps(result, indent=2, ensure_ascii=True)
        print(output)
    print('='*80)

def test_complete_batch_pipeline(file_path: str, verbose: bool = False):
    """Test complete pipeline with batch processing"""
    
    print(f"\n{'='*80}")
    print("COMPLETE BATCH PIPELINE TEST")
    print('='*80)
    print(f"Testing file: {file_path}")
    print(f"Verbose mode: {'ON' if verbose else 'OFF'}")
    
    total_start = time.time()
    
    # Phase 1: File Reading (M1)
    print("\n[Phase 1] Reading file...")
    phase_start = time.time()
    
    response = requests.post(
        f"{ENDPOINTS['M1']}/api/read",
        json={"file_path": file_path}
    )
    
    if response.status_code not in [200, 201]:
        print(f"[ERROR] M1 failed: {response.status_code}")
        try:
            print(response.text)
        except UnicodeEncodeError:
            print(response.text.encode('ascii', 'replace').decode('ascii'))
        return
    
    m1_result = response.json()
    raw_text = m1_result['output']['text']
    phase_time = time.time() - phase_start
    print(f"[OK] M1 completed in {phase_time:.2f}s")
    print(f"  - Extracted text length: {len(raw_text)} characters")
    
    if verbose:
        print_verbose_output("Phase 1: File Reading (M1)", m1_result)
    
    # Phase 2: Text Normalization (M2)
    print("\n[Phase 2] Normalizing text...")
    phase_start = time.time()
    
    response = requests.post(
        f"{ENDPOINTS['M2']}/api/normalize",
        json={"text": raw_text}
    )
    
    if response.status_code not in [200, 201]:
        print(f"[ERROR] M2 failed: {response.status_code}")
        try:
            print(response.text)
        except UnicodeEncodeError:
            print(response.text.encode('ascii', 'replace').decode('ascii'))
        return
    
    m2_result = response.json()
    normalized_text = m2_result.get('normalized_text') or m2_result.get('output', {}).get('normalized_text')
    phase_time = time.time() - phase_start
    print(f"[OK] M2 completed in {phase_time:.2f}s")
    print(f"  - Normalized text length: {len(normalized_text)} characters")
    
    if verbose:
        print_verbose_output("Phase 2: Text Normalization (M2)", m2_result)
    
    # Phase 3: Latinization (M3)
    print("\n[Phase 3] Latinizing text...")
    phase_start = time.time()
    
    response = requests.post(
        f"{ENDPOINTS['M3']}/api/latinize",
        json={"text": normalized_text}
    )
    
    if response.status_code not in [200, 201]:
        print(f"[ERROR] M3 failed: {response.status_code}")
        try:
            print(response.text)
        except UnicodeEncodeError:
            print(response.text.encode('ascii', 'replace').decode('ascii'))
        return
    
    m3_result = response.json()
    latinized_text = m3_result.get('latinized_text') or m3_result.get('output', {}).get('latinized_text')
    phase_time = time.time() - phase_start
    print(f"[OK] M3 completed in {phase_time:.2f}s")
    print(f"  - Latinized text length: {len(latinized_text)} characters")
    
    if verbose:
        print_verbose_output("Phase 3: Latinization (M3)", m3_result)
    
    # Phase 4: Legal Parsing (M4)
    print("\n[Phase 4] Parsing legal structure...")
    phase_start = time.time()
    
    response = requests.post(
        f"{ENDPOINTS['M4']}/api/parse",
        json={
            "text": latinized_text,
            "source_uri": f"file:///{file_path}",
            "filename": Path(file_path).name
        }
    )
    
    if response.status_code not in [200, 201]:
        print(f"[ERROR] M4 failed: {response.status_code}")
        try:
            print(response.text)
        except UnicodeEncodeError:
            print(response.text.encode('ascii', 'replace').decode('ascii'))
        return
    
    m4_result = response.json()
    output = m4_result.get('output', m4_result)
    units = output.get('legal_units', [])
    phase_time = time.time() - phase_start
    print(f"[OK] M4 completed in {phase_time:.2f}s")
    print(f"  - Parsed units: {len(units)}")
    
    if verbose:
        print_verbose_output("Phase 4: Legal Parsing (M4)", m4_result)
    
    # Phase 5: Batch Assertion Extraction (M6)
    print("\n[Phase 5] Extracting assertions (batch)...")
    phase_start = time.time()
    
    # Transform M4 legal units to M6 expected format
    # M4 uses: legal_unit_id, content_text
    # M6 expects: unit_id, content
    m6_units = []
    for unit in units:
        m6_units.append({
            "unit_id": unit.get("legal_unit_id"),
            "content": unit.get("content_text"),
            "unit_type": unit.get("unit_type"),
            "number": unit.get("number")
        })
    
    response = requests.post(
        f"{ENDPOINTS['M6']}/api/extract/batch",
        json={"legal_units": m6_units, "min_confidence": 0.5}
    )
    
    if response.status_code not in [200, 201]:
        print(f"[ERROR] M6 failed: {response.status_code}")
        try:
            print(response.text)
        except UnicodeEncodeError:
            print(response.text.encode('ascii', 'replace').decode('ascii'))
        return
    
    m6_result = response.json()
    phase_time = time.time() - phase_start
    
    # Extract assertions from M6 batch response structure
    # M6 returns: {"results": [{"legal_unit_id": "...", "output": {"assertions": [...]}}]}
    assertions = []
    for result in m6_result.get('results', []):
        if result.get('status') == 'success' and result.get('output'):
            assertions.extend(result['output'].get('assertions', []))
    
    total_assertions = len(assertions)
    print(f"[OK] M6 completed in {phase_time:.2f}s")
    print(f"  - Total assertions: {total_assertions}")
    print(f"  - Processing time: {m6_result.get('processing_ms', 0):.0f}ms")
    print(f"  - Throughput: {m6_result.get('throughput', 0):.2f} units/sec")
    
    if verbose:
        print_verbose_output("Phase 5: Assertion Extraction (M6)", m6_result)
    
    # Phase 6: Batch Entity Recognition (M7)
    print("\n[Phase 6] Recognizing entities (batch)...")
    phase_start = time.time()
    
    response = requests.post(
        f"{ENDPOINTS['M7']}/api/recognize/batch",
        json={"assertions": assertions}
    )
    
    if response.status_code not in [200, 201]:
        print(f"[ERROR] M7 failed: {response.status_code}")
        try:
            print(response.text)
        except UnicodeEncodeError:
            print(response.text.encode('ascii', 'replace').decode('ascii'))
        return
    
    m7_result = response.json()
    phase_time = time.time() - phase_start
    
    # Extract entities from M7 batch response structure
    # M7 returns: {"results": [{"assertion_id": "...", "output": {"entities": [...]}}]}
    total_entities = m7_result.get('metadata', {}).get('total_entities', 0)
    print(f"[OK] M7 completed in {phase_time:.2f}s")
    print(f"  - Total entities: {total_entities}")
    print(f"  - Processing time: {m7_result.get('metadata', {}).get('timings', {}).get('processing_ms', 0):.0f}ms")
    
    # Calculate throughput from metadata
    throughput = m7_result.get('metadata', {}).get('throughput_assertions_per_sec', 0)
    print(f"  - Throughput: {throughput:.2f} assertions/sec")
    
    if verbose:
        print_verbose_output("Phase 6: Entity Recognition (M7)", m7_result)
    
    # Reconstruct assertions with entities for M8
    # M8 expects: {"assertions": [{"assertion_id": "...", "text": "...", "entities": [...]}]}
    assertions_with_entities = []
    for result in m7_result.get('results', []):
        if result.get('status') == 'success' and result.get('output'):
            # Find original assertion
            original_assertion = next(
                (a for a in assertions if a['assertion_id'] == result['assertion_id']),
                None
            )
            if original_assertion:
                assertion_with_entities = original_assertion.copy()
                assertion_with_entities['entities'] = result['output'].get('entities', [])
                assertions_with_entities.append(assertion_with_entities)
    
    # Phase 7: Batch Condition Extraction (M8)
    print("\n[Phase 7] Extracting conditions (batch)...")
    phase_start = time.time()
    
    response = requests.post(
        f"{ENDPOINTS['M8']}/api/extract/batch",
        json={"assertions": assertions_with_entities}
    )
    
    if response.status_code not in [200, 201]:
        print(f"[ERROR] M8 failed: {response.status_code}")
        try:
            print(response.text)
        except UnicodeEncodeError:
            print(response.text.encode('ascii', 'replace').decode('ascii'))
        return
    
    m8_result = response.json()
    phase_time = time.time() - phase_start
    
    # Extract conditions from M8 batch response structure
    total_conditions = m8_result.get('metadata', {}).get('total_conditions', 0)
    print(f"[OK] M8 completed in {phase_time:.2f}s")
    print(f"  - Total conditions: {total_conditions}")
    print(f"  - Processing time: {m8_result.get('metadata', {}).get('timings', {}).get('processing_ms', 0):.0f}ms")
    
    throughput = m8_result.get('metadata', {}).get('throughput_assertions_per_sec', 0)
    print(f"  - Throughput: {throughput:.2f} assertions/sec")
    
    if verbose:
        print_verbose_output("Phase 7: Condition Extraction (M8)", m8_result)
    
    # Reconstruct assertions with conditions for M9
    assertions_with_conditions = []
    for result in m8_result.get('results', []):
        if result.get('status') == 'success' and result.get('output'):
            # Find assertion with entities
            original_assertion = next(
                (a for a in assertions_with_entities if a['assertion_id'] == result['assertion_id']),
                None
            )
            if original_assertion:
                assertion_with_conditions = original_assertion.copy()
                assertion_with_conditions['conditions'] = result['output'].get('conditions', [])
                assertions_with_conditions.append(assertion_with_conditions)
    
    # Phase 8: Batch Assertion Classification (M9)
    print("\n[Phase 8] Classifying assertions (batch)...")
    phase_start = time.time()
    
    response = requests.post(
        f"{ENDPOINTS['M9']}/classify/batch",
        json={"assertions": assertions_with_conditions}
    )
    
    if response.status_code not in [200, 201]:
        print(f"[ERROR] M9 failed: {response.status_code}")
        try:
            print(response.text)
        except UnicodeEncodeError:
            print(response.text.encode('ascii', 'replace').decode('ascii'))
        return
    
    m9_result = response.json()
    phase_time = time.time() - phase_start
    
    # Extract classification results
    successful = m9_result.get('successful', 0)
    print(f"[OK] M9 completed in {phase_time:.2f}s")
    print(f"  - Classified assertions: {successful}")
    print(f"  - Processing time: {m9_result.get('metadata', {}).get('timing', {}).get('processing_ms', 0):.0f}ms")
    
    throughput = m9_result.get('metadata', {}).get('timing', {}).get('throughput_assertions_per_sec', 0)
    print(f"  - Throughput: {throughput:.2f} assertions/sec")
    
    if verbose:
        print_verbose_output("Phase 8: Assertion Classification (M9)", m9_result)
    
    # Reconstruct assertions with classifications for M10
    classified_assertions = []
    for result in m9_result.get('results', []):
        if result.get('status') == 'success' and result.get('classification'):
            # Find assertion with conditions
            original_assertion = next(
                (a for a in assertions_with_conditions if a['assertion_id'] == result['assertion_id']),
                None
            )
            if original_assertion:
                classified_assertion = original_assertion.copy()
                classified_assertion['classification'] = result['classification']
                classified_assertions.append(classified_assertion)
    
    # Phase 9: Batch Knowledge Enrichment (M10)
    print("\n[Phase 9] Enriching with knowledge (batch)...")
    phase_start = time.time()
    
    response = requests.post(
        f"{ENDPOINTS['M10']}/enrich/batch",
        json={"assertions": classified_assertions}
    )
    
    if response.status_code not in [200, 201]:
        print(f"[ERROR] M10 failed: {response.status_code}")
        try:
            print(response.text)
        except UnicodeEncodeError:
            print(response.text.encode('ascii', 'replace').decode('ascii'))
        return
    
    m10_result = response.json()
    phase_time = time.time() - phase_start
    
    # Extract enrichment results
    successful = m10_result.get('successful', 0)
    print(f"[OK] M10 completed in {phase_time:.2f}s")
    print(f"  - Enriched assertions: {successful}")
    print(f"  - Processing time: {m10_result.get('metadata', {}).get('timing', {}).get('total_ms', 0):.0f}ms")
    
    throughput = m10_result.get('metadata', {}).get('timing', {}).get('throughput_assertions_per_sec', 0)
    print(f"  - Throughput: {throughput:.2f} assertions/sec")
    
    if verbose:
        print_verbose_output("Phase 9: Knowledge Enrichment (M10)", m10_result)
    
    # Final Summary
    total_time = time.time() - total_start
    
    print(f"\n{'='*80}")
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print('='*80)
    print(f"Total execution time: {total_time:.2f}s")
    print(f"\nFinal Statistics:")
    print(f"  - Legal units: {len(m4_result.get('units', []))}")
    print(f"  - Assertions: {len(m10_result.get('assertions', []))}")
    print(f"  - Entities: {total_entities}")
    print(f"  - Conditions: {total_conditions}")
    
    # Save results
    output_file = 'batch_pipeline_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(m10_result, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Results saved to: {output_file}")
    print('='*80)

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Test complete batch pipeline with performance optimizations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_batch_pipeline_complete.py document.pdf
  python test_batch_pipeline_complete.py document.pdf --verbose
  python test_batch_pipeline_complete.py "D:\\path\\to\\document.pdf" --verbose
        """
    )
    
    parser.add_argument(
        'filename',
        help='Path to the PDF file to process'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print complete output after each phase'
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    if not Path(args.filename).exists():
        print(f"Error: File not found: {args.filename}")
        exit(1)
    
    # Run the test
    test_complete_batch_pipeline(args.filename, args.verbose)

# Made with Bob
