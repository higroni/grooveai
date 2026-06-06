"""
Full Pipeline Test: Modules 1-4
Tests the complete pipeline from PDF to parsed legal units
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
PDF_PATH = BASE_DIR / "DOCUMENTS" / "DEV" / "onedoc" / "radni_odnosi_0001_000001.pdf"
OUTPUT_JSON = BASE_DIR / "pipeline_output_parsed.json"

# Module endpoints
M1_URL = "http://localhost:8101"  # File Reader
M2_URL = "http://localhost:8102"  # Text Normalizer
M3_URL = "http://localhost:8103"  # Latinizer
M4_URL = "http://localhost:8104"  # Legal Parser

def test_pipeline():
    print("=" * 80)
    print("FULL PIPELINE TEST: Modules 1-4")
    print("=" * 80)
    print()
    
    # Step 1: Read PDF
    print("[STEP 1] Reading PDF file...")
    print(f"File: {PDF_PATH}")
    
    with open(PDF_PATH, 'rb') as f:
        files = {'file': ('radni_odnosi.pdf', f, 'application/pdf')}
        response = requests.post(f"{M1_URL}/api/read", files=files, timeout=30)
    
    if response.status_code != 200:
        print(f"[ERROR] Module 1 failed: {response.status_code}")
        return
    
    m1_result = response.json()
    text = m1_result['output']['text']
    print(f"[OK] Extracted {len(text)} characters")
    print()
    
    # Step 2: Normalize text
    print("[STEP 2] Normalizing text...")
    
    response = requests.post(
        f"{M2_URL}/api/normalize",
        json={"text": text},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"[ERROR] Module 2 failed: {response.status_code}")
        return
    
    m2_result = response.json()
    normalized_text = m2_result['output']['text']
    print(f"[OK] Normalized {len(normalized_text)} characters")
    print()
    
    # Step 3: Latinize text
    print("[STEP 3] Latinizing text...")
    
    response = requests.post(
        f"{M3_URL}/api/latinize",
        json={"text": normalized_text},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"[ERROR] Module 3 failed: {response.status_code}")
        return
    
    m3_result = response.json()
    latinized_text = m3_result['output']['text']
    print(f"[OK] Latinized {len(latinized_text)} characters")
    print()
    
    # Step 4: Parse legal structure
    print("[STEP 4] Parsing legal structure...")
    print("This may take a moment...")
    
    response = requests.post(
        f"{M4_URL}/api/parse",
        json={
            "text": latinized_text,
            "filename": "radni_odnosi.pdf",
            "document_type": "law"
        },
        timeout=60
    )
    
    if response.status_code != 200:
        print(f"[ERROR] Module 4 failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    m4_result = response.json()
    print(f"[OK] Parsing complete")
    print()
    
    # Analyze results
    output = m4_result['output']
    stats = output['statistics']
    legal_units = output['legal_units']
    
    print("=" * 80)
    print("PARSING RESULTS")
    print("=" * 80)
    print(f"Total units:      {stats['total_units']}")
    print(f"Articles:         {stats['total_articles']}")
    print(f"Paragraphs:       {stats['total_paragraphs']}")
    print(f"Points:           {stats['total_points']}")
    print()
    
    # Show first 3 articles
    print("First 3 articles:")
    print("-" * 80)
    for i, unit in enumerate(legal_units[:3], 1):
        print(f"\n[Article {unit['number']}]")
        if unit['heading']:
            print(f"Heading: {unit['heading']}")
        content = unit['content_text']
        if len(content) > 100:
            content = content[:100] + "..."
        print(f"Content: {content}")
    
    print()
    print("-" * 80)
    
    # Check for issues
    print("\n[VALIDATION]")
    
    # Check for empty content
    empty_content = [u for u in legal_units if not u['content_text'].strip()]
    if empty_content:
        print(f"[WARNING] {len(empty_content)} articles have empty content")
    else:
        print("[OK] All articles have content")
    
    # Check for metadata in content
    metadata_in_content = [
        u for u in legal_units 
        if 'Misljenja' in u['content_text'] or 'Mišljenja' in u['content_text']
    ]
    if metadata_in_content:
        print(f"[WARNING] {len(metadata_in_content)} articles contain metadata lines")
        print(f"Example: Article {metadata_in_content[0]['number']}")
    else:
        print("[OK] No metadata lines in content")
    
    # Check headings
    with_headings = [u for u in legal_units if u['heading']]
    print(f"[INFO] {len(with_headings)} articles have headings")
    
    # Save full output
    print(f"\n[SAVING] Writing parsed output to {OUTPUT_JSON}...")
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(m4_result, f, ensure_ascii=False, indent=2)
    print("[OK] Saved")
    
    print("\n" + "=" * 80)
    print("PIPELINE TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_pipeline()
    except Exception as e:
        print(f"\n[ERROR] Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
