"""
Integration test for Modules 1, 2, and 3.
Tests the pipeline: File Reader -> Text Normalizer -> Latinizer
"""

import requests
import json
import time
from shared.config_loader import config

# Module URLs
FILE_READER_URL = "http://localhost:8101"
TEXT_NORMALIZER_URL = "http://localhost:8102"
LATINIZER_URL = "http://localhost:8103"

# Test PDF file from config
TEST_PDF = config.get_sample_file()

def test_pipeline():
    """Test the complete pipeline from PDF to latinized text."""
    
    print("=" * 80)
    print("TESTING PIPELINE: File Reader -> Text Normalizer -> Latinizer")
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
    
    # Debug: print output structure
    print(f"[DEBUG] Output keys: {list(data1['output'].keys())}")
    
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
    
    # Save results to file
    output_file = "pipeline_output_latinized.txt"
    print(f"\n[SAVING] Writing latinized text to {output_file}...")
    
    with open(output_file, "w", encoding="utf-8") as f:
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
    
    print(f"[OK] Saved to {output_file}")
    
    # Summary
    print("\n" + "=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)
    print(f"Module 1 (File Reader):     {len(raw_text):>10} chars")
    print(f"Module 2 (Text Normalizer): {len(normalized_text):>10} chars")
    print(f"Module 3 (Latinizer):       {len(latinized_text):>10} chars")
    print(f"Cyrillic converted:         {data3['cyrillic_chars_converted']:>10} chars")
    print("=" * 80)
    print(f"\nOutput saved to: {output_file}")
    print("Pipeline test completed successfully!")

if __name__ == "__main__":
    try:
        test_pipeline()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
