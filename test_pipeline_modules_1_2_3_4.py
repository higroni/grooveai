"""
Integration test for Modules 1, 2, 3, and 4.
Tests the pipeline: File Reader -> Text Normalizer -> Latinizer -> Legal Parser
"""

import requests
import json
import time
import sys
import io
from shared.config_loader import config

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Module URLs
FILE_READER_URL = "http://localhost:8101"
TEXT_NORMALIZER_URL = "http://localhost:8102"
LATINIZER_URL = "http://localhost:8103"
LEGAL_PARSER_URL = "http://localhost:8104"

# Test PDF file from config
TEST_PDF = config.get_sample_file()

def test_pipeline():
    """Test the complete pipeline from PDF to parsed legal structure."""
    
    print("=" * 80)
    print("TESTING PIPELINE: File Reader -> Text Normalizer -> Latinizer -> Legal Parser")
    print("=" * 80)
    
    # Step 1: Read PDF file
    print("\n[STEP 1] Reading PDF file...")
    print(f"File: {TEST_PDF}")
    
    response1 = requests.post(
        f"{FILE_READER_URL}/api/read",
        json={"file_path": TEST_PDF}
    )
    
    if response1.status_code not in [200, 201]:
        print(f"ERROR: File Reader failed with status {response1.status_code}")
        return
    
    data1 = response1.json()
    
    # File Reader returns data in 'output' key
    job1_id = data1["job_id"]
    raw_text = data1["output"]["text"]
    
    print(f"[OK] Job ID: {job1_id}")
    print(f"[OK] Extracted {len(raw_text)} characters")
    print(f"[OK] Processing time: {data1['metadata']['processing_time_ms']}ms")
    
    # Step 2: Normalize text
    print("\n[STEP 2] Normalizing text...")
    
    response2 = requests.post(
        f"{TEXT_NORMALIZER_URL}/api/normalize",
        json={"text": raw_text}
    )
    
    if response2.status_code not in [200, 201]:
        print(f"ERROR: Text Normalizer failed with status {response2.status_code}")
        return
    
    data2 = response2.json()
    job2_id = data2["job_id"]
    normalized_text = data2["output"]["normalized_text"]
    
    print(f"[OK] Job ID: {job2_id}")
    print(f"[OK] Normalized {len(normalized_text)} characters")
    print(f"[OK] Processing time: {data2['metadata']['processing_time_ms']}ms")
    print(f"[OK] Changes: {data2['output']['changes_made']}")
    
    # Step 3: Latinize text
    print("\n[STEP 3] Latinizing text (Cyrillic -> Latin)...")
    
    response3 = requests.post(
        f"{LATINIZER_URL}/api/latinize",
        json={"text": normalized_text}
    )
    
    if response3.status_code not in [200, 201]:
        print(f"ERROR: Latinizer failed with status {response3.status_code}")
        return
    
    data3 = response3.json()
    job3_id = data3["job_id"]
    latinized_text = data3["latinized_text"]
    
    print(f"[OK] Job ID: {job3_id}")
    print(f"[OK] Latinized {len(latinized_text)} characters")
    print(f"[OK] Cyrillic chars converted: {data3['cyrillic_chars_converted']}")
    print(f"[OK] Processing time: {data3['processing_time_ms']}ms")
    
    # Step 4: Parse legal structure
    print("\n[STEP 4] Parsing legal structure...")
    
    response4 = requests.post(
        f"{LEGAL_PARSER_URL}/api/parse",
        json={
            "text": latinized_text,
            "source_uri": f"file:///{TEST_PDF}",
            "filename": TEST_PDF.split("/")[-1]
        }
    )
    
    if response4.status_code not in [200, 201]:
        print(f"ERROR: Legal Parser failed with status {response4.status_code}")
        print(f"Response: {response4.text}")
        return
    
    data4 = response4.json()
    
    job4_id = data4["job_id"]
    output = data4["output"]  # ParseOutput contains document, legal_units, statistics
    
    print(f"[OK] Job ID: {job4_id}")
    print(f"[OK] Status: {data4['status']}")
    print(f"[OK] Document: {output['document']['filename']}")
    print(f"[OK] Title: {output['document']['title']}")
    print(f"[OK] Type: {output['document']['document_type']}")
    print(f"[OK] Total units: {output['statistics']['total_units']}")
    print(f"[OK] Articles: {output['statistics']['total_articles']}")
    print(f"[OK] Paragraphs: {output['statistics']['total_paragraphs']}")
    print(f"[OK] Points: {output['statistics']['total_points']}")
    print(f"[OK] Processing time: {data4['metadata']['processing_time_ms']}ms")
    
    # Display first few legal units
    print("\n[PREVIEW] First 5 legal units:")
    for i, unit in enumerate(output['legal_units'][:5], 1):
        print(f"\n  {i}. [{unit['unit_type'].upper()}] {unit.get('number', '')}")
        if unit.get('heading'):
            print(f"     Heading: {unit['heading']}")
        if unit.get('content_text'):
            content = unit['content_text'][:80] + "..." if len(unit['content_text']) > 80 else unit['content_text']
            print(f"     Content: {content}")
        print(f"     Path: {unit['path']}")
        print(f"     Akoma eId: {unit['akoma_eid']}")
    
    # Save latinized text
    output_file_txt = "pipeline_output_latinized.txt"
    print(f"\n[SAVING] Writing latinized text to {output_file_txt}...")
    
    with open(output_file_txt, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PIPELINE OUTPUT: Modules 1 -> 2 -> 3\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Source PDF: {TEST_PDF}\n")
        f.write(f"Module 1 Job ID: {job1_id}\n")
        f.write(f"Module 2 Job ID: {job2_id}\n")
        f.write(f"Module 3 Job ID: {job3_id}\n\n")
        f.write(f"Original length: {len(raw_text)} chars\n")
        f.write(f"Normalized length: {len(normalized_text)} chars\n")
        f.write(f"Latinized length: {len(latinized_text)} chars\n")
        f.write(f"Cyrillic chars converted: {data3['cyrillic_chars_converted']}\n\n")
        f.write("=" * 80 + "\n")
        f.write("LATINIZED TEXT:\n")
        f.write("=" * 80 + "\n\n")
        f.write(latinized_text)
    
    print(f"[OK] Saved to {output_file_txt}")
    
    # Save parsed structure as JSON
    output_file_json = "pipeline_output_parsed.json"
    print(f"[SAVING] Writing parsed structure to {output_file_json}...")
    
    with open(output_file_json, "w", encoding="utf-8") as f:
        # Save the complete response including module, status, job_id, output, metadata
        json.dump(data4, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved to {output_file_json}")
    
    # Save sample units as text
    output_file_sample = "pipeline_output_sample_units.txt"
    print(f"[SAVING] Writing sample units to {output_file_sample}...")
    
    with open(output_file_sample, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PARSED LEGAL UNITS - SAMPLE (First 20 units)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Document: {output['document']['filename']}\n")
        f.write(f"Total Articles: {output['statistics']['total_articles']}\n")
        f.write(f"Total Units: {output['statistics']['total_units']}\n\n")
        f.write("=" * 80 + "\n\n")
        
        for i, unit in enumerate(output['legal_units'][:20], 1):
            f.write(f"Unit {i}: {unit['unit_type'].upper()}\n")
            f.write(f"Number: {unit.get('number', 'N/A')}\n")
            if unit.get('heading'):
                f.write(f"Heading: {unit['heading']}\n")
            f.write(f"Path: {unit['path']}\n")
            f.write(f"Akoma eId: {unit['akoma_eid']}\n")
            f.write(f"UUID: {unit['legal_unit_id']}\n")
            if unit.get('content_text'):
                f.write(f"Content: {unit['content_text'][:200]}...\n")
            f.write("\n" + "-" * 80 + "\n\n")
    
    print(f"[OK] Saved to {output_file_sample}")
    
    # Summary
    print("\n" + "=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)
    print(f"Module 1 (File Reader):     {len(raw_text):>10} chars")
    print(f"Module 2 (Text Normalizer): {len(normalized_text):>10} chars")
    print(f"Module 3 (Latinizer):       {len(latinized_text):>10} chars")
    print(f"Module 4 (Legal Parser):    {output['statistics']['total_units']:>10} units")
    print(f"  - Articles:               {output['statistics']['total_articles']:>10}")
    print(f"  - Paragraphs:             {output['statistics']['total_paragraphs']:>10}")
    print(f"  - Points:                 {output['statistics']['total_points']:>10}")
    print(f"Cyrillic converted:         {data3['cyrillic_chars_converted']:>10} chars")
    print("=" * 80)
    print(f"\nOutput files:")
    print(f"  - {output_file_txt} (latinized text)")
    print(f"  - {output_file_json} (parsed structure JSON)")
    print(f"  - {output_file_sample} (sample units text)")
    print("\nPipeline test completed successfully!")

if __name__ == "__main__":
    try:
        test_pipeline()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
